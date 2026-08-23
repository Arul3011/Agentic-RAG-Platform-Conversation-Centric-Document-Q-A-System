from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.chunk import DocumentChunk
from app.retrieval.vector_retriever import vector_retrieve
from app.retrieval.keyword_retriever import keyword_retrieve
from app.retrieval.metadata_retriever import metadata_retrieve
from app.retrieval.hybrid_retriever import hybrid_retrieve
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RetrievalService:
    def retrieve(
        self,
        db: Session,
        conversation_id: str,
        strategy: str,
        query: str,
        metadata_filters: Dict[str, Any],
        top_k: int,
    ) -> List[Tuple[DocumentChunk, float]]:
        logger.info(f"Retrieval: strategy={strategy}, query={query!r}, conv={conversation_id}")

        if strategy == "vector":
            chunks = vector_retrieve(db, conversation_id, query, top_k)
            if not chunks:
                # gracefully fall back to keyword
                logger.info("Vector returned empty, falling back to keyword")
                chunks = keyword_retrieve(db, conversation_id, query, top_k)
            return [(c, getattr(c, "_similarity_score", 0.9)) for c in chunks]

        elif strategy == "keyword":
            chunks = keyword_retrieve(db, conversation_id, query, top_k)
            return [(c, getattr(c, "_similarity_score", 0.8)) for c in chunks]

        elif strategy == "metadata":
            chunks = metadata_retrieve(db, conversation_id, metadata_filters, top_k)
            return [(c, getattr(c, "_similarity_score", 0.7)) for c in chunks]

        elif strategy == "hybrid":
            return hybrid_retrieve(db, conversation_id, query, metadata_filters, top_k)

        else:
            logger.warning(f"Unknown strategy '{strategy}', defaulting to keyword")
            chunks = keyword_retrieve(db, conversation_id, query, top_k)
            return [(c, getattr(c, "_similarity_score", 0.5)) for c in chunks]


retrieval_service = RetrievalService()
