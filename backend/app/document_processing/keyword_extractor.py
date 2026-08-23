"""
Lightweight keyword extraction — uses frequency + stopword filtering.
No external API call needed; an LLM version can replace this later.
"""
import re
from typing import List
from collections import Counter

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "this", "that", "these", "those",
    "it", "its", "we", "you", "he", "she", "they", "i", "not", "as", "if",
    "can", "all", "also", "more", "than", "so", "up", "out", "about",
}


def extract_keywords(text: str, top_n: int = 15) -> List[str]:
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_\-]{2,}\b", text.lower())
    filtered = [w for w in words if w not in STOPWORDS]
    freq = Counter(filtered)
    return [word for word, _ in freq.most_common(top_n)]
