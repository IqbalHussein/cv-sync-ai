from datetime import datetime, timezone


def build_match_report(results: list[dict], resume_skills: list[str]) -> dict:
    """
    Build a machine-readable match report from ranked match results.

    Shared by the CLI and the Streamlit app so both export the same schema.

    Args:
        results: Match result dictionaries, already ranked best-first.
        resume_skills: Skills extracted from the resume that were used for matching.

    Returns:
        Dictionary with a UTC 'generated_at' timestamp, the resume skills used,
        and one entry per result with its rank, scores, and skill breakdown.
    """
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "resume": {
            "skills_used": resume_skills
        },
        "results": []
    }

    for rank, r in enumerate(results, start=1):
        report["results"].append({
            "rank": rank,
            "title": r["title"],
            "company": r["company"],
            "final_score": r.get("final_score", r["score"]),
            "score": round(r["score"], 3),
            "semantic_score": r.get("semantic_score", 0),
            "matched_skills": r["matched_skills"],
            "missing_skills": r["missing_skills"]
        })

    return report
