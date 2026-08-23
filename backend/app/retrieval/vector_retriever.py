from typing import List
from sqlalchemy.orm import Session
from app.repositories.chunk_repository import chunk_repo
from app.services.embedding_service import embedding_service
from app.models.chunk import DocumentChunk
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def vector_retrieve(db: Session, conversation_id: str, query: str, top_k: int) -> List[DocumentChunk]:
    """
    Perform cosine similarity search. Returns empty list if Gemini is not configured
    or no embeddings exist — callers must handle graceful degradation.
    """
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        logger.warning("Vector retrieval skipped — GEMINI_API_KEY not configured")
        return []
    try:
        embedding = embedding_service.embed_text(query)
        return chunk_repo.vector_search(db, conversation_id, embedding, top_k)
    except Exception as e:
        logger.warning(f"Vector retrieval failed ({e}), returning empty results")
        return []
