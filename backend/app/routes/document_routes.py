from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.document_schema import DocumentResponse
from app.services.document_service import document_service
from app.repositories.document_repository import document_repo
from app.services.conversation_service import conversation_service

router = APIRouter(prefix="/conversations", tags=["documents"])


@router.post("/{conversation_id}/documents", response_model=DocumentResponse, status_code=201)
def upload_document(
    conversation_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    conv = conversation_service.get(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    doc = document_service.upload_and_process(db, conversation_id, file)
    return DocumentResponse(
        id=doc.id,
        conversation_id=doc.conversation_id,
        file_name=doc.file_name,
        file_type=doc.file_type,
        file_size=doc.file_size,
        status=doc.status,
        metadata=doc.metadata_ or {},
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.get("/{conversation_id}/documents", response_model=List[DocumentResponse])
def list_documents(conversation_id: str, db: Session = Depends(get_db)):
    docs = document_repo.list_by_conversation(db, conversation_id)
    return [
        DocumentResponse(
            id=d.id,
            conversation_id=d.conversation_id,
            file_name=d.file_name,
            file_type=d.file_type,
            file_size=d.file_size,
            status=d.status,
            metadata=d.metadata_ or {},
            created_at=d.created_at,
            updated_at=d.updated_at,
        )
        for d in docs
    ]


@router.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: str, db: Session = Depends(get_db)):
    ok = document_repo.delete(db, document_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Document not found")
