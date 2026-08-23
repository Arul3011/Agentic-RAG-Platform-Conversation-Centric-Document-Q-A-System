import pytest
from unittest.mock import MagicMock
from app.retrieval.reranker import reciprocal_rank_fusion, rerank


def _make_chunk(chunk_id: str):
    chunk = MagicMock()
    chunk.id = chunk_id
    return chunk


def test_rrf_single_list():
    chunks = [_make_chunk(f"c{i}") for i in range(5)]
    result = reciprocal_rank_fusion([chunks])
    assert len(result) == 5
    ids = [c.id for c, _ in result]
    assert ids[0] == "c0"  # rank 1 always gets highest score


def test_rrf_combines_lists():
    list_a = [_make_chunk("a"), _make_chunk("b"), _make_chunk("c")]
    list_b = [_make_chunk("b"), _make_chunk("a"), _make_chunk("d")]
    result = reciprocal_rank_fusion([list_a, list_b])
    ids = [c.id for c, _ in result]
    # "a" and "b" appear in both lists, should rank higher than "c" and "d"
    assert ids.index("a") < ids.index("c")
    assert ids.index("b") < ids.index("d")


def test_rerank_limits_final_k():
    chunks = [_make_chunk(f"c{i}") for i in range(10)]
    result = rerank([chunks], final_k=3)
    assert len(result) == 3


def test_rrf_scores_positive():
    chunks = [_make_chunk(f"c{i}") for i in range(3)]
    result = reciprocal_rank_fusion([chunks])
    assert all(score > 0 for _, score in result)
