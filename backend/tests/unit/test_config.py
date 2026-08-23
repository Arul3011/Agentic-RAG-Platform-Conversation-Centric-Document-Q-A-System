import pytest
from app.core.config import settings


def test_settings_loaded():
    assert settings.APP_NAME == "Agentic-RAG"


def test_vector_dimension_positive():
    assert settings.VECTOR_DIMENSION > 0


def test_chunk_size_positive():
    assert settings.CHUNK_SIZE > 0
    assert settings.CHUNK_OVERLAP < settings.CHUNK_SIZE


def test_max_file_size_bytes():
    assert settings.max_file_size_bytes == settings.MAX_FILE_SIZE_MB * 1024 * 1024


def test_database_url_set():
    assert settings.DATABASE_URL.startswith("postgresql")
