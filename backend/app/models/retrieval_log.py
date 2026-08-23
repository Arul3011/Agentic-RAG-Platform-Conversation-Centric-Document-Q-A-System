from sqlalchemy import Column, String, Text, DateTime, func, JSON, Integer
from sqlalchemy import ForeignKey
from app.db.database import Base
import uuid


class RetrievalLog(Base):
    __tablename__ = "retrieval_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(String, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    strategy = Column(String(50), nullable=False)
    search_query = Column(Text, nullable=True)
    metadata_filters = Column(JSON, default=dict)
    top_k = Column(Integer, nullable=False, default=10)
    retrieved_chunks = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
