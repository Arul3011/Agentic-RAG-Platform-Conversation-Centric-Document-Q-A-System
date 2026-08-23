"""
Orchestrates the complete document ingestion pipeline:
upload → extract → chunk → keywords/metadata → embed → store.
"""
import os
import shutil
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException

from app.core.config import settings
from app.core.logging import get_logger
from app.repositories.document_repository import document_repo
from app.repositories.chunk_repository import chunk_repo
from app.models.chunk import DocumentChunk
from app.document_processing.chunker import chunk_text
from app.document_processing.keyword_extractor import extract_keywords
from app.document_processing.metadata_extractor import extract_metadata
from app.document_processing.extractors.pdf_extractor import extract_pdf
from app.document_processing.extractors.docx_extractor import extract_docx
from app.document_processing.extractors.text_extractor import extract_text
from app.services.embedding_service import embedding_service

logger = get_logger(__name__)

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
    "text/markdown": "md",
}


class DocumentService:
    def _ensure_upload_dir(self):
        os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)

    def _validate_file(self, file: UploadFile) -> str:
        content_type = file.content_type or ""
        if content_type not in ALLOWED_TYPES:
            # fallback: detect by extension
            ext = os.path.splitext(file.filename or "")[1].lower()
            ext_map = {".pdf": "pdf", ".docx": "docx", ".txt": "txt", ".md": "md"}
            if ext not in ext_map:
                raise HTTPException(
                    status_code=415,
                    detail=f"Unsupported file type: {content_type}. Allowed: PDF, DOCX, TXT, MD",
                )
            return ext_map[ext]
        return ALLOWED_TYPES[content_type]

    def _save_file(self, file: UploadFile, document_id: str, file_ext: str) -> tuple[str, int]:
        self._ensure_upload_dir()
        filename = f"{document_id}.{file_ext}"
        path = os.path.join(settings.UPLOAD_DIRECTORY, filename)
        size = 0
        with open(path, "wb") as out:
            while chunk := file.file.read(1024 * 64):
                size += len(chunk)
                if size > settings.max_file_size_bytes:
                    os.remove(path)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File exceeds maximum size of {settings.MAX_FILE_SIZE_MB}MB",
                    )
                out.write(chunk)
        return path, size

    def _extract_pages(self, path: str, file_type: str):
        if file_type == "pdf":
            return extract_pdf(path)
        elif file_type == "docx":
            return extract_docx(path)
        else:
            return extract_text(path)

    def upload_and_process(
        self,
        db: Session,
        conversation_id: str,
        file: UploadFile,
        embed: bool = True,
    ):
        """
        Full pipeline: save → extract → chunk → embed → store.
        Returns the created Document ORM object.
        """
        file_type = self._validate_file(file)
        # Create DB record first to get an ID
        doc = document_repo.create(
            db=db,
            conversation_id=conversation_id,
            file_name=file.filename or "unknown",
            file_type=file_type,
            file_size=0,
            storage_path="",
        )
        try:
            logger.info(f"Pipeline started for document {doc.id} ({file.filename})")

            logger.info("Step 1/6: Saving file to disk...")
            path, size = self._save_file(file, doc.id, file_type)
            doc.storage_path = path
            doc.file_size = size
            db.commit()
            logger.info(f"File saved: {path} ({size} bytes)")

            document_repo.update_status(db, doc.id, "processing")

            logger.info("Step 2/6: Extracting text...")
            pages = self._extract_pages(path, file_type)
            full_text = " ".join(p["text"] for p in pages)
            logger.info(f"Text extracted: {len(pages)} pages, {len(full_text)} characters total")

            logger.info("Step 3/6: Extracting metadata...")
            metadata = extract_metadata(full_text, file.filename or "", file_type)
            doc.metadata_ = metadata
            db.commit()
            logger.info(f"Metadata extracted: type={metadata.get('document_type', 'unknown')}")

            logger.info("Step 4/6: Chunking document...")
            raw_chunks = chunk_text(pages)

            logger.info("Step 5/6: Building chunk objects with keywords...")
            orm_chunks = []
            for raw in raw_chunks:
                keywords = extract_keywords(raw["content"])
                chunk_meta = {
                    "document_type": metadata.get("document_type", "general"),
                    "section": raw.get("section", ""),
                }
                c = DocumentChunk(
                    document_id=doc.id,
                    conversation_id=conversation_id,
                    chunk_index=raw["chunk_index"],
                    content=raw["content"],
                    page_number=raw.get("page_number"),
                    section=raw.get("section", ""),
                    keywords=keywords,
                    metadata_=chunk_meta,
                )
                orm_chunks.append(c)
            logger.info(f"Built {len(orm_chunks)} ORM chunk objects")

            logger.info("Step 6/6: Generating embeddings...")
            if embed and settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
                texts = [c.content for c in orm_chunks]
                embeddings = embedding_service.embed_documents(texts)
                for c, emb in zip(orm_chunks, embeddings):
                    c.embedding = emb
                logger.info(f"Embeddings generated for {len(orm_chunks)} chunks")
            else:
                logger.warning("Gemini API key not set — skipping embeddings (vector search will be unavailable)")

            chunk_repo.bulk_create(db, orm_chunks)
            logger.info(f"Stored {len(orm_chunks)} chunks in database")

            document_repo.update_status(db, doc.id, "ready")
            logger.info(f"Pipeline complete for document {doc.id}: {len(orm_chunks)} chunks processed successfully")
            return doc

        except HTTPException:
            document_repo.update_status(db, doc.id, "error")
            raise
        except Exception as e:
            document_repo.update_status(db, doc.id, "error")
            logger.error(f"Document processing failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")


document_service = DocumentService()
