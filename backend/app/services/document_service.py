"""
Orchestrates the complete document ingestion pipeline:
upload → extract → chunk → keywords/metadata → embed → store.

Runs the pipeline in a background thread so the API can report progress
(stage, chunk counts, percentage) while processing runs.
"""
import os
from typing import Optional
from sqlalchemy.orm import Session, sessionmaker
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

    def _update_progress(
        self,
        db: Session,
        document_id: str,
        status: str,
        step: str,
        percent: float,
        chunk_count: Optional[int] = None,
        chunk_total: Optional[int] = None,
        step_percent: Optional[float] = None,
    ):
        """Persist progress info into the document metadata JSON."""
        doc = document_repo.get(db, document_id)
        if not doc:
            return
        metadata = dict(doc.metadata_ or {})
        metadata["processing_progress"] = {
            "status": status,
            "step": step,
            "percent": round(percent, 1),
            "chunks_processed": chunk_count,
            "chunks_total": chunk_total,
            "step_percent": round(step_percent, 1) if step_percent is not None else None,
        }
        doc.metadata_ = metadata
        doc.status = status
        db.commit()

    def _run_pipeline(self, session_factory, conversation_id: str, document_id: str, file_path: str, file_name: str, file_type: str, file_size: int):
        """Execute the full processing pipeline in a background thread (own DB session)."""
        db = session_factory()
        try:
            logger.info(f"Pipeline started for document {document_id} ({file_name})")

            # Step 1: Saving file (already persisted at upload; mark progress)
            self._update_progress(db, document_id, "processing", "Saving file", 5.0)

            # Step 2: Extracting text
            self._update_progress(db, document_id, "processing", "Extracting text", 15.0)
            pages = self._extract_pages(file_path, file_type)
            full_text = " ".join(p["text"] for p in pages)
            logger.info(f"Text extracted: {len(pages)} pages, {len(full_text)} characters total")

            doc = document_repo.get(db, document_id)
            if doc:
                doc.file_size = file_size
                db.commit()

            # Step 3: Extracting metadata
            self._update_progress(db, document_id, "processing", "Extracting metadata", 30.0)
            metadata = extract_metadata(full_text, file_name, file_type)
            doc = document_repo.get(db, document_id)
            if doc:
                doc_data = dict(doc.metadata_ or {})
                doc_data.update(metadata)
                doc.metadata_ = doc_data
                db.commit()

            # Step 4: Chunking document
            self._update_progress(db, document_id, "processing", "Chunking content", 40.0)
            raw_chunks = chunk_text(pages)
            chunk_total = len(raw_chunks)
            logger.info(f"Chunking complete: {len(pages)} pages → {chunk_total} chunks")
            self._update_progress(db, document_id, "processing", "Chunking content", 55.0, 0, chunk_total, 100.0)

            # Step 5: Building chunk objects with keywords
            orm_chunks = []
            for i, raw in enumerate(raw_chunks, 1):
                keywords = extract_keywords(raw["content"])
                chunk_meta = {
                    "document_type": metadata.get("document_type", "general"),
                    "section": raw.get("section", ""),
                }
                c = DocumentChunk(
                    document_id=document_id,
                    conversation_id=conversation_id,
                    chunk_index=raw["chunk_index"],
                    content=raw["content"],
                    page_number=raw.get("page_number"),
                    section=raw.get("section", ""),
                    keywords=keywords,
                    metadata_=chunk_meta,
                )
                orm_chunks.append(c)
                if i % 10 == 0 or i == chunk_total:
                    pct = 55.0 + (i / chunk_total) * 15.0
                    self._update_progress(
                        db, document_id, "processing", "Preparing chunks",
                        pct, i, chunk_total, (i / chunk_total) * 100.0,
                    )
            logger.info(f"Built {len(orm_chunks)} ORM chunk objects")

            # Step 6: Generating embeddings
            if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
                texts = [c.content for c in orm_chunks]
                total = len(texts)
                self._update_progress(db, document_id, "processing", "Embedding content", 70.0, 0, total, 0.0)
                embeddings = []
                for i, t in enumerate(texts, 1):
                    embeddings.append(embedding_service.embed_text(t))
                    pct = 70.0 + (i / total) * 25.0
                    self._update_progress(
                        db, document_id, "processing", "Embedding content",
                        pct, i, total, (i / total) * 100.0,
                    )
                for c, emb in zip(orm_chunks, embeddings):
                    c.embedding = emb
                logger.info(f"Embeddings generated for {len(orm_chunks)} chunks")
                self._update_progress(db, document_id, "processing", "Storing chunks", 96.0, total, total, 100.0)
            else:
                logger.warning("Gemini API key not set — skipping embeddings (vector search will be unavailable)")
                self._update_progress(db, document_id, "processing", "Storing chunks", 96.0, chunk_total, chunk_total, 100.0)

            chunk_repo.bulk_create(db, orm_chunks)
            logger.info(f"Stored {len(orm_chunks)} chunks in database")

            self._update_progress(db, document_id, "ready", "Complete", 100.0, chunk_total, chunk_total, 100.0)
            logger.info(f"Pipeline complete for document {document_id}: {chunk_total} chunks processed successfully")
        except HTTPException:
            self._update_progress(db, document_id, "error", "Failed", 100.0)
            logger.exception("Document processing failed (HTTP)")
        except Exception as e:
            self._update_progress(db, document_id, "error", "Failed", 100.0)
            logger.error(f"Document processing failed: {e}", exc_info=True)
            raise
        finally:
            db.close()

    def start_processing(self, db: Session, conversation_id: str, file: UploadFile) -> object:
        """
        Persist the document as 'pending', save the file to disk, then kick
        off the pipeline in a background thread. Returns the created Document.
        """
        file_type = self._validate_file(file)
        doc = document_repo.create(
            db=db,
            conversation_id=conversation_id,
            file_name=file.filename or "unknown",
            file_type=file_type,
            file_size=0,
            storage_path="",
        )

        path, size = self._save_file_safely(db, doc, file)

        session_factory = sessionmaker(bind=db.bind, autocommit=False, autoflush=False)
        import threading
        threading.Thread(
            target=self._run_pipeline,
            args=(session_factory, conversation_id, doc.id, path, doc.file_name, file_type, size),
            daemon=True,
        ).start()
        return doc

    def _save_file_safely(self, db: Session, doc, file: UploadFile) -> tuple[str, int]:
        try:
            path, size = self._save_file(file, doc.id, doc.file_type)
            db_doc = document_repo.get(db, doc.id)
            if db_doc:
                db_doc.storage_path = path
                db_doc.file_size = size
                db_doc.status = "processing"
                db.commit()
            return path, size
        except HTTPException:
            document_repo.update_status(db, doc.id, "error")
            raise
        except Exception:
            document_repo.update_status(db, doc.id, "error")
            raise


document_service = DocumentService()
