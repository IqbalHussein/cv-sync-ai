from src.parsing.job_parser import parse_jobs_with_stats, parse_jobs_from_file

POSTINGS = """
Applied ML Engineer
Acme Robotics · Ottawa, ON (Hybrid)
Apply
Save Applied ML Engineer at Acme Robotics
About the job
We need Python and Docker.
====
Software Engineer
AMAZON, Inc.
Toronto, ON
Full-time
Requirements: Java, AWS
====
Profile insights
Here’s how the job qualifications align with your profile
====
Random text with no recognisable heading
just words here
"""


def _parse(tmp_path):
    path = tmp_path / "jobs.txt"
    path.write_text(POSTINGS, encoding="utf-8")
    return parse_jobs_with_stats(str(path))


def test_title_containing_apply_is_kept(tmp_path):
    jobs, _ = _parse(tmp_path)
    assert jobs[0]["title"] == "Applied ML Engineer"
    assert jobs[0]["company"] == "Acme Robotics"
    assert jobs[0]["skills"] == ["Docker", "Python"]


def test_company_containing_province_code_letters(tmp_path):
    jobs, _ = _parse(tmp_path)
    assert jobs[1]["title"] == "Software Engineer"
    assert jobs[1]["company"] == "AMAZON, Inc."


def test_skipped_count_excludes_insight_overlays(tmp_path):
    jobs, skipped = _parse(tmp_path)
    assert len(jobs) == 2
    assert skipped == 1


def test_parse_jobs_from_file_returns_list(tmp_path):
    path = tmp_path / "jobs.txt"
    path.write_text(POSTINGS, encoding="utf-8")
    assert len(parse_jobs_from_file(str(path))) == 2
