"""
Orchestrates the full RAG question-answering pipeline:
load context → agent decision → retrieval → build prompt → generate answer → persist.
"""
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.config import settings
from app.core.logging import get_logger
from app.repositories.conversation_repository import conversation_repo
from app.repositories.message_repository import message_repo
from app.repositories.document_repository import document_repo
from app.repositories.retrieval_repository import retrieval_repo
from app.services.agent_service import agent_service
from app.services.retrieval_service import retrieval_service
from app.services.summary_service import summary_service
from app.integrations.openrouter_client import openrouter_client
from app.agents.prompts import ANSWER_GENERATION_SYSTEM
from app.models.chunk import DocumentChunk
from app.schemas.chat_schema import SourceInfo

logger = get_logger(__name__)


class ChatService:
    def ask(
        self, db: Session, conversation_id: str, question: str
    ) -> Dict[str, Any]:
        # 1. Validate conversation
        conv = conversation_repo.get(db, conversation_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # 2. Load context
        recent_msgs = message_repo.get_recent(db, conversation_id, settings.MAX_HISTORY_MESSAGES)
        recent_for_agent = [{"role": m.role, "content": m.content} for m in recent_msgs]
        docs = document_repo.list_by_conversation(db, conversation_id)
        docs_info = [{"file_name": d.file_name, "file_type": d.file_type, "id": d.id} for d in docs]

        # 3. Agent decides retrieval strategy
        decision = agent_service.decide_retrieval(
            question=question,
            conversation_id=conversation_id,
            conversation_summary=conv.summary or "",
            recent_messages=recent_for_agent,
            available_documents=docs_info,
        )
        logger.info(f"Agent decision: {decision}")

        # 4. Execute retrieval if required
        retrieved: List[Tuple[DocumentChunk, float]] = []
        if decision.get("requires_retrieval") and docs:
            retrieved = retrieval_service.retrieve(
                db=db,
                conversation_id=conversation_id,
                strategy=decision.get("strategy", "hybrid"),
                query=decision.get("search_query", question),
                metadata_filters=decision.get("metadata_filters", {}),
                top_k=decision.get("top_k", settings.TOP_K),
            )
            retrieved = retrieved[: settings.FINAL_CONTEXT_K]

        # 5. Build context string
        context_parts = []
        sources: List[SourceInfo] = []
        doc_name_map = {d.id: d.file_name for d in docs}

        for chunk, score in retrieved:
            context_parts.append(
                f"[Source: {doc_name_map.get(chunk.document_id, 'Unknown')}, "
                f"Page {chunk.page_number}]\n{chunk.content}"
            )
            sources.append(
                SourceInfo(
                    document_id=chunk.document_id,
                    document_name=doc_name_map.get(chunk.document_id, "Unknown"),
                    chunk_id=chunk.id,
                    page_number=chunk.page_number,
                    similarity_score=score,
                    retrieval_strategy=decision.get("strategy", "none"),
                )
            )

        context_str = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant documents found."

        # 6. Build LLM message list
        system_msg = ANSWER_GENERATION_SYSTEM.format(
            summary=conv.summary or "No summary yet.",
            context=context_str,
        )
        llm_messages: List[Dict[str, str]] = [{"role": "system", "content": system_msg}]
        for m in recent_msgs[-8:]:
            llm_messages.append({"role": m.role, "content": m.content})
        llm_messages.append({"role": "user", "content": question})

        # 7. Generate answer
        if settings.OPENROUTER_API_KEY and settings.OPENROUTER_API_KEY != "YOUR_OPENROUTER_API_KEY_HERE":
            answer = openrouter_client.chat(llm_messages, temperature=0.4, max_tokens=2048)
        else:
            answer = (
                "[OpenRouter not configured] I received your question: "
                f'"{question}". Please set OPENROUTER_API_KEY in .env to get AI-generated answers.'
            )

        # 8. Persist messages
        user_msg = message_repo.create(db, conversation_id, "user", question)
        ai_msg = message_repo.create(db, conversation_id, "assistant", answer, {
            "retrieval_strategy": decision.get("strategy", "none"),
            "sources_count": len(sources),
        })

        # 9. Log retrieval
        if retrieved:
            retrieval_repo.log(
                db=db,
                conversation_id=conversation_id,
                message_id=ai_msg.id,
                strategy=decision.get("strategy", "none"),
                search_query=decision.get("search_query", question),
                metadata_filters=decision.get("metadata_filters", {}),
                top_k=decision.get("top_k", settings.TOP_K),
                retrieved_chunk_ids=[c.id for c, _ in retrieved],
            )

        # 10. Trigger summarization if threshold reached
        if summary_service.should_summarize(db, conversation_id):
            all_msgs = message_repo.list_by_conversation(db, conversation_id, limit=200)
            summary_service.summarize(db, conversation_id, all_msgs)

        return {
            "message": ai_msg,
            "sources": sources,
            "retrieval": {
                "used": bool(retrieved),
                "strategy": decision.get("strategy", "none"),
                "decision": decision,
            },
        }


chat_service = ChatService()
