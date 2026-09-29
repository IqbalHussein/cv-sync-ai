# Description

**CVSyncAI** is a project designed to pull the technical skills from a job posting and compare them against resumes to show highlights and weak points.

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

Jobs are ranked by a match score that blends weighted skill overlap (70%) with semantic similarity (30%); the split is `SKILL_SCORE_WEIGHT` in `src/config/weights.py`.

## Web Interface
Run the Streamlit app for an interactive UI:
```bash
streamlit run streamlit_app.py
```
Upload a resume (`.txt`/`.pdf`) and a job postings file (`.txt`). The app ranks matches, shows matched/missing skills with evidence, suggests learning resources, drafts cover letters (requires `GEMINI_API_KEY`) with PDF export, and warns if any postings were skipped because no title or company could be identified.

# Tests
```bash
pip install -r requirements-dev.txt
pytest
```
