from src.config.skills import ALIASES, STRICT_SKILLS, ALL_SKILLS, PROPER_NOUN_SKILLS
from src.config.weights import SKILL_WEIGHTS
from src.parsing.skills_extraction import extract_skills


def _extract(text):
    return extract_skills(text, ALL_SKILLS)


def test_every_canonical_name_is_extractable():
    known = set(ALL_SKILLS)
    assert set(ALIASES.values()) <= known
    assert set(STRICT_SKILLS.values()) <= known
    assert set(PROPER_NOUN_SKILLS.values()) <= known
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


def test_non_technical_skills_are_extracted():
    found = _extract("Prepare journal entries, own month end close and reconcile accounts payable in QuickBooks.")
    assert {"Journal Entries", "Month-End Close", "Accounts Payable", "QuickBooks"} <= set(found)


def test_excel_verb_is_not_a_skill():
    assert "Excel" not in _extract("You will excel in a fast-paced environment.")
    assert "Excel" in _extract("Advanced Excel skills, including pivot tables.")


def test_single_word_domain_skills_do_not_lemma_match():
    assert "Purchasing" not in _extract("Employees may purchase discounted stock.")
