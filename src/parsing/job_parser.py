from src.config.skills import NOISE_SUBSTRINGS, NOISE_EXACT_LINES, META_SUBSTRINGS, TITLE_KEYWORDS, ALL_SKILLS
import logging
import re
from src.parsing.text_utilities import read_text_file, normalize_text
from src.parsing.skills_extraction import extract_skills

logger = logging.getLogger(__name__)

PROVINCE_CODE_RE = re.compile(r"\b(ON|QC|BC|AB|MB|NS|NB|NL|PE|SK|YT|NT|NU)\b")

def parse_jobs_from_file(filename):
    """
    Parse job postings from a text file into structured job records.

    Convenience wrapper around parse_jobs_with_stats() that discards the
    skipped-posting count.
    """
    jobs, _ = parse_jobs_with_stats(filename)
    return jobs

def parse_jobs_with_stats(filename) -> tuple[list[dict], int]:
    """
    Parse job postings from a text file into structured job records.
    
    Reads a file containing multiple job postings separated by '====', extracts
    the title, company, and required skills from each posting, and returns a list
    of structured job dictionaries.
    
    Args:
        filename: Path to the file containing job postings
        
    Returns:
        Tuple of (jobs, skipped) where jobs is a list of job dictionaries, each containing:
        - 'id': Sequential job ID
        - 'title': Job title
        - 'company': Company name
        - 'skills': List of extracted technical skills
        - 'text': Original job posting text
        and skipped is the number of postings dropped because no title or
        company could be identified. "Profile insights" overlay chunks are
        not postings and are not counted.
    """
    def clean_lines(job_text: str) -> list[str]:
        """
        Split job text into non-empty lines with whitespace stripped.
        
        Args:
            job_text: Raw job posting text
            
        Returns:
            List of non-empty, trimmed lines
        """
        lines = [ln.strip() for ln in job_text.splitlines()]
        lines = [ln for ln in lines if ln]  # remove empty
        return lines

    def is_noise_line(line: str) -> bool:
        """
        Determine if a line contains noise/boilerplate text to be filtered out.
        
        Checks against common LinkedIn/Indeed UI elements like "Easy Apply",
        "Show more", "Benefits", etc. Short labels in NOISE_EXACT_LINES only
        count when they are the whole line, so titles like "Applied ML
        Engineer" are kept.
        
        Args:
            line: Text line to check
            
        Returns:
            True if line is noise and should be filtered, False otherwise
        """
        l = line.lower()
        if l.strip().rstrip(":") in NOISE_EXACT_LINES:
            return True
        return any(s in l for s in NOISE_SUBSTRINGS)

    def is_rating(line: str) -> bool:
        """
        Determine if a line represents a company rating.
        
        Detects patterns like "4.5", "3.2", or "4.5 out of 5 stars".
        
        Args:
            line: Text line to check
            
        Returns:
            True if line appears to be a rating, False otherwise
        """
        l = line.lower()
        if "out of 5 stars" in l:
            return True
        return bool(re.fullmatch(r"\d(\.\d)?", line.strip()))

    def is_job_type(line: str) -> bool:
        """
        Determine if a line indicates job type (full-time, contract, etc.).
        
        Args:
            line: Text line to check
            
        Returns:
            True if line matches a known job type, False otherwise
        """
        l = line.lower()
        return l in {"full-time", "part-time", "contract", "permanent", "internship", "temporary"}

    def is_location_or_meta(line: str) -> bool:
        """
        Determine if a line contains location or metadata information.
        
        Detects Canadian provincial codes (ON, BC, etc.), work arrangements
        (hybrid, remote), and metadata like "reposted" or "applicants".
        
        Args:
            line: Text line to check
            
        Returns:
            True if line appears to be location/metadata, False otherwise
        """
        l = line.lower()

        if "·" in line and any(s in l for s in META_SUBSTRINGS):
            return True
        # Canadian provincial & territorial locations
        if PROVINCE_CODE_RE.search(line):
            if "·" in line or "," in line or "(" in line:
                return True
        if "hybrid" in l or "remote" in l or "on-site" in l:
            # these are often meta/location lines, not company
            return True
        return False
        

    def title_like(line: str) -> bool:
        """
        Determine if a line looks like a job title.
        
        Uses heuristics including:
        - Contains job-related keywords (engineer, developer, software, etc.)
        - Reasonable length (4-90 characters)
        - Not a noise line or metadata line
        
        Args:
            line: Text line to check
            
        Returns:
            True if line appears to be a job title, False otherwise
        """
        l = line.lower()
        if is_noise_line(line):
            return False
        if any(s in l for s in META_SUBSTRINGS):
            return False
        if l.startswith("save "):
            return False
        if " at " in l and l.startswith("save "):
            return False
        if len(line) < 4 or len(line) > 90:
            return False
        return any(k in l for k in TITLE_KEYWORDS)
    
    def extract_title_company(job_text: str) -> tuple[str | None, str | None]:
        """
        Extract job title and company name from a job posting.
        
        Uses multiple heuristics to handle different job board formats:
        - Indeed-style: "Title - job post" followed by company name
        - LinkedIn-style: First title-like line, company in "Company · Location" format
        - "Save <title> at <company>" pattern
        
        Args:
            job_text: Raw job posting text
            
        Returns:
            Tuple of (title, company), either may be None if not found
        """
        lines = clean_lines(job_text)
        if not lines:
            return None, None

        # If it's an "insights overlay" chunk, skip it
        if lines[0].lower() == "profile insights":
            return None, None

        # Remove obvious noise lines (keep order)
        filtered = [ln for ln in lines if not is_noise_line(ln)]

        # ---- TITLE ----
        title = None

        # T1: Indeed-style "- job post"
        for ln in filtered:
            if "- job post" in ln.lower():
                title = ln
                break

        # T2: LinkedIn-style: first title-like line
        if title is None:
            for ln in filtered[:25]:  # usually near top
                if title_like(ln):
                    title = ln
                    break

        # ---- COMPANY ----
        company = None

        # C1: "Save <title> at <company>"
        for ln in filtered[:60]:
            l = ln.lower()
            if l.startswith("save ") and " at " in l:
                company = ln.split(" at ", 1)[1].strip()
                # strip trailing junk if present
                company = re.split(r"\s{2,}|\s·\s", company)[0].strip()
                break

        # C2: "Company · Location"
        if company is None:
            for ln in filtered[:60]:
                if "·" in ln:
                    left = ln.split("·", 1)[0].strip()
                    # Avoid meta lines like "Ottawa, ON · Reposted..."
                    if left and not is_location_or_meta(ln) and not is_job_type(left):
                        # left side should not itself look like a location
                        if not is_location_or_meta(left) and not is_rating(left):
                            company = left
                            break

        # C3: Indeed-style: next clean line after title
        if company is None and title is not None:
            try:
                t_idx = filtered.index(title)
                for ln in filtered[t_idx + 1 : t_idx + 12]:
                    if is_rating(ln) or is_location_or_meta(ln) or is_job_type(ln):
                        continue
                    company = ln
                    break
            except ValueError:
                pass

        return title, company
    raw_file_data = read_text_file(filename)

    jobs = raw_file_data.split("====")

    structured_jobs = []
    skipped = 0
    for idx, job in enumerate(jobs):
        # Split the job posting into lines and remove empty lines
        lines = job.splitlines()
        lines = [line.strip() for line in lines if line.strip()]

        if not lines:
            continue

        # Pull skills from job postings
        found_skills = extract_skills(job, ALL_SKILLS)

        title, company = extract_title_company(job)

        if title is None or company is None:
            if lines[0].lower() != "profile insights":
                skipped += 1
                logger.warning("Skipped posting #%d: could not identify title/company (%r)", idx + 1, lines[0][:60])
            continue

        job_record = {
            "id": idx + 1,
            "title": title,
            "company": company,
            "skills": found_skills,
            "text": job,
        }

        structured_jobs.append(job_record)
        
    return structured_jobs, skipped
