from src.matching.semantic import _chunk_text


def test_chunking_covers_all_words():
    chunks = _chunk_text("word " * 320, chunk_words=150)
    assert [len(c.split()) for c in chunks] == [150, 150, 20]


def test_chunking_empty_text():
    assert _chunk_text("   \n ") == []
