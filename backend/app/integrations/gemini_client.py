"""
Gemini integration — wraps google-genai SDK.
The SDK reads GOOGLE_API_KEY from environment (set in core/config.py).
"""
from typing import List
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class GeminiClient:
    """Thin wrapper around google-genai for embedding generation."""

    def __init__(self):
        self._client = None
        self.model = settings.GEMINI_EMBEDDING_MODEL

    def _get_client(self):
        if self._client is None:
            try:
                from google import genai  # noqa: import inside method
                self._client = genai.Client()
            except Exception as e:
                raise RuntimeError(
                    f"Could not initialise google-genai client: {e}. "
                    "Ensure GEMINI_API_KEY is set in .env"
                ) from e
        return self._client

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        client = self._get_client()
        result = client.models.embed_content(
            model=self.model,
            contents=text,
        )
        embedding = result.embeddings[0].values
        logger.debug(f"Embedded text ({len(text)} chars) → {len(embedding)}-dim vector")
        return list(embedding)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of texts (calls embed_text sequentially; Gemini doesn't support true batch yet)."""
        return [self.embed_text(t) for t in texts]


gemini_client = GeminiClient()
