import time
from typing import List
from app.integrations.gemini_client import gemini_client
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """
    Abstraction over the Gemini embedding model.
    All document chunking and query embedding flows through here.
    """

    def embed_text(self, text: str) -> List[float]:
        """Embed a single string and return the vector."""
        return gemini_client.embed_text(text)

    def embed_documents(self, chunks: List[str]) -> List[List[float]]:
        """Embed a list of chunk strings (sequential calls to Gemini)."""
        total = len(chunks)
        logger.info(f"Embedding started: {total} chunks to embed")
        embeddings = []
        start_time = time.time()
        for i, chunk in enumerate(chunks):
            logger.info(f"Embedding chunk {i+1}/{total}")
            embeddings.append(gemini_client.embed_text(chunk))
        elapsed = time.time() - start_time
        logger.info(f"Embedding complete: {total} chunks embedded in {elapsed:.2f}s")
        return embeddings


embedding_service = EmbeddingService()
