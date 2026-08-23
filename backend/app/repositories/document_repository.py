from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.document import Document


class DocumentRepository:
    def create(
        self,
        db: Session,
        conversation_id: str,
        file_name: str,
        file_type: str,
        file_size: int,
        storage_path: str,
        metadata: dict = None,
    ) -> Document:
        doc = Document(
            conversation_id=conversation_id,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            storage_path=storage_path,
            status="pending",
            metadata_=metadata or {},
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    def get(self, db: Session, document_id: str) -> Optional[Document]:
        return db.query(Document).filter(Document.id == document_id).first()

    def list_by_conversation(self, db: Session, conversation_id: str) -> List[Document]:
        return (
            db.query(Document)
            .filter(Document.conversation_id == conversation_id)
            .order_by(Document.created_at.asc())
            .all()
        )

    def update_status(self, db: Session, document_id: str, status: str) -> Optional[Document]:
        doc = self.get(db, document_id)
        if doc:
            doc.status = status
            db.commit()
            db.refresh(doc)
        return doc

    def delete(self, db: Session, document_id: str) -> bool:
        doc = self.get(db, document_id)
        if doc:
            db.delete(doc)
            db.commit()
            return True
        return False


document_repo = DocumentRepository()
