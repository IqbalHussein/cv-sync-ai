"""
Benchmark CVSyncAI's skill extraction and job ranking against hand-labeled data.

Usage:
    python -m benchmarks.run_benchmark            # full run, writes benchmarks/RESULTS.md
    python -m benchmarks.run_benchmark --no-semantic   # skip the embedding model

Reports:
1. Skill extraction precision / recall / F1 (micro-averaged) for the spaCy
   EntityRuler extractor vs. a naive case-insensitive substring baseline.
2. Ranking quality (NDCG@5, MRR, Precision@5) of each resume against all
   postings, for the production hybrid scorer and several baselines.
3. Throughput: time to rank all postings for one resume.
"""
import argparse
import math
import os
import tempfile
import time
from datetime import date

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from benchmarks.dataset import EXTRACTION_CASES, JOBS, NON_TECH_POSTINGS, RESUMES, relevance
from src.config.skills import ALIASES, ALL_SKILLS, PROPER_NOUN_SKILLS, STRICT_SKILLS
from src.matching.matcher import match_resume_to_jobs
from src.matching.semantic import get_semantic_matcher
from src.parsing.resume_parser import parse_resume_from_file
from src.parsing.skills_extraction import extract_skills

K = 5
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "RESULTS.md")


# ---------------------------------------------------------------- extraction

def naive_extract(text: str) -> list[str]:
    """Baseline: case-insensitive substring search over every skill name and alias."""
    lower = text.lower()
    terms = {s.lower(): s for s in ALL_SKILLS}
    terms.update(ALIASES)
    terms.update(STRICT_SKILLS)
    terms.update({k.lower(): v for k, v in PROPER_NOUN_SKILLS.items()})
    return sorted({canonical for term, canonical in terms.items() if term in lower})


def prf(pairs: list[tuple[set, set]]) -> dict:
    """Micro-averaged precision/recall/F1 over (predicted, gold) set pairs."""
    tp = sum(len(p & g) for p, g in pairs)
    fp = sum(len(p - g) for p, g in pairs)
    fn = sum(len(g - p) for p, g in pairs)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def extraction_samples() -> list[tuple[str, set]]:
    samples = [(job["text"], set(job["gold_skills"])) for job in JOBS]
    samples += [(job["text"], set(job["gold"])) for job in NON_TECH_POSTINGS]
    samples += [(case["text"], set(case["gold"])) for case in EXTRACTION_CASES]
    return samples


def run_extraction() -> dict:
    samples = extraction_samples()
    out = {}
    errors = []
    for name, fn in [("spaCy EntityRuler (CVSyncAI)", lambda t: extract_skills(t, ALL_SKILLS)),
                     ("Naive substring baseline", naive_extract)]:
        pairs = []
        for text, gold in samples:
            pred = set(fn(text))
            pairs.append((pred, gold))
            if name.startswith("spaCy") and pred != gold:
                errors.append((text.splitlines()[0][:60], sorted(pred - gold), sorted(gold - pred)))
        out[name] = prf(pairs)
    out["_n_docs"] = len(samples)
    out["_n_skills"] = sum(len(g) for _, g in samples)
    out["_errors"] = errors
    return out


# ------------------------------------------------------------------ ranking

def ndcg_at_k(rels: list[int], ideal: list[int], k: int) -> float:
    def dcg(rs):
        return sum((2 ** r - 1) / math.log2(i + 2) for i, r in enumerate(rs[:k]))
    best = dcg(sorted(ideal, reverse=True))
    return dcg(rels) / best if best else 0.0


def rank_metrics(ranked_ids: list[str], resume_family: str) -> dict:
    family = {j["id"]: j["family"] for j in JOBS}
    rels = [relevance(resume_family, family[jid]) for jid in ranked_ids]
    first_hit = next((i for i, r in enumerate(rels) if r == 2), None)
    return {
        "ndcg": ndcg_at_k(rels, rels, K),
        "mrr": 1.0 / (first_hit + 1) if first_hit is not None else 0.0,
        "p_at_k": sum(1 for r in rels[:K] if r == 2) / K,
        "top1": 1.0 if rels[0] == 2 else 0.0,
    }


def build_jobs() -> list[dict]:
    """Structure postings the same way job_parser does."""
    return [
        {"id": j["id"], "title": j["title"], "company": j["company"],
         "text": j["text"], "skills": extract_skills(j["text"], ALL_SKILLS)}
        for j in JOBS
    ]


def parse_resume_text(text: str) -> dict:
    """Run a resume string through the production file parser."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(text)
        path = f.name
    try:
        return parse_resume_from_file(path)
    finally:
        os.remove(path)


def tfidf_ranking(resume_text: str, jobs: list[dict]) -> list[str]:
    vec = TfidfVectorizer(stop_words="english")
    matrix = vec.fit_transform([resume_text] + [j["text"] for j in jobs])
    sims = cosine_similarity(matrix[0:1], matrix[1:])[0]
    return [jobs[i]["id"] for i in sorted(range(len(jobs)), key=lambda i: -sims[i])]


def jaccard_ranking(resume_skills: list[str], jobs: list[dict]) -> list[str]:
    rs = set(resume_skills)
    def jac(j):
        js = set(j["skills"])
        return len(rs & js) / len(rs | js) if rs | js else 0.0
    return [j["id"] for j in sorted(jobs, key=jac, reverse=True)]


def run_ranking(use_semantic: bool) -> dict:
    jobs = build_jobs()
    systems: dict[str, list[dict]] = {}
    timings = []
    if use_semantic:
        get_semantic_matcher()  # load the model up front so timings exclude it

    def record(name, ranked, family):
        systems.setdefault(name, []).append(rank_metrics(ranked, family))

    for r in RESUMES:
        resume = parse_resume_text(r["text"])
        skills = resume["skills_all"]

        record("Skill Jaccard (keyword baseline)", jaccard_ranking(skills, jobs), r["family"])
        record("TF-IDF cosine (text baseline)", tfidf_ranking(resume["text"], jobs), r["family"])

        weighted = match_resume_to_jobs(jobs, skills)
        record("Weighted skills only", [x["job_id"] for x in weighted], r["family"])

        if use_semantic:
            start = time.perf_counter()
            hybrid = match_resume_to_jobs(jobs, skills, resume_data=resume)
            timings.append(time.perf_counter() - start)
            by_sem = sorted(hybrid, key=lambda x: x["semantic_score"], reverse=True)
            record("Semantic embeddings only", [x["job_id"] for x in by_sem], r["family"])
            record("Hybrid (CVSyncAI production)", [x["job_id"] for x in hybrid], r["family"])

    averaged = {
        name: {m: sum(row[m] for row in rows) / len(rows) for m in rows[0]}
        for name, rows in systems.items()
    }
    return {"systems": averaged, "timings": timings}


# ------------------------------------------------------------------ report

def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def render(extraction: dict, ranking: dict) -> str:
    lines = [f"# CVSyncAI Benchmark Results", "",
             f"_Generated {date.today().isoformat()} by `python -m benchmarks.run_benchmark`._", "",
             "## Skill extraction", "",
             f"{extraction['_n_docs']} hand-labeled documents ({len(JOBS)} software postings, "
             f"{len(NON_TECH_POSTINGS)} non-software postings, {len(EXTRACTION_CASES)} adversarial sentences), "
             f"{extraction['_n_skills']} gold skill mentions, {len(ALL_SKILLS)}-skill vocabulary.", "",
             "| Extractor | Precision | Recall | F1 | FP | FN |", "|---|---|---|---|---|---|"]
    for name, m in extraction.items():
        if name.startswith("_"):
            continue
        lines.append(f"| {name} | {pct(m['precision'])} | {pct(m['recall'])} | {pct(m['f1'])} | {m['fp']} | {m['fn']} |")

    lines += ["", "## Job ranking", "",
              f"{len(RESUMES)} resumes ranked against {len(JOBS)} postings across 6 role families. "
              "Same family = relevant (2), adjacent family = partially relevant (1). Averaged over resumes.", "",
              f"| Ranker | NDCG@{K} | MRR | Precision@{K} | Top-1 accuracy |", "|---|---|---|---|---|"]
    for name, m in ranking["systems"].items():
        lines.append(f"| {name} | {m['ndcg']:.3f} | {m['mrr']:.3f} | {pct(m['p_at_k'])} | {pct(m['top1'])} |")

    if ranking["timings"]:
        avg = sum(ranking["timings"]) / len(ranking["timings"])
        lines += ["", "## Throughput", "",
                  f"Hybrid ranking of {len(JOBS)} postings for one resume (model warm, CPU): "
                  f"**{avg * 1000:.0f} ms** average ({len(JOBS) / avg:.0f} postings/sec)."]

    if extraction["_errors"]:
        lines += ["", "## Extraction errors (CVSyncAI)", "", "| Document | False positives | Missed |", "|---|---|---|"]
        for doc, fp, fn in extraction["_errors"]:
            lines.append(f"| {doc.replace('|', '/')} | {', '.join(fp) or '-'} | {', '.join(fn) or '-'} |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--no-semantic", action="store_true", help="Skip embedding-based rankers")
    args = parser.parse_args(argv)

    extraction = run_extraction()
    ranking = run_ranking(use_semantic=not args.no_semantic)
    report = render(extraction, ranking)
    print(report)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Wrote {RESULTS_PATH}")


if __name__ == "__main__":
    main()
