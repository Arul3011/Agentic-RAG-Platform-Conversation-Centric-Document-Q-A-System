from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.conversation_repository import conversation_repo
from app.repositories.message_repository import message_repo
from app.models.conversation import Conversation


class ConversationService:
    def create(self, db: Session, title: str = "New Conversation") -> Conversation:
        return conversation_repo.create(db, title)

    def list_all(self, db: Session) -> List[Conversation]:
        return conversation_repo.list_all(db)

    def get(self, db: Session, conversation_id: str) -> Optional[Conversation]:
        return conversation_repo.get(db, conversation_id)

    def get_messages(self, db: Session, conversation_id: str):
        return message_repo.list_by_conversation(db, conversation_id)

    def delete(self, db: Session, conversation_id: str) -> bool:
        return conversation_repo.delete(db, conversation_id)


conversation_service = ConversationService()
