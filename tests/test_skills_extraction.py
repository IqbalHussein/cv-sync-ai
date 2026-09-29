from src.config.skills import ALIASES, STRICT_SKILLS, SOFT_ENG_SKILLS
from src.config.weights import SKILL_WEIGHTS
from src.parsing.skills_extraction import extract_skills


def _extract(text):
    return extract_skills(text, SOFT_ENG_SKILLS)


def test_every_canonical_name_is_extractable():
    known = set(SOFT_ENG_SKILLS)
    assert set(ALIASES.values()) <= known
    assert set(STRICT_SKILLS.values()) <= known
    assert set(SKILL_WEIGHTS) <= known


def test_aliases_map_to_canonical_names():
    found = _extract("Experience with sklearn, torch and ml flow pipelines.")
    assert {"scikit-learn", "PyTorch", "MLflow"} <= set(found)


def test_tdd_alias_merges_with_full_name():
    assert _extract("We practice TDD daily.") == ["Test Driven Development"]


def test_c_family_not_matched_inside_words():
    assert "C" not in _extract("Account manager for a large accounting firm.")
    assert {"C", "C++"} <= set(_extract("Proficient in C and C++."))


def test_go_verb_is_not_a_skill():
    assert "Go" not in _extract("We will go to the office on Mondays.")
    assert "Go" in _extract("Backend services written in Golang.")
