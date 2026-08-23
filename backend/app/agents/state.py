from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    question: str
    conversation_id: str
    conversation_summary: Optional[str]
    recent_messages: List[Dict[str, str]]
    available_documents: List[Dict[str, Any]]
    retrieval_decision: Optional[Dict[str, Any]]
    retrieved_chunks: List[Dict[str, Any]]
    answer: Optional[str]
    sources: List[Dict[str, Any]]
