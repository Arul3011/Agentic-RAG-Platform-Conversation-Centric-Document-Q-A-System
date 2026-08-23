from typing import List
from sqlalchemy.orm import Session
from app.models.message import Message
from app.integrations.openrouter_client import openrouter_client
from app.repositories.conversation_repository import conversation_repo
from app.agents.prompts import SUMMARIZATION_SYSTEM
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class SummaryService:
    def should_summarize(self, db: Session, conversation_id: str) -> bool:
        from app.repositories.message_repository import message_repo
        count = message_repo.count_by_conversation(db, conversation_id)
        return count > 0 and count % settings.SUMMARY_TRIGGER_MESSAGES == 0

    def summarize(
        self,
        db: Session,
        conversation_id: str,
        messages: List[Message],
    ) -> str:
        if not settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEY == "YOUR_OPENROUTER_API_KEY_HERE":
            return "Summary unavailable — OPENROUTER_API_KEY not configured."

        history = "\n".join(
            f"{m.role.upper()}: {m.content}" for m in messages
        )
        response = openrouter_client.chat_summary(
            messages=[
                {"role": "system", "content": SUMMARIZATION_SYSTEM},
                {"role": "user", "content": f"Conversation to summarize:\n\n{history}"},
            ],
            temperature=0.3,
            max_tokens=512,
        )
        conversation_repo.update_summary(db, conversation_id, response)
        logger.info(f"Conversation {conversation_id} summarized ({len(response)} chars)")
        return response


summary_service = SummaryService()
