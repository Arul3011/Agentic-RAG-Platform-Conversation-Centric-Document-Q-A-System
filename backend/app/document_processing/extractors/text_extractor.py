from typing import List, Dict, Any
from app.core.logging import get_logger

logger = get_logger(__name__)


def extract_text(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    logger.info(f"Text extracted: {len(text)} chars from {path}")
    return [{"page_number": 1, "text": text}]
