from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.conversation_schema import ConversationCreate, ConversationResponse
from app.services.conversation_service import conversation_service

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse, status_code=201)
def create_conversation(body: ConversationCreate, db: Session = Depends(get_db)):
    conv = conversation_service.create(db, body.title or "New Conversation")
    return conv


@router.get("", response_model=List[ConversationResponse])
def list_conversations(db: Session = Depends(get_db)):
    return conversation_service.list_all(db)


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conv = conversation_service.get(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    ok = conversation_service.delete(db, conversation_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Conversation not found")
