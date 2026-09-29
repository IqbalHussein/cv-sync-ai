import pytest
import torch

from src.config.weights import SKILL_SCORE_WEIGHT, SKILL_WEIGHTS
from src.matching import matcher


class FakeSemanticMatcher:
    """Stands in for the sentence-transformer so tests don't load a model."""

    def encode_many(self, texts, batch_size=32):
        return [torch.zeros(3) for _ in texts]

    def compute_similarity_score(self, a, b):
        return 0.5


JOBS = [
    {"id": 1, "title": "Backend", "company": "X", "skills": ["Python", "Docker"], "text": "Python\nDocker"},
    {"id": 2, "title": "Python Dev", "company": "Y", "skills": ["Python"], "text": "Python"},
]


def test_weighted_skill_score_without_semantic():
    results = matcher.match_resume_to_jobs(JOBS, ["Python"])
    by_id = {r["job_id"]: r for r in results}

    expected = SKILL_WEIGHTS["Python"] / (SKILL_WEIGHTS["Python"] + SKILL_WEIGHTS["Docker"])
    assert by_id[1]["score"] == pytest.approx(expected, abs=1e-3)
    assert by_id[1]["missing_skills"] == ["Docker"]
    assert by_id[1]["final_score"] == by_id[1]["score"]
    assert [r["job_id"] for r in results] == [2, 1]


def test_final_score_blends_semantic(monkeypatch):
    monkeypatch.setattr(matcher, "get_semantic_matcher", lambda: FakeSemanticMatcher())
    resume_data = {"text": "Python", "sections": {"experience": "Python work"}}
    progress = []

    results = matcher.match_resume_to_jobs(
        JOBS, ["Python"], resume_data=resume_data, progress_callback=progress.append
    )

    for r in results:
        assert r["semantic_score"] == pytest.approx(0.5)
        assert r["final_score"] == pytest.approx(
            SKILL_SCORE_WEIGHT * r["score"] + (1 - SKILL_SCORE_WEIGHT) * 0.5, abs=1e-3
        )
    assert progress == sorted(progress)
    assert progress[-1] == pytest.approx(1.0)
