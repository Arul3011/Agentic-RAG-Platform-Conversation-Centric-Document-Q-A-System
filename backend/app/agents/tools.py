"""
LangGraph tool definitions for the RAG agent.
"""
from typing import List, Dict, Any
from langchain_core.tools import tool
from app.core.logging import get_logger

logger = get_logger(__name__)


@tool
def vector_search_tool(query: str, conversation_id: str, top_k: int = 10) -> str:
    """Perform semantic vector similarity search on document chunks."""
    return f"vector_search:{query}:{conversation_id}:{top_k}"


@tool
def keyword_search_tool(query: str, conversation_id: str, top_k: int = 10) -> str:
    """Perform keyword full-text search on document chunks."""
    return f"keyword_search:{query}:{conversation_id}:{top_k}"


@tool
def metadata_filter_tool(filters: Dict[str, Any], conversation_id: str, top_k: int = 10) -> str:
    """Filter document chunks by metadata fields."""
    return f"metadata_filter:{filters}:{conversation_id}:{top_k}"


@tool
def hybrid_search_tool(
    query: str,
    conversation_id: str,
    metadata_filters: Dict[str, Any] = None,
    top_k: int = 10,
) -> str:
    """Perform hybrid retrieval combining vector, keyword, and metadata search."""
    return f"hybrid_search:{query}:{conversation_id}:{metadata_filters}:{top_k}"
