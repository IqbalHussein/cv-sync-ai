import os

import pytest

import main
from src.generation import cover_letter
from src.reporting import build_match_report


def test_build_match_report_ranks_results():
    results = [
        {"title": "A", "company": "X", "final_score": 0.9, "score": 0.8, "semantic_score": 0.4,
         "matched_skills": ["Python"], "missing_skills": []},
        {"title": "B", "company": "Y", "score": 0.5, "matched_skills": [], "missing_skills": ["Go"]},
    ]
    report = build_match_report(results, ["Python"])
    assert report["generated_at"].endswith("Z")
    assert report["resume"]["skills_used"] == ["Python"]
    assert [r["rank"] for r in report["results"]] == [1, 2]
    assert report["results"][1]["final_score"] == 0.5


def test_cli_default_paths_exist():
    args = main.parse_args([])
    assert os.path.exists(args.jobs)


def test_cover_letter_failure_raises(monkeypatch):
    def boom():
        raise RuntimeError("GEMINI_API_KEY is not set in the environment.")
    monkeypatch.setattr(cover_letter, "get_gemini_client", boom)
    with pytest.raises(cover_letter.CoverLetterError, match="GEMINI_API_KEY"):
        cover_letter.generate_cover_letter({"sections": {}}, {"title": "Dev"})


def test_cover_letter_prompt_includes_experience(monkeypatch):
    captured = {}

    class FakeModels:
        def generate_content(self, model, contents):
            captured["prompt"] = contents
            return type("Resp", (), {"text": " Dear Hiring Manager, ... "})()

    fake_client = type("Client", (), {"models": FakeModels()})()
    monkeypatch.setattr(cover_letter, "get_gemini_client", lambda: fake_client)

    resume = {"sections": {"experience": "Built Kafka pipelines at Acme"}, "skills_all": ["Python"]}
    letter = cover_letter.generate_cover_letter(resume, {"title": "Dev", "company": "Co", "matched_skills": []})
    assert letter == "Dear Hiring Manager, ..."
    assert "Built Kafka pipelines at Acme" in captured["prompt"]
