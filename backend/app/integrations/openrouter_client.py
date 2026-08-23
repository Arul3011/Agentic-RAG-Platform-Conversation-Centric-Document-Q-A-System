"""
OpenRouter integration — uses openai SDK pointed at OpenRouter base URL.
Never exposes API key to the frontend.
"""
from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenRouterClient:
    """Unified client for all OpenRouter LLM calls."""

    def __init__(self):
        self._client: Optional[OpenAI] = None

    def _get_client(self) -> OpenAI:
        if self._client is None:
            if not settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEY == "YOUR_OPENROUTER_API_KEY_HERE":
                raise RuntimeError("OPENROUTER_API_KEY not configured in .env")
            self._client = OpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL,
            )
        return self._client

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        response_format: Optional[Dict] = None,
    ) -> str:
        """Send a chat completion request, return content string."""
        client = self._get_client()
        model = model or settings.OPENROUTER_MODEL
        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format
        logger.debug(f"OpenRouter request → model={model}, msgs={len(messages)}")
        response = client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content or ""
        logger.debug(f"OpenRouter response ({len(content)} chars)")
        return content

    def chat_agent(self, messages: List[Dict[str, str]], **kwargs) -> str:
        return self.chat(messages, model=settings.OPENROUTER_AGENT_MODEL, **kwargs)

    def chat_summary(self, messages: List[Dict[str, str]], **kwargs) -> str:
        return self.chat(messages, model=settings.OPENROUTER_SUMMARY_MODEL, **kwargs)


openrouter_client = OpenRouterClient()
