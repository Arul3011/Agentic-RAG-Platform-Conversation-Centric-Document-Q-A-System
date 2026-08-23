from sqlalchemy.orm import Session
from app.models.retrieval_log import RetrievalLog


class RetrievalRepository:
    def log(
        self,
        db: Session,
        conversation_id: str,
        message_id: str,
        strategy: str,
        search_query: str,
        metadata_filters: dict,
        top_k: int,
        retrieved_chunk_ids: list,
    ) -> RetrievalLog:
        log = RetrievalLog(
            conversation_id=conversation_id,
            message_id=message_id,
            strategy=strategy,
            search_query=search_query,
            metadata_filters=metadata_filters,
            top_k=top_k,
            retrieved_chunks=retrieved_chunk_ids,
        )
        db.add(log)
        db.commit()
        return log


retrieval_repo = RetrievalRepository()
