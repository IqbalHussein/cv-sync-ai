import argparse
import json
import os
from src.parsing.job_parser import parse_jobs_with_stats
from src.parsing.resume_parser import parse_resume_from_file
from src.matching.matcher import match_resume_to_jobs
from src.reporting import build_match_report


def _default_resume_path() -> str:
    """Prefer a PDF resume in data/ when present, otherwise the text resume."""
    if os.path.exists("data/resume.pdf"):
        return "data/resume.pdf"
    return "data/resume.txt"


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Match a resume against job postings.")
    parser.add_argument("--jobs", default="sample-postings.txt",
                        help="Job postings file, postings separated by '====' (default: %(default)s)")
    parser.add_argument("--resume", default=None,
                        help="Resume file, .txt or .pdf (default: data/resume.pdf if present, else data/resume.txt)")
    parser.add_argument("--out", default="data",
                        help="Directory for structured JSON output and the match report (default: %(default)s)")
    parser.add_argument("--top", type=int, default=5,
                        help="Number of top matches to print (default: %(default)s)")
    return parser.parse_args(argv)


def main(argv=None):
    """
    Main entry point for the CVSyncAI application.
    
    This function orchestrates the complete workflow:
    1. Parses job postings from a text file and saves structured data to JSON
    2. Parses resume from a text or PDF file and saves structured data to JSON
    3. Matches resume skills against job requirements
    4. Displays the top job matches with scores and skill breakdowns
    5. Generates a comprehensive match report saved to JSON
    
    The matching algorithm blends weighted skill scoring with semantic
    similarity to rank jobs.
    """
    args = parse_args(argv)
    os.makedirs(args.out, exist_ok=True)

    jobs, skipped = parse_jobs_with_stats(args.jobs)
    print(f"Parsed {len(jobs)} job postings from {args.jobs}" + (f" ({skipped} skipped)" if skipped else ""))
    with open(os.path.join(args.out, "structured_jobs.json"), "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

    resume_path = args.resume or _default_resume_path()
    print(f"Using resume: {resume_path}")

    resume = parse_resume_from_file(resume_path)
    with open(os.path.join(args.out, "resume_structured.json"), "w", encoding="utf-8") as f:
        json.dump(resume, f, indent=2, ensure_ascii=False)

    # choose which resume skill list to match with
    resume_skills = resume["skills_all"]
    # Pass full resume object for granular semantic matching
    results = match_resume_to_jobs(jobs, resume_skills, resume_data=resume)

    print(f"\nTop {args.top} job matches:\n")
    for i, r in enumerate(results[:args.top], start=1):
        print(f"{i}) {r['title']} — {r['company']} | final={r['final_score']} | skills={r['score']} "
            f"| semantic={r.get('semantic_score', 0)} ({r['matched_weight']}/{r['total_weight']})")
        print("   matched:", ", ".join(r["matched_skills"]) if r["matched_skills"] else "None")
        if r["missing_skills"]:
            print("   missing:", ", ".join(r["missing_skills"][:12]) + (" ..." if len(r["missing_skills"]) > 12 else ""))
        else:
            print("   missing: None")
        print()

    match_report = build_match_report(results, resume_skills)
    report_path = os.path.join(args.out, "match_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(match_report, f, indent=2, ensure_ascii=False)
    print(f"Match report written to {report_path}")

if __name__ == "__main__":
    main()
