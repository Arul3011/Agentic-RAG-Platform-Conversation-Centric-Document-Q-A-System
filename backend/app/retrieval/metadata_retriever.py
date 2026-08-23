from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.chunk_repository import chunk_repo
from app.models.chunk import DocumentChunk


def metadata_retrieve(
    db: Session, conversation_id: str, filters: Dict[str, Any], top_k: int
) -> List[DocumentChunk]:
    return chunk_repo.metadata_search(db, conversation_id, filters, top_k)
