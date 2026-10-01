from benchmarks.dataset import JOBS, RESUMES, relevance
from benchmarks.run_benchmark import ndcg_at_k, run_extraction


def test_extraction_f1_does_not_regress():
    results = run_extraction()
    ours = results["spaCy EntityRuler (CVSyncAI)"]
    baseline = results["Naive substring baseline"]
    assert ours["f1"] >= 0.95
    assert ours["precision"] > baseline["precision"]


def test_every_family_has_a_resume_and_postings():
    families = {r["family"] for r in RESUMES}
    assert families == {j["family"] for j in JOBS}
    assert all(relevance(f, f) == 2 for f in families)


def test_ndcg_perfect_and_reversed():
    rels = [2, 2, 1, 0, 0]
    assert ndcg_at_k(rels, rels, 5) == 1.0
    assert ndcg_at_k(rels[::-1], rels, 5) < ndcg_at_k([2, 1, 2, 0, 0], rels, 5) < 1.0
