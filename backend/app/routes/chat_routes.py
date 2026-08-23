from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.chat_schema import MessageCreate, MessageResponse, ChatResponse
from app.services.chat_service import chat_service
from app.services.conversation_service import conversation_service

router = APIRouter(prefix="/conversations", tags=["chat"])


@router.post("/{conversation_id}/messages", response_model=ChatResponse, status_code=201)
def send_message(
    conversation_id: str, body: MessageCreate, db: Session = Depends(get_db)
):
    return chat_service.ask(db, conversation_id, body.content)


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
def list_messages(conversation_id: str, db: Session = Depends(get_db)):
    conv = conversation_service.get(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    msgs = conversation_service.get_messages(db, conversation_id)
    return [
        MessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            role=m.role,
            content=m.content,
            created_at=m.created_at,
            metadata=m.metadata_ or {},
        )
        for m in msgs
    ]
