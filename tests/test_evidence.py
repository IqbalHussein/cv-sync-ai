from src.matching.evidence import find_skill_evidence


def test_evidence_respects_word_boundaries():
    text = "Account manager\nWrote C code\nUsed C++ daily"
    evidence = find_skill_evidence(text, ["C", "C++"])
    assert "L1: Account manager" not in evidence["C"]
    assert "L2: Wrote C code" in evidence["C"]
    assert evidence["C++"] == ["L3: Used C++ daily"]


def test_evidence_includes_aliases_and_caps_lines():
    text = "\n".join(f"Used sklearn in project {i}" for i in range(5))
    evidence = find_skill_evidence(text, ["scikit-learn"], max_lines_per_skill=2)
    assert len(evidence["scikit-learn"]) == 2
