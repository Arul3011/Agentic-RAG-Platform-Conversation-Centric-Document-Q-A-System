from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.conversation import Conversation


class ConversationRepository:
    def create(self, db: Session, title: str = "New Conversation") -> Conversation:
        conv = Conversation(title=title)
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return conv

    def get(self, db: Session, conversation_id: str) -> Optional[Conversation]:
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def list_all(self, db: Session, limit: int = 50, offset: int = 0) -> List[Conversation]:
        return (
            db.query(Conversation)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def update_summary(self, db: Session, conversation_id: str, summary: str) -> Optional[Conversation]:
        conv = self.get(db, conversation_id)
        if conv:
            conv.summary = summary
            db.commit()
            db.refresh(conv)
        return conv

    def update_title(self, db: Session, conversation_id: str, title: str) -> Optional[Conversation]:
        conv = self.get(db, conversation_id)
        if conv:
            conv.title = title
            db.commit()
            db.refresh(conv)
        return conv

    def delete(self, db: Session, conversation_id: str) -> bool:
        conv = self.get(db, conversation_id)
        if conv:
            db.delete(conv)
            db.commit()
            return True
        return False


conversation_repo = ConversationRepository()
