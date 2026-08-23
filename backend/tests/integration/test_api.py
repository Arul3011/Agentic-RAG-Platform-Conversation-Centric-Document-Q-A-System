"""
Integration tests — run against real PostgreSQL with test DB.
Uses TestClient (sync) so no async pytest-asyncio needed.
"""
import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db
from app.core.config import settings

# Use a separate test database
TEST_DB_URL = settings.DATABASE_URL.replace("/agentic_rag", "/agentic_rag_test")

test_engine = create_engine(TEST_DB_URL)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    with test_engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    return TestClient(app)


# ── Conversation CRUD ───────────────────────────────────────────────────────

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_conversation(client):
    r = client.post("/api/v1/conversations", json={"title": "Test Chat"})
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Test Chat"
    assert "id" in data
    return data["id"]


def test_list_conversations(client):
    client.post("/api/v1/conversations", json={"title": "ListTest"})
    r = client.get("/api/v1/conversations")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1


def test_get_conversation(client):
    create_r = client.post("/api/v1/conversations", json={"title": "GetMe"})
    conv_id = create_r.json()["id"]
    r = client.get(f"/api/v1/conversations/{conv_id}")
    assert r.status_code == 200
    assert r.json()["id"] == conv_id


def test_get_conversation_not_found(client):
    r = client.get("/api/v1/conversations/nonexistent-id")
    assert r.status_code == 404


# ── Messages ────────────────────────────────────────────────────────────────

def test_send_message_no_openrouter(client):
    """Without API keys, message still persists with stub answer."""
    create_r = client.post("/api/v1/conversations", json={"title": "MsgTest"})
    conv_id = create_r.json()["id"]
    r = client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        json={"content": "Hello, what is 2+2?"},
    )
    assert r.status_code == 201
    data = r.json()
    assert "message" in data
    assert data["message"]["role"] == "assistant"
    assert data["message"]["conversation_id"] == conv_id


def test_list_messages(client):
    create_r = client.post("/api/v1/conversations", json={"title": "MsgList"})
    conv_id = create_r.json()["id"]
    client.post(f"/api/v1/conversations/{conv_id}/messages", json={"content": "Hi"})
    r = client.get(f"/api/v1/conversations/{conv_id}/messages")
    assert r.status_code == 200
    msgs = r.json()
    # user + assistant
    assert len(msgs) >= 2


# ── Documents ───────────────────────────────────────────────────────────────

def test_upload_txt_document(client):
    create_r = client.post("/api/v1/conversations", json={"title": "DocTest"})
    conv_id = create_r.json()["id"]

    content = b"This is a test document about authentication and JWT tokens."
    r = client.post(
        f"/api/v1/conversations/{conv_id}/documents",
        files={"file": ("test.txt", io.BytesIO(content), "text/plain")},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["conversation_id"] == conv_id
    assert data["file_name"] == "test.txt"
    # Status may be 'ready' (no embed) or 'error' — just not 'pending'
    assert data["status"] in ("ready", "processing", "error")


def test_list_documents(client):
    create_r = client.post("/api/v1/conversations", json={"title": "DocList"})
    conv_id = create_r.json()["id"]

    content = b"Document content for listing test."
    client.post(
        f"/api/v1/conversations/{conv_id}/documents",
        files={"file": ("list.txt", io.BytesIO(content), "text/plain")},
    )
    r = client.get(f"/api/v1/conversations/{conv_id}/documents")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_upload_to_nonexistent_conversation(client):
    content = b"some content"
    r = client.post(
        "/api/v1/conversations/bad-id/documents",
        files={"file": ("x.txt", io.BytesIO(content), "text/plain")},
    )
    assert r.status_code == 404


def test_message_in_nonexistent_conversation(client):
    r = client.post(
        "/api/v1/conversations/fake-conv/messages",
        json={"content": "Hello"},
    )
    assert r.status_code == 404


# ── Multi-document retrieval ─────────────────────────────────────────────────

def test_multi_document_conversation(client):
    """Upload multiple docs to same conversation, then ask."""
    create_r = client.post("/api/v1/conversations", json={"title": "MultiDoc"})
    conv_id = create_r.json()["id"]

    for i, text_content in enumerate(
        [b"Document one about security policies.", b"Document two about API rate limiting."]
    ):
        client.post(
            f"/api/v1/conversations/{conv_id}/documents",
            files={"file": (f"doc{i}.txt", io.BytesIO(text_content), "text/plain")},
        )

    docs_r = client.get(f"/api/v1/conversations/{conv_id}/documents")
    assert len(docs_r.json()) == 2

    msg_r = client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        json={"content": "What does the documentation cover?"},
    )
    assert msg_r.status_code == 201
