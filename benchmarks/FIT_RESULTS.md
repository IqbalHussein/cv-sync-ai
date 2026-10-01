# Resume/JD Fit Benchmark

Dataset: [cnamuangtoun/resume-job-description-fit](https://huggingface.co/datasets/cnamuangtoun/resume-job-description-fit) — 6241 train / 1759 test pairs; job descriptions are disjoint across splits. Model and blend weight selected on train only (models within 0.005 train NDCG of the best count as tied; the fastest is selected); test has {results['Random']['n_jds']} job descriptions, each ranking its labeled candidates.

## Embedding models

| Model | Encode speed (chunks/s, CPU) | Tuned w | Train NDCG@10 | Test NDCG@10, semantic only | Test NDCG@10, hybrid | Test ROC-AUC, hybrid |
|---|---|---|---|---|---|---|
| all-MiniLM-L6-v2 **(selected)** | 47 | 0.0 | 0.761 | 0.738 | 0.738 | 0.616 |
| all-MiniLM-L12-v2 | 46 | 0.0 | 0.756 | 0.714 | 0.714 | 0.601 |
| BAAI/bge-small-en-v1.5 | 16 | 0.0 | 0.754 | 0.721 | 0.721 | 0.603 |
| all-mpnet-base-v2 | 5 | 0.0 | 0.761 | 0.729 | 0.729 | 0.601 |
| BAAI/bge-base-en-v1.5 | 6 | 0.0 | 0.755 | 0.725 | 0.725 | 0.598 |

## Test results

| Scorer | NDCG@10 | ROC-AUC (fit vs. no fit) |
|---|---|---|
| Random | 0.578 | 0.483 |
| TF-IDF cosine | 0.702 | 0.590 |
| Weighted skills only | 0.492 | 0.549 |
| Hybrid, all-MiniLM-L6-v2, w=0.1 (shipped config) | 0.744 | 0.606 |
| Hybrid, all-MiniLM-L6-v2, w=0.0 (selected on train) | 0.738 | 0.616 |

## By job domain (selected configuration)

Domain = the skill domain contributing the most skills extracted from the job description.

| Domain | Test JDs | Skills-only NDCG@10 | Hybrid NDCG@10 |
|---|---|---|---|
| Accounting & Finance | 12 | 0.599 | 0.932 |
| Business & Analytics | 7 | 0.543 | 0.786 |
| Project & Operations Management | 6 | 0.393 | 0.592 |
| Software & Data | 27 | 0.560 | 0.678 |
| Unrecognized | 6 | 0.148 | 0.702 |

## Train sweep for all-MiniLM-L6-v2 (NDCG@10 vs. SKILL_SCORE_WEIGHT)

| w | Train NDCG |
|---|---|
| 0.0 | 0.761 |
| 0.05 | 0.752 |
| 0.1 | 0.743 |
| 0.15 | 0.739 |
| 0.2 | 0.739 |
| 0.25 | 0.739 |
| 0.3 | 0.735 |
| 0.35 | 0.734 |
| 0.4 | 0.733 |
| 0.45 | 0.732 |
| 0.5 | 0.732 |
| 0.55 | 0.731 |
| 0.6 | 0.731 |
| 0.65 | 0.732 |
| 0.7 | 0.732 |
| 0.75 | 0.730 |
| 0.8 | 0.730 |
| 0.85 | 0.730 |
| 0.9 | 0.730 |
| 0.95 | 0.730 |
| 1.0 | 0.564 |
