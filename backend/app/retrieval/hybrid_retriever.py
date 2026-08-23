from typing import List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from app.retrieval.vector_retriever import vector_retrieve
from app.retrieval.keyword_retriever import keyword_retrieve
from app.retrieval.metadata_retriever import metadata_retrieve
from app.retrieval.reranker import rerank
from app.models.chunk import DocumentChunk
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def hybrid_retrieve(
    db: Session,
    conversation_id: str,
    query: str,
    metadata_filters: Dict[str, Any],
    top_k: int,
) -> List[Tuple[DocumentChunk, float]]:
    result_lists = []

    if settings.VECTOR_SEARCH_ENABLED:
        vec_results = vector_retrieve(db, conversation_id, query, top_k)
        if vec_results:
            result_lists.append(vec_results)

    if settings.KEYWORD_SEARCH_ENABLED:
        kw_results = keyword_retrieve(db, conversation_id, query, top_k)
        if kw_results:
            result_lists.append(kw_results)

    if settings.METADATA_SEARCH_ENABLED and metadata_filters:
        meta_results = metadata_retrieve(db, conversation_id, metadata_filters, top_k)
        if meta_results:
            result_lists.append(meta_results)

    if not result_lists:
        logger.info("Hybrid retrieve: no results from any strategy")
        return []

    return rerank(result_lists, settings.FINAL_CONTEXT_K)
