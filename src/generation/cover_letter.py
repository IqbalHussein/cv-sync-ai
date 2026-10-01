import os
from src.generation import get_gemini_client

DEFAULT_MODEL = "gemini-2.5-flash"

MAX_SECTION_CHARS = 2500


class CoverLetterError(RuntimeError):
    """Raised when a cover letter cannot be generated."""

PROMPT_TEMPLATE = (
    "You are an expert career coach writing a professional cover letter. "
    "Write a concise, 3-paragraph cover letter in Markdown format.\n\n"
    "Candidate summary:\n{summary}\n\n"
    "Candidate experience:\n{experience}\n\n"
    "Candidate projects:\n{projects}\n\n"
    "Candidate skills: {skills}\n\n"
    "Target role: {title} at {company}\n"
    "Skills the candidate matches for this role: {matched_skills}\n\n"
    "Structure:\n"
    "Paragraph 1: State interest in the {title} role at {company}. "
    "Begin with 'Dear Hiring Manager,'.\n"
    "Paragraph 2: Highlight how the candidate's experience aligns with the "
    "role, specifically referencing these matched skills: {matched_skills}. "
    "Be specific and draw from the candidate experience and projects above. "
    "Do not fabricate experience.\n"
    "Paragraph 3: Enthusiastic closing with a call to action.\n\n"
    "Keep the tone professional yet personable. Do not use placeholder "
    "brackets. Output only the letter text."
)



def generate_cover_letter(resume_data: dict, match_result: dict) -> str:
    """
    Generate a 3-paragraph cover letter bridging the candidate's resume
    with a specific job's requirements using the Gemini API.

    Args:
        resume_data: Parsed resume dictionary containing 'sections' and
            'skills_all'.
        match_result: A single match result dictionary containing 'title',
            'company', and 'matched_skills'.

    Returns:
        A Markdown-formatted cover letter string.

    Raises:
        CoverLetterError: If the API key is missing, the API call fails, or
            the model returns no text.
    """
    sections = resume_data.get("sections", {})
    summary = sections.get("summary", "")
    experience = sections.get("experience", "")[:MAX_SECTION_CHARS]
    projects = sections.get("projects", "")[:MAX_SECTION_CHARS]
    skills = resume_data.get("skills_all", [])
    title = match_result.get("title", "the open position")
    company = match_result.get("company", "your company")
    matched_skills = match_result.get("matched_skills", [])

    prompt = PROMPT_TEMPLATE.format(
        summary=summary or "Not provided",
        experience=experience or "Not provided",
        projects=projects or "Not provided",
        skills=", ".join(skills),
        title=title,
        company=company,
        matched_skills=", ".join(matched_skills) if matched_skills else "general professional skills",
    )

    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model=os.environ.get("GEMINI_MODEL", DEFAULT_MODEL),
            contents=prompt,
        )
    except Exception as e:
        raise CoverLetterError(f"Cover letter generation failed: {e}") from e

    if not response.text:
        raise CoverLetterError("Cover letter generation returned no text.")
    return response.text.strip()
