from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.message import Message


class MessageRepository:
    def create(
        self,
        db: Session,
        conversation_id: str,
        role: str,
        content: str,
        metadata: dict = None,
    ) -> Message:
        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata_=metadata or {},
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg

    def list_by_conversation(
        self, db: Session, conversation_id: str, limit: int = 100
    ) -> List[Message]:
        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
            .all()
        )

    def count_by_conversation(self, db: Session, conversation_id: str) -> int:
        return db.query(Message).filter(Message.conversation_id == conversation_id).count()

    def get_recent(self, db: Session, conversation_id: str, n: int = 20) -> List[Message]:
        rows = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(n)
            .all()
        )
        return list(reversed(rows))


message_repo = MessageRepository()
