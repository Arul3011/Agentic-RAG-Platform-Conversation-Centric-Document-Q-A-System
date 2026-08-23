"""
Agent evaluation tests — verify retrieval decision logic
using mocked OpenRouter responses.
"""
import json
import pytest
from unittest.mock import patch, MagicMock
from app.services.agent_service import agent_service


MOCK_DOCS = [
    {"file_name": "security.pdf", "file_type": "pdf", "id": "doc-1"},
    {"file_name": "api.pdf", "file_type": "pdf", "id": "doc-2"},
]


def _mock_openrouter(decision: dict):
    """Return a mock that produces the given JSON decision."""
    mock = MagicMock()
    mock.return_value = json.dumps(decision)
    return mock


# ── Test cases from spec §34 ─────────────────────────────────────────────────

@pytest.mark.parametrize("question,expected_retrieval,expected_strategy", [
    # Factual questions requiring retrieval
    ("What is the maximum JWT expiration time?", True, "keyword"),
    ("What security protocols does the API support?", True, "vector"),
    ("Show me all authentication-related sections", True, "metadata"),
    # Conversational follow-ups that may skip retrieval
    ("Can you explain that more simply?", False, "none"),
    ("Thank you!", False, "none"),
])
def test_agent_decision_cases(question, expected_retrieval, expected_strategy):
    """Verify that agent returns correct structure for known question types."""
    decision_response = {
        "requires_retrieval": expected_retrieval,
        "strategy": expected_strategy,
        "search_query": question if expected_retrieval else "",
        "metadata_filters": {},
        "top_k": 10,
        "reasoning": "test case",
    }

    with patch(
        "app.integrations.openrouter_client.openrouter_client.chat_agent",
        return_value=json.dumps(decision_response),
    ):
        result = agent_service.decide_retrieval(
            question=question,
            conversation_id="test-conv",
            conversation_summary="User is asking about API security.",
            recent_messages=[{"role": "user", "content": "Tell me about JWT"}],
            available_documents=MOCK_DOCS,
        )

    assert "requires_retrieval" in result
    assert "strategy" in result
    assert "search_query" in result
    assert isinstance(result["requires_retrieval"], bool)


def test_agent_falls_back_on_error():
    """Agent must not crash when OpenRouter is unavailable."""
    with patch(
        "app.integrations.openrouter_client.openrouter_client.chat_agent",
        side_effect=Exception("API unreachable"),
    ):
        result = agent_service.decide_retrieval(
            question="What are the rate limits?",
            conversation_id="test-conv",
            conversation_summary="",
            recent_messages=[],
            available_documents=MOCK_DOCS,
        )

    # Must still return a valid decision
    assert "requires_retrieval" in result
    assert "strategy" in result


def test_agent_decision_structure():
    """Returned decision must have all required keys."""
    required_keys = {"requires_retrieval", "strategy", "search_query", "metadata_filters", "top_k"}
    with patch(
        "app.integrations.openrouter_client.openrouter_client.chat_agent",
        return_value='{"requires_retrieval": true, "strategy": "hybrid", '
                     '"search_query": "test", "metadata_filters": {}, "top_k": 10}',
    ):
        result = agent_service.decide_retrieval(
            question="test",
            conversation_id="c",
            conversation_summary="",
            recent_messages=[],
            available_documents=[],
        )
    assert required_keys.issubset(result.keys())
