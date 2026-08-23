"""
LangGraph-based agentic retrieval decision engine.
"""
import json
import re
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.prompts import RETRIEVAL_DECISION_SYSTEM
from app.integrations.openrouter_client import openrouter_client
from app.core.logging import get_logger

logger = get_logger(__name__)

_DEFAULT_DECISION: Dict[str, Any] = {
    "requires_retrieval": True,
    "strategy": "hybrid",
    "search_query": "",
    "metadata_filters": {},
    "top_k": 10,
    "reasoning": "default fallback",
}


def _make_retrieval_decision(state: AgentState) -> AgentState:
    """Node: call OpenRouter agent model to decide retrieval strategy."""
    docs_summary = [
        {"name": d.get("file_name"), "type": d.get("file_type")}
        for d in state.get("available_documents", [])
    ]
    prompt = RETRIEVAL_DECISION_SYSTEM.format(
        documents=json.dumps(docs_summary, indent=2),
        summary=state.get("conversation_summary") or "No summary yet.",
        recent="\n".join(
            f"{m['role'].upper()}: {m['content']}"
            for m in state.get("recent_messages", [])[-6:]
        ),
        question=state["question"],
    )
    try:
        raw = openrouter_client.chat_agent(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=512,
        )
        # Extract JSON from response
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            decision = json.loads(match.group())
        else:
            decision = _DEFAULT_DECISION.copy()
            decision["search_query"] = state["question"]
    except Exception as e:
        logger.warning(f"Agent decision failed ({e}), using default")
        decision = _DEFAULT_DECISION.copy()
        decision["search_query"] = state["question"]

    if not decision.get("search_query"):
        decision["search_query"] = state["question"]

    state["retrieval_decision"] = decision
    return state


def _route_after_decision(state: AgentState) -> str:
    decision = state.get("retrieval_decision", {})
    if decision.get("requires_retrieval"):
        return "retrieve"
    return "generate"


def _no_retrieval_node(state: AgentState) -> AgentState:
    """Placeholder node when retrieval is skipped."""
    state["retrieved_chunks"] = []
    return state


def _generate_answer(state: AgentState) -> AgentState:
    """Node: generate the final answer (retrieval is handled by ChatService before this)."""
    # Actual generation is done in ChatService; this node is a pass-through.
    return state


def build_rag_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("decide", _make_retrieval_decision)
    graph.add_node("retrieve", _no_retrieval_node)   # Populated externally
    graph.add_node("generate", _generate_answer)

    graph.set_entry_point("decide")
    graph.add_conditional_edges(
        "decide",
        _route_after_decision,
        {"retrieve": "retrieve", "generate": "generate"},
    )
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    return graph.compile()


rag_graph = build_rag_graph()
