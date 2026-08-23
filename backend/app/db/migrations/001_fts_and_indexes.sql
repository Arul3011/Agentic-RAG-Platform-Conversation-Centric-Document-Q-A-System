-- Full-text search support for document_chunks (keyword retrieval)
ALTER TABLE document_chunks
    ADD COLUMN IF NOT EXISTS content_tsv tsvector
    GENERATED ALWAYS AS (to_tsvector('english', coalesce(content, ''))) STORED;

CREATE INDEX IF NOT EXISTS ix_document_chunks_content_tsv
    ON document_chunks USING GIN (content_tsv);

-- Keyword array search support
CREATE INDEX IF NOT EXISTS ix_document_chunks_keywords
    ON document_chunks USING GIN (keywords);

-- Metadata JSONB filtering support
CREATE INDEX IF NOT EXISTS ix_document_chunks_metadata
    ON document_chunks USING GIN (chunk_metadata);

CREATE INDEX IF NOT EXISTS ix_documents_metadata
    ON documents USING GIN (document_metadata);

-- Vector similarity index (HNSW, cosine distance)
CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw
    ON document_chunks USING hnsw (embedding vector_cosine_ops);
