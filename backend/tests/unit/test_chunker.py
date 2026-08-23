import pytest
from app.document_processing.chunker import chunk_text, _detect_section


def test_chunk_text_basic():
    pages = [{"page_number": 1, "text": "Hello world " * 100}]
    chunks = chunk_text(pages)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c["content"]) <= 750  # chunk_size + a bit of slack


def test_chunk_text_preserves_page_number():
    pages = [
        {"page_number": 3, "text": "Page three content " * 50},
    ]
    chunks = chunk_text(pages)
    assert all(c["page_number"] == 3 for c in chunks)


def test_chunk_text_empty_page():
    pages = [{"page_number": 1, "text": ""}]
    chunks = chunk_text(pages)
    assert chunks == []


def test_chunk_text_short_content():
    pages = [{"page_number": 1, "text": "Short text."}]
    chunks = chunk_text(pages)
    assert len(chunks) == 1
    assert chunks[0]["content"] == "Short text."


def test_chunk_indices_sequential():
    pages = [{"page_number": 1, "text": "word " * 500}]
    chunks = chunk_text(pages)
    indices = [c["chunk_index"] for c in chunks]
    assert indices == list(range(len(chunks)))


def test_detect_section_title_case():
    text = "Authentication Module\nThis section covers..."
    assert _detect_section(text) == "Authentication Module"


def test_detect_section_none():
    text = "plain lowercase text with no headers"
    # should return empty string or at least not crash
    assert isinstance(_detect_section(text), str)
