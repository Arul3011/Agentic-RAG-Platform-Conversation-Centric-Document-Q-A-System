from pydantic import BaseModel, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = {}

    @model_validator(mode="before")
    @classmethod
    def coerce_metadata(cls, data: Any) -> Any:
        # ORM object: read metadata_ attribute, not the SQLAlchemy MetaData object
        if hasattr(data, "__dict__"):
            raw = getattr(data, "metadata_", None)
            return {
                "id": data.id,
                "conversation_id": data.conversation_id,
                "role": data.role,
                "content": data.content,
                "created_at": data.created_at,
                "metadata": raw if isinstance(raw, dict) else {},
            }
        # Plain dict path — just sanitise the metadata key
        if isinstance(data, dict):
            meta = data.get("metadata", {})
            if not isinstance(meta, dict):
                data["metadata"] = {}
        return data

    model_config = {"from_attributes": True}


class SourceInfo(BaseModel):
    document_id: str
    document_name: str
    chunk_id: str
    page_number: Optional[int] = None
    similarity_score: Optional[float] = None
    retrieval_strategy: str


class ChatResponse(BaseModel):
    message: MessageResponse
    sources: List[SourceInfo] = []
    retrieval: Dict[str, Any] = {"used": False, "strategy": "none"}
