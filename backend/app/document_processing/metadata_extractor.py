"""
Lightweight metadata extraction without LLM — heuristic based.
"""
import re
from typing import Dict, Any


def extract_metadata(text: str, file_name: str, file_type: str) -> Dict[str, Any]:
    meta: Dict[str, Any] = {
        "file_type": file_type,
        "file_name": file_name,
        "char_count": len(text),
        "word_count": len(text.split()),
    }
    # Detect document type heuristically
    lower = text.lower()
    if any(k in lower for k in ["api", "endpoint", "request", "response", "http"]):
        meta["document_type"] = "technical"
    elif any(k in lower for k in ["agreement", "contract", "liability", "clause"]):
        meta["document_type"] = "legal"
    elif any(k in lower for k in ["revenue", "profit", "loss", "balance", "quarterly"]):
        meta["document_type"] = "financial"
    else:
        meta["document_type"] = "general"

    # Detect version/date patterns
    ver = re.search(r"v(?:ersion)?\s*(\d+[\.\d]*)", text[:2000], re.IGNORECASE)
    if ver:
        meta["version"] = ver.group(1)

    date = re.search(r"\b(\d{4}[-/]\d{2}[-/]\d{2})\b", text[:2000])
    if date:
        meta["date"] = date.group(1)

    return meta
