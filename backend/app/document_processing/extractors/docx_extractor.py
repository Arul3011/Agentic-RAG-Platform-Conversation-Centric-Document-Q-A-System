from typing import List, Dict, Any
from docx import Document
from app.core.logging import get_logger

logger = get_logger(__name__)


def extract_docx(path: str) -> List[Dict[str, Any]]:
    """Return list of {page_number, text} — DOCX has no pages so we chunk by paragraphs."""
    doc = Document(path)
    full_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    logger.info(f"DOCX extracted: {len(full_text)} chars from {path}")
    return [{"page_number": 1, "text": full_text}]
