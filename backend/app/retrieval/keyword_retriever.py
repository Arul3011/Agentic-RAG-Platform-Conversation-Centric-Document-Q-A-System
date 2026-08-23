from typing import List
from sqlalchemy.orm import Session
from app.repositories.chunk_repository import chunk_repo
from app.models.chunk import DocumentChunk


def keyword_retrieve(db: Session, conversation_id: str, query: str, top_k: int) -> List[DocumentChunk]:
    return chunk_repo.keyword_search(db, conversation_id, query, top_k)
