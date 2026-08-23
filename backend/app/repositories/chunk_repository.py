from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, cast, String
from app.models.chunk import DocumentChunk
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ChunkRepository:
    def bulk_create(self, db: Session, chunks: List[DocumentChunk]) -> None:
        db.add_all(chunks)
        db.commit()

    def vector_search(
        self, db: Session, conversation_id: str, embedding: List[float], top_k: int
    ) -> List[DocumentChunk]:
        """Cosine similarity search using pgvector <=> operator."""
        vec_str = "[" + ",".join(str(v) for v in embedding) + "]"
        raw = db.execute(
            text(
                f"SELECT id, 1 - (embedding <=> '{vec_str}'::vector) AS score "
                f"FROM document_chunks "
                f"WHERE conversation_id = :conv_id AND embedding IS NOT NULL "
                f"ORDER BY embedding <=> '{vec_str}'::vector "
                f"LIMIT :k"
            ),
            {"conv_id": conversation_id, "k": top_k},
        ).fetchall()
        ids = [r[0] for r in raw]
        scores = {r[0]: r[1] for r in raw}
        chunks = db.query(DocumentChunk).filter(DocumentChunk.id.in_(ids)).all()
        # Attach similarity scores as transient attributes
        for c in chunks:
            c._similarity_score = scores.get(c.id, 0.0)
        chunks.sort(key=lambda c: c._similarity_score, reverse=True)
        return chunks

    def keyword_search(
        self, db: Session, conversation_id: str, query: str, top_k: int
    ) -> List[DocumentChunk]:
        """PostgreSQL full-text search."""
        raw = db.execute(
            text(
                "SELECT id, ts_rank(to_tsvector('english', content), plainto_tsquery('english', :q)) AS score "
                "FROM document_chunks "
                "WHERE conversation_id = :conv_id "
                "AND to_tsvector('english', content) @@ plainto_tsquery('english', :q) "
                "ORDER BY score DESC LIMIT :k"
            ),
            {"conv_id": conversation_id, "q": query, "k": top_k},
        ).fetchall()
        ids = [r[0] for r in raw]
        scores = {r[0]: float(r[1]) for r in raw}
        chunks = db.query(DocumentChunk).filter(DocumentChunk.id.in_(ids)).all()
        for c in chunks:
            c._similarity_score = scores.get(c.id, 0.0)
        chunks.sort(key=lambda c: c._similarity_score, reverse=True)
        return chunks

    def metadata_search(
        self, db: Session, conversation_id: str, filters: dict, top_k: int
    ) -> List[DocumentChunk]:
        """JSON metadata filtering (portable across JSON / JSONB column types)."""
        q = db.query(DocumentChunk).filter(
            DocumentChunk.conversation_id == conversation_id
        )
        for key, value in filters.items():
            q = q.filter(
                cast(DocumentChunk.metadata_[key], String) == str(value)
            )
        chunks = q.limit(top_k).all()
        for c in chunks:
            c._similarity_score = 0.5
        return chunks

    def get_by_conversation(self, db: Session, conversation_id: str) -> List[DocumentChunk]:
        return db.query(DocumentChunk).filter(
            DocumentChunk.conversation_id == conversation_id
        ).all()


chunk_repo = ChunkRepository()