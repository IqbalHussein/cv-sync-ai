from datetime import datetime
from fpdf import FPDF


def cover_letter_to_pdf(
    cover_letter_text: str,
    job_title: str,
    company: str,
) -> bytes:
    """
    Render a cover letter string into a clean PDF document.

    Args:
        cover_letter_text: The plain-text or lightly-formatted cover letter.
        job_title: Target job title (used in the PDF header).
        company: Target company name (used in the PDF header).

    Returns:
        Raw PDF bytes suitable for Streamlit's download_button.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()

    pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(100, 100, 100)
    date_str = datetime.now().strftime("%B %d, %Y")
    pdf.cell(0, 8, date_str, align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)

    pdf.set_font("Helvetica", style="B", size=14)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, f"Cover Letter: {job_title}", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, company, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(8)

    clean_text = _strip_markdown(cover_letter_text)

    pdf.set_font("Helvetica", size=11)
    pdf.set_text_color(40, 40, 40)

    paragraphs = clean_text.split("\n\n")
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        pdf.multi_cell(0, 6, paragraph)
        pdf.ln(4)

    return bytes(pdf.output())


def _strip_markdown(text: str) -> str:
    """
    Remove common Markdown formatting characters so the PDF body
    contains clean prose.

    Args:
        text: Markdown-formatted string.

    Returns:
        Plain text with bold/italic markers and heading hashes removed.
    """
    import re
    lines = []
    for line in text.splitlines():
        line = re.sub(r"^#{1,6}\s+", "", line)
        line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
        line = re.sub(r"__(.+?)__", r"\1", line)
        line = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"\1", line)
        lines.append(line.strip())
    return "\n".join(lines)
