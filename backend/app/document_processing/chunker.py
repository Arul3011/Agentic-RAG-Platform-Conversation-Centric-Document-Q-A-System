from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def chunk_text(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Split pages into overlapping chunks of at most CHUNK_SIZE characters.
    Returns list of chunk dicts with page_number, content, chunk_index.
    """
    chunk_size = settings.CHUNK_SIZE
    overlap = settings.CHUNK_OVERLAP
    chunks: List[Dict[str, Any]] = []
    idx = 0

    logger.info(f"Starting chunking: {len(pages)} pages, chunk_size={chunk_size}, overlap={overlap}")

    for page in pages:
        page_num = page["page_number"]
        text = page["text"]
        if not text:
            logger.debug(f"Page {page_num}: empty, skipping")
            continue

        page_chunk_count = 0
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_content = text[start:end].strip()
            if chunk_content:
                section = _detect_section(chunk_content)
                chunks.append({
                    "chunk_index": idx,
                    "content": chunk_content,
                    "page_number": page_num,
                    "section": section,
                })
                idx += 1
                page_chunk_count += 1
            start += chunk_size - overlap

        logger.debug(f"Page {page_num}: produced {page_chunk_count} chunks ({len(text)} chars)")

    logger.info(f"Chunking complete: {len(pages)} pages → {len(chunks)} chunks created")
    return chunks


def _detect_section(text: str) -> str:
    """Heuristic: first short ALL-CAPS or Title-Case line as section header."""
    for line in text.split("\n")[:5]:
        line = line.strip()
        if 2 < len(line) < 80 and (line.isupper() or line.istitle()):
            return line
    return ""
