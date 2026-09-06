from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.document_schema import DocumentResponse
from app.services.document_service import document_service
from app.repositories.document_repository import document_repo
from app.services.conversation_service import conversation_service

router = APIRouter(prefix="/conversations", tags=["documents"])


def _build_response(doc) -> DocumentResponse:
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


@router.post("/{conversation_id}/documents", response_model=DocumentResponse, status_code=201)
def upload_document(
    conversation_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    conv = conversation_service.get(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    doc = document_service.start_processing(db, conversation_id, file)
    return _build_response(doc)


@router.get("/{conversation_id}/documents", response_model=List[DocumentResponse])
def list_documents(conversation_id: str, db: Session = Depends(get_db)):
    docs = document_repo.list_by_conversation(db, conversation_id)
    return [_build_response(d) for d in docs]


@router.get("/{conversation_id}/documents/{document_id}", response_model=DocumentResponse)
def get_document(conversation_id: str, document_id: str, db: Session = Depends(get_db)):
    doc = document_repo.get(db, document_id)
    if not doc or doc.conversation_id != conversation_id:
        raise HTTPException(status_code=404, detail="Document not found")
    return _build_response(doc)


@router.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: str, db: Session = Depends(get_db)):
    ok = document_repo.delete(db, document_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Document not found")
