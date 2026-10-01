# CVSyncAI Benchmark Results

_Generated 2026-10-01 by `python -m benchmarks.run_benchmark`._

## Skill extraction

72 hand-labeled documents (30 software postings, 12 non-software postings, 30 adversarial sentences), 273 gold skill mentions, 252-skill vocabulary.

| Extractor | Precision | Recall | F1 | FP | FN |
|---|---|---|---|---|---|
| spaCy EntityRuler (CVSyncAI) | 99.3% | 98.2% | 98.7% | 2 | 5 |
| Naive substring baseline | 69.6% | 98.2% | 81.5% | 117 | 5 |

## Job ranking

6 resumes ranked against 30 postings across 6 role families. Same family = relevant (2), adjacent family = partially relevant (1). Averaged over resumes.

| Ranker | NDCG@5 | MRR | Precision@5 | Top-1 accuracy |
|---|---|---|---|---|
| Skill Jaccard (keyword baseline) | 0.823 | 0.917 | 70.0% | 83.3% |
| TF-IDF cosine (text baseline) | 0.923 | 1.000 | 86.7% | 100.0% |
| Weighted skills only | 0.781 | 0.722 | 70.0% | 50.0% |
| Semantic embeddings only | 0.942 | 1.000 | 90.0% | 100.0% |
| Hybrid (CVSyncAI production) | 0.942 | 1.000 | 90.0% | 100.0% |

## Throughput

Hybrid ranking of 30 postings for one resume (model warm, CPU): **506 ms** average (59 postings/sec).

## Extraction errors (CVSyncAI)

| Document | False positives | Missed |
|---|---|---|
| Full Stack Developer | Tutoring | - |
| Compiler Engineer | - | Code Review, Testing |
| Staff Accountant | - | Auditing |
| Financial Analyst | - | Financial Modeling |
| Report to the C-suite on quarterly budgets. | C | - |
| Dockerized the app and wrote a docker compose file. | - | Docker |
