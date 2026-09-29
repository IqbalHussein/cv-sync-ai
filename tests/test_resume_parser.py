from src.parsing.resume_parser import split_resume_sections


def test_sections_split_on_aliases_and_caps_headings():
    text = "\n".join([
        "Jane Doe",
        "jane@example.com",
        "Technical Skills:",
        "Python, Docker",
        "WORK EXPERIENCE",
        "- Built data pipelines",
        "Education",
        "BSc Computer Science",
    ])
    sections = split_resume_sections(text)
    assert sections["summary"].startswith("Jane Doe")
    assert sections["skills"] == "Python, Docker"
    assert sections["experience"] == "- Built data pipelines"
    assert sections["education"] == "BSc Computer Science"


def test_no_headings_puts_everything_in_summary():
    assert split_resume_sections("just some text\nmore text") == {"summary": "just some text\nmore text"}
