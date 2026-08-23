"""
Simple reciprocal-rank fusion reranker.
Combines results from multiple retrieval strategies.
"""
from typing import List, Dict, Tuple
from app.models.chunk import DocumentChunk


def reciprocal_rank_fusion(
    result_lists: List[List[DocumentChunk]], k: int = 60
) -> List[Tuple[DocumentChunk, float]]:
    """RRF: score = sum(1 / (k + rank)) across lists."""
    scores: Dict[str, float] = {}
    chunk_map: Dict[str, DocumentChunk] = {}

    for results in result_lists:
        for rank, chunk in enumerate(results, start=1):
            scores[chunk.id] = scores.get(chunk.id, 0.0) + 1.0 / (k + rank)
            chunk_map[chunk.id] = chunk

    ranked = sorted(chunk_map.keys(), key=lambda cid: scores[cid], reverse=True)
    return [(chunk_map[cid], scores[cid]) for cid in ranked]


def rerank(
    result_lists: List[List[DocumentChunk]], final_k: int
) -> List[Tuple[DocumentChunk, float]]:
    fused = reciprocal_rank_fusion(result_lists)
    return fused[:final_k]
