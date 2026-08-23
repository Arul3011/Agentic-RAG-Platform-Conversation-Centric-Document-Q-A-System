import pytest
from app.document_processing.keyword_extractor import extract_keywords


def test_returns_list():
    result = extract_keywords("The quick brown fox jumps over the lazy dog")
    assert isinstance(result, list)


def test_excludes_stopwords():
    result = extract_keywords("the and or but in on at for of with by from is are")
    # All words are stopwords, result may be empty
    assert "the" not in result
    assert "and" not in result


def test_top_n_limit():
    text = " ".join([f"word{i}" for i in range(100)])
    result = extract_keywords(text, top_n=5)
    assert len(result) <= 5


def test_extracts_meaningful_words():
    text = "authentication JWT token expiration security OAuth endpoint"
    result = extract_keywords(text, top_n=10)
    assert "authentication" in result or "token" in result or "security" in result


def test_empty_text():
    result = extract_keywords("")
    assert result == []
