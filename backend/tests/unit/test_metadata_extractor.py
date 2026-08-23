import pytest
from app.document_processing.metadata_extractor import extract_metadata


def test_basic_structure():
    meta = extract_metadata("some text", "test.pdf", "pdf")
    assert "file_type" in meta
    assert "char_count" in meta
    assert "word_count" in meta


def test_technical_detection():
    text = "This API endpoint handles HTTP requests and returns JSON responses"
    meta = extract_metadata(text, "api.pdf", "pdf")
    assert meta["document_type"] == "technical"


def test_legal_detection():
    text = "This agreement and contract outlines the liability clauses"
    meta = extract_metadata(text, "contract.pdf", "pdf")
    assert meta["document_type"] == "legal"


def test_financial_detection():
    text = "Quarterly revenue and profit and loss balance sheet"
    meta = extract_metadata(text, "report.pdf", "pdf")
    assert meta["document_type"] == "financial"


def test_version_extraction():
    text = "Version 2.3.1 of the system documentation"
    meta = extract_metadata(text, "doc.txt", "txt")
    assert meta.get("version") == "2.3.1"


def test_char_count_correct():
    text = "hello world"
    meta = extract_metadata(text, "f.txt", "txt")
    assert meta["char_count"] == len(text)
