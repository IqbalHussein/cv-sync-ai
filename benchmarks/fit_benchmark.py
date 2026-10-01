"""
Tune and evaluate CVSyncAI's scoring on the public resume/job-description fit dataset.

Dataset: cnamuangtoun/resume-job-description-fit on Hugging Face
(8,000 resume/JD pairs labeled "No Fit" / "Potential Fit" / "Good Fit",
pre-split into train and test with disjoint job descriptions).

Protocol:
1. Skill score for every pair from the production matcher (model independent).
2. Semantic score for every pair under each candidate embedding model, using
   the production semantic scoring (same texts, same component weights).
3. On the train split only: pick the blend weight (SKILL_SCORE_WEIGHT) per
   model, then pick the model with the best tuned train NDCG.
4. Report on the held-out test split: for each job description, rank its
   labeled candidate resumes and compute NDCG@10 (Good=2, Potential=1, No=0),
   plus ROC-AUC for separating any-fit from no-fit.

Usage:
    python -m benchmarks.fit_benchmark
    python -m benchmarks.fit_benchmark --models all-MiniLM-L6-v2 BAAI/bge-small-en-v1.5
Scores are cached per model in data/external/, so reruns only redo the evaluation.
"""
import argparse
import os
import time
import urllib.request
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import roc_auc_score

from benchmarks.run_benchmark import ndcg_at_k, parse_resume_text
from src.config.skills import ALL_SKILLS, SKILL_DOMAIN
from src.config.weights import SKILL_SCORE_WEIGHT
from src.matching.matcher import (
    job_semantic_texts,
    match_resume_to_jobs,
    resume_semantic_texts,
    semantic_score_from_embeddings,
)
from src.matching.semantic import DEFAULT_MODEL, get_semantic_matcher
from src.parsing.skills_extraction import extract_skills

DATA_DIR = os.path.join("data", "external")
BASE_URL = "https://huggingface.co/datasets/cnamuangtoun/resume-job-description-fit/resolve/main"
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "FIT_RESULTS.md")
LABEL_GRADE = {"No Fit": 0, "Potential Fit": 1, "Good Fit": 2}
K = 10
WEIGHT_GRID = [round(w, 2) for w in np.arange(0.0, 1.01, 0.05)]
# Models whose tuned train NDCG is within this of the best count as tied; the
# fastest of them is selected, since the app embeds on CPU.
TIE_TOLERANCE = 0.005
MODELS = [
    "all-MiniLM-L6-v2",
    "all-MiniLM-L12-v2",
    "BAAI/bge-small-en-v1.5",
    "all-mpnet-base-v2",
    "BAAI/bge-base-en-v1.5",
]


def load_split(split: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, f"fit_{split}.csv")
    if not os.path.exists(path):
        os.makedirs(DATA_DIR, exist_ok=True)
        print(f"Downloading {split} split...")
        urllib.request.urlretrieve(f"{BASE_URL}/{split}.csv", path)
    df = pd.read_csv(path)
    df["grade"] = df["label"].map(LABEL_GRADE)
    return df


class Corpus:
    """Parsed resumes and structured JDs for every unique text in both splits."""

    def __init__(self, frames: list[pd.DataFrame]):
        both = pd.concat(frames)
        resume_texts = both["resume_text"].unique()
        jd_texts = both["job_description_text"].unique()
        print(f"Parsing {len(resume_texts)} resumes and {len(jd_texts)} job descriptions...")
        self.resumes = {t: parse_resume_text(t) for t in resume_texts}
        self.jobs = {t: {"id": i, "title": "", "company": "", "text": t,
                         "skills": extract_skills(t, ALL_SKILLS)}
                     for i, t in enumerate(jd_texts)}


def skill_scores(df: pd.DataFrame, split: str, corpus: Corpus) -> np.ndarray:
    """Production skill score (weighted overlap + context check) for each pair."""
    cache_path = os.path.join(DATA_DIR, f"fit_{split}_skill.csv")
    if os.path.exists(cache_path):
        return pd.read_csv(cache_path)["skill_score"].to_numpy()

    out = np.zeros(len(df))
    for resume_text, idx in df.groupby("resume_text").indices.items():
        resume = corpus.resumes[resume_text]
        jobs = [dict(corpus.jobs[df["job_description_text"].iat[i]], id=int(i)) for i in idx]
        for r in match_resume_to_jobs(jobs, resume["skills_all"], resume_data=resume, semantic=False):
            out[r["job_id"]] = r["score"]
    pd.DataFrame({"skill_score": out}).to_csv(cache_path, index=False)
    return out


def semantic_scores(frames: dict[str, pd.DataFrame], corpus: Corpus, model: str) -> tuple[dict, float]:
    """Production semantic score per pair under `model`; returns scores per split and chunks/sec."""
    slug = model.replace("/", "__")
    paths = {split: os.path.join(DATA_DIR, f"fit_{split}_semantic_{slug}.csv") for split in frames}
    timing_path = os.path.join(DATA_DIR, f"fit_timing_{slug}.txt")
    if all(os.path.exists(p) for p in paths.values()) and os.path.exists(timing_path):
        with open(timing_path) as f:
            speed = float(f.read())
        return {s: pd.read_csv(p)["semantic_score"].to_numpy() for s, p in paths.items()}, speed

    matcher = get_semantic_matcher(model)
    resume_parts = {t: resume_semantic_texts(r, r["skills_all"]) for t, r in corpus.resumes.items()}
    job_parts = {t: job_semantic_texts(j) for t, j in corpus.jobs.items()}
    texts = list(dict.fromkeys(
        [p for parts in resume_parts.values() for p in parts] + [p for parts in job_parts.values() for p in parts]
    ))
    n_chunks = sum(max(1, -(-len(t.split()) // 150)) for t in texts)
    print(f"[{model}] embedding {len(texts)} unique texts (~{n_chunks} chunks)...")
    start = time.perf_counter()
    embs = dict(zip(texts, matcher.encode_many(texts)))
    speed = n_chunks / (time.perf_counter() - start)

    out = {}
    for split, df in frames.items():
        scores = np.zeros(len(df))
        for i, (r_text, j_text) in enumerate(zip(df["resume_text"], df["job_description_text"])):
            res_embs = [embs[p] for p in resume_parts[r_text]]
            job_full, job_skills = (embs[p] for p in job_parts[j_text])
            scores[i] = semantic_score_from_embeddings(matcher, res_embs, job_full, job_skills)
        pd.DataFrame({"semantic_score": scores}).to_csv(paths[split], index=False)
        out[split] = scores
    with open(timing_path, "w") as f:
        f.write(str(speed))
    return out, speed


def tfidf_scores(df: pd.DataFrame) -> np.ndarray:
    vec = TfidfVectorizer(stop_words="english", max_features=50000)
    vec.fit(pd.concat([df["resume_text"], df["job_description_text"]]).unique())
    r = vec.transform(df["resume_text"])
    j = vec.transform(df["job_description_text"])
    return np.asarray(r.multiply(j).sum(axis=1)).ravel()  # rows are L2-normalized → cosine


def evaluate(df: pd.DataFrame, scores: np.ndarray, mask=None) -> dict:
    """Mean per-JD NDCG@K over JDs with at least one fit, plus pairwise ROC-AUC."""
    if mask is not None:
        df, scores = df[mask], scores[mask]
    grades = df["grade"].to_numpy()
    ndcgs = []
    for idx in df.groupby("job_description_text").indices.values():
        g = grades[idx]
        if g.max() == 0 or len(idx) < 2:
            continue
        order = np.argsort(-scores[idx], kind="stable")
        ndcgs.append(ndcg_at_k(list(g[order]), list(g), K))
    return {"ndcg": float(np.mean(ndcgs)), "auc": float(roc_auc_score(grades > 0, scores)), "n_jds": len(ndcgs)}


def jd_domain(job: dict) -> str:
    """The domain contributing the most extracted skills, or 'Unrecognized'."""
    counts = Counter(SKILL_DOMAIN[s] for s in job["skills"])
    return counts.most_common(1)[0][0] if counts else "Unrecognized"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Resume/JD fit benchmark")
    parser.add_argument("--models", nargs="+", default=MODELS, help="Embedding models to compare")
    args = parser.parse_args(argv)

    frames = {"train": load_split("train"), "test": load_split("test")}
    corpus = Corpus(list(frames.values()))
    train, test = frames["train"], frames["test"]
    skill = {s: skill_scores(df, s, corpus) for s, df in frames.items()}

    def blend(split, sem, w):
        return w * skill[split] + (1 - w) * sem[split]

    rows = []
    for model in args.models:
        sem, speed = semantic_scores(frames, corpus, model)
        sweep = [(w, evaluate(train, blend("train", sem, w))["ndcg"]) for w in WEIGHT_GRID]
        w_best, train_ndcg = max(sweep, key=lambda x: x[1])
        row = {
            "model": model, "speed": speed, "w": w_best, "train_ndcg": train_ndcg,
            "sem_only": evaluate(test, sem["test"]),
            "tuned": evaluate(test, blend("test", sem, w_best)),
            "sem": sem, "sweep": sweep,
        }
        rows.append(row)
        print(f"[{model}] w={w_best} train NDCG={train_ndcg:.3f} test NDCG={row['tuned']['ndcg']:.3f} "
              f"AUC={row['tuned']['auc']:.3f} ({speed:.0f} chunks/s)")

    top = max(r["train_ndcg"] for r in rows)
    best = max((r for r in rows if r["train_ndcg"] >= top - TIE_TOLERANCE), key=lambda r: r["speed"])
    baseline = next((r for r in rows if r["model"] == DEFAULT_MODEL), rows[0])
    rng = np.random.default_rng(0)
    systems = {
        "Random": rng.random(len(test)),
        "TF-IDF cosine": tfidf_scores(test),
        "Weighted skills only": skill["test"],
        f"Hybrid, {baseline['model']}, w={SKILL_SCORE_WEIGHT} (shipped config)":
            blend("test", baseline["sem"], SKILL_SCORE_WEIGHT),
        f"Hybrid, {best['model']}, w={best['w']} (selected on train)": blend("test", best["sem"], best["w"]),
    }
    results = {name: evaluate(test, s) for name, s in systems.items()}

    domains = test["job_description_text"].map(lambda t: jd_domain(corpus.jobs[t]))
    domain_rows = []
    for domain in sorted(domains.unique()):
        mask = (domains == domain).to_numpy()
        if test[mask]["job_description_text"].nunique() < 3:
            continue
        domain_rows.append((domain, evaluate(test, skill["test"], mask),
                            evaluate(test, systems[list(systems)[-1]], mask)))

    lines = ["# Resume/JD Fit Benchmark", "",
             "Dataset: [cnamuangtoun/resume-job-description-fit]"
             "(https://huggingface.co/datasets/cnamuangtoun/resume-job-description-fit) — "
             f"{len(train)} train / {len(test)} test pairs; job descriptions are disjoint across splits. "
             f"Model and blend weight selected on train only (models within {TIE_TOLERANCE} train NDCG "
             "of the best count as tied; the fastest is selected); test has {results['Random']['n_jds']} job descriptions, "
             "each ranking its labeled candidates.", "",
             "## Embedding models", "",
             f"| Model | Encode speed (chunks/s, CPU) | Tuned w | Train NDCG@{K} | Test NDCG@{K}, semantic only "
             f"| Test NDCG@{K}, hybrid | Test ROC-AUC, hybrid |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        mark = " **(selected)**" if r is best else ""
        lines.append(f"| {r['model']}{mark} | {r['speed']:.0f} | {r['w']} | {r['train_ndcg']:.3f} | "
                     f"{r['sem_only']['ndcg']:.3f} | {r['tuned']['ndcg']:.3f} | {r['tuned']['auc']:.3f} |")

    lines += ["", "## Test results", "", f"| Scorer | NDCG@{K} | ROC-AUC (fit vs. no fit) |", "|---|---|---|"]
    lines += [f"| {name} | {m['ndcg']:.3f} | {m['auc']:.3f} |" for name, m in results.items()]

    lines += ["", "## By job domain (selected configuration)", "",
              "Domain = the skill domain contributing the most skills extracted from the job description.", "",
              f"| Domain | Test JDs | Skills-only NDCG@{K} | Hybrid NDCG@{K} |", "|---|---|---|---|"]
    lines += [f"| {d} | {h['n_jds']} | {s['ndcg']:.3f} | {h['ndcg']:.3f} |" for d, s, h in domain_rows]

    lines += ["", f"## Train sweep for {best['model']} (NDCG@{K} vs. SKILL_SCORE_WEIGHT)", "",
              "| w | Train NDCG |", "|---|---|"]
    lines += [f"| {w} | {n:.3f} |" for w, n in best["sweep"]]
    report = "\n".join(lines) + "\n"
    print(report)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Wrote {RESULTS_PATH}")


if __name__ == "__main__":
    main()
