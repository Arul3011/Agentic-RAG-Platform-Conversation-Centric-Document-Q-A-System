from typing import Dict, Any, List
from app.agents.rag_agent import rag_graph
from app.core.logging import get_logger

logger = get_logger(__name__)


class AgentService:
    def decide_retrieval(
        self,
        question: str,
        conversation_id: str,
        conversation_summary: str,
        recent_messages: List[Dict[str, str]],
        available_documents: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Run the LangGraph agent to decide whether/how to retrieve.
        Returns the retrieval_decision dict.
        """
        state = {
            "question": question,
            "conversation_id": conversation_id,
            "conversation_summary": conversation_summary,
            "recent_messages": recent_messages,
            "available_documents": available_documents,
            "retrieval_decision": None,
            "retrieved_chunks": [],
            "answer": None,
            "sources": [],
        }
        try:
            result = rag_graph.invoke(state)
            return result.get("retrieval_decision", {
                "requires_retrieval": True,
                "strategy": "hybrid",
                "search_query": question,
                "metadata_filters": {},
                "top_k": 10,
            })
        except Exception as e:
            logger.warning(f"Agent graph failed ({e}), using safe default")
            return {
                "requires_retrieval": True,
                "strategy": "keyword",
                "search_query": question,
                "metadata_filters": {},
                "top_k": 10,
            }


agent_service = AgentService()
