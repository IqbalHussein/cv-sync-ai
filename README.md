# Description

**CVSyncAI** pulls the skills from a job posting and compares them against resumes to show highlights and weak points. Its skill vocabulary covers about 250 skills across software, accounting & finance, business analytics, operations, sales & marketing, HR, healthcare, legal, education and design roles (`DOMAIN_SKILLS` in `src/config/skills.py`).

# Setup

```bash
git clone https://github.com/IqbalHussein/cv-sync-ai.git
cd cv-sync-ai
python -m venv venv
source venv/bin/activate
# Windows
# venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # then set GEMINI_API_KEY (needed only for cover letters)
```

`GEMINI_API_KEY` is used for cover-letter generation. Optionally set `GEMINI_MODEL` to override the default model (`gemini-2.5-flash`).

# Usage

## CLI
Match a resume against a file of job postings (postings separated by `====`):
```bash
python main.py
python main.py --jobs data/test_jobs.txt --resume data/resume.txt --out data --top 10
```

| Flag | Default | Description |
| --- | --- | --- |
| `--jobs` | `sample-postings.txt` | Job postings file |
| `--resume` | `data/resume.pdf` if present, else `data/resume.txt` | Resume (`.txt` or `.pdf`) |
| `--out` | `data` | Directory for `structured_jobs.json`, `resume_structured.json`, `match_report.json` |
| `--top` | `5` | Number of matches printed |

Jobs are ranked by a match score that blends weighted skill overlap (10%) with semantic similarity (90%); the split is `SKILL_SCORE_WEIGHT` in `src/config/weights.py`, tuned on the fit benchmark below.

## Web Interface
Run the Streamlit app for an interactive UI:
```bash
streamlit run streamlit_app.py
```
Upload a resume (`.txt`/`.pdf`) and a job postings file (`.txt`). The app ranks matches, shows matched/missing skills with evidence, suggests learning resources, drafts cover letters (requires `GEMINI_API_KEY`) with PDF export, and warns if any postings were skipped because no title or company could be identified.

# Benchmark
`benchmarks/` holds a hand-labeled dataset (6 resumes, 30 job postings across 6 role families, 20 adversarial extraction sentences) and a runner that measures:
- **Skill extraction** precision/recall/F1 vs. a naive substring-matching baseline
- **Ranking quality** (NDCG@5, MRR, Precision@5) for the hybrid scorer vs. keyword, TF-IDF and embedding-only baselines
- **Throughput** of the hybrid ranker

```bash
python -m benchmarks.run_benchmark          # writes benchmarks/RESULTS.md
python -m benchmarks.run_benchmark --no-semantic   # skip the embedding model
```

`benchmarks/fit_benchmark.py` evaluates the scorer on the public [resume-job-description-fit](https://huggingface.co/datasets/cnamuangtoun/resume-job-description-fit) dataset (8,000 labeled resume/JD pairs). It tunes `SKILL_SCORE_WEIGHT` on the train split and reports per-job NDCG@10 and ROC-AUC on the held-out test split. The data downloads to `data/external/` on first run. Scoring takes a while on CPU; the scores are cached, so later runs take seconds.
```bash
python -m benchmarks.fit_benchmark          # writes benchmarks/FIT_RESULTS.md
```

# Tests
```bash
pip install -r requirements-dev.txt
pytest
```
