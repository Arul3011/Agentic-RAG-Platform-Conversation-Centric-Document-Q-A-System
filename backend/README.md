# Agentic RAG — Backend

Conversation-centric Agentic RAG platform built with FastAPI, PostgreSQL/pgvector, Google Gemini embeddings, and OpenRouter LLMs.

## Architecture

```
React UI → FastAPI Routes → Services → Repositories → PostgreSQL + pgvector
                                  ↓
                          LangGraph Agent (retrieval decision)
                                  ↓
                     Vector / Keyword / Metadata / Hybrid retrieval
                                  ↓
                         OpenRouter LLM (answer generation)
```

## Quick Start

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 14+ with pgvector extension
- Google Gemini API key (AI Studio)
- OpenRouter API key

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your actual keys:
#   GEMINI_API_KEY=...
#   OPENROUTER_API_KEY=...
#   POSTGRES_PASSWORD=...
```

### 4. Set up PostgreSQL

```sql
CREATE DATABASE agentic_rag;
CREATE EXTENSION vector;
```

### 5. Run the server

```bash
uvicorn app.main:app --reload --port 8000
```

API available at: http://localhost:8000  
Docs at: http://localhost:8000/docs

---

## Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/conversations` | Create a conversation |
| GET | `/api/v1/conversations` | List conversations |
| POST | `/api/v1/conversations/{id}/messages` | Send a message (triggers RAG pipeline) |
| GET | `/api/v1/conversations/{id}/messages` | Get conversation history |
| POST | `/api/v1/conversations/{id}/documents` | Upload a document |
| GET | `/api/v1/conversations/{id}/documents` | List documents in conversation |
| DELETE | `/api/v1/documents/{id}` | Delete a document |

---

## Agentic Retrieval Flow

```
Question
  ↓
LangGraph Agent (OpenRouter)
  ↓ decides:
  ├── requires_retrieval: false → skip to LLM
  └── requires_retrieval: true
        ├── strategy: vector   → Gemini embedding + pgvector cosine search
        ├── strategy: keyword  → PostgreSQL full-text search
        ├── strategy: metadata → JSONB filter
        └── strategy: hybrid   → all three + RRF reranking
              ↓
         Retrieved chunks → OpenRouter LLM → Answer + Sources
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google AI Studio key — used for `gemini-embedding-2` |
| `GEMINI_EMBEDDING_MODEL` | Embedding model (default: `gemini-embedding-2`) |
| `VECTOR_DIMENSION` | Must match embedding model output (3072 for gemini-embedding-2) |
| `OPENROUTER_API_KEY` | OpenRouter key for all LLM calls |
| `OPENROUTER_MODEL` | Answer generation model |
| `OPENROUTER_AGENT_MODEL` | Retrieval decision model (can be smaller/cheaper) |
| `OPENROUTER_SUMMARY_MODEL` | Conversation summarization model |
| `DATABASE_URL` | PostgreSQL connection string |
| `CHUNK_SIZE` | Characters per chunk (default: 700) |
| `CHUNK_OVERLAP` | Overlap between chunks (default: 100) |
| `TOP_K` | Chunks fetched per retrieval strategy (default: 10) |
| `FINAL_CONTEXT_K` | Chunks passed to LLM after reranking (default: 5) |

---

## Recommended Free OpenRouter Models

```env
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
OPENROUTER_AGENT_MODEL=meta-llama/llama-3.1-8b-instruct:free
OPENROUTER_SUMMARY_MODEL=meta-llama/llama-3.1-8b-instruct:free
```

Check https://openrouter.ai/models?supported_parameters=free for currently available free models.

---

## Running Tests

```bash
# Unit tests only (no DB required)
pytest tests/unit/ -v

# All tests (requires PostgreSQL)
pytest tests/ -v
```

---

## Folder Structure

```
backend/
├── app/
│   ├── main.py                        # FastAPI app + lifespan
│   ├── core/
│   │   ├── config.py                  # pydantic-settings from .env
│   │   └── logging.py
│   ├── routes/                        # HTTP layer only
│   │   ├── conversation_routes.py
│   │   ├── chat_routes.py
│   │   └── document_routes.py
│   ├── services/                      # Business logic
│   │   ├── chat_service.py            # Main RAG orchestrator
│   │   ├── document_service.py        # Ingestion pipeline
│   │   ├── embedding_service.py       # Gemini wrapper
│   │   ├── agent_service.py           # LangGraph runner
│   │   ├── retrieval_service.py       # Strategy dispatcher
│   │   ├── summary_service.py         # Conversation summarizer
│   │   └── conversation_service.py
│   ├── repositories/                  # DB access layer
│   ├── agents/                        # LangGraph graph + prompts
│   ├── retrieval/                     # Retrieval strategies + reranker
│   ├── document_processing/           # Extractors, chunker, keywords
│   ├── integrations/                  # gemini_client, openrouter_client
│   ├── models/                        # SQLAlchemy ORM models
│   ├── schemas/                       # Pydantic request/response schemas
│   └── db/                            # Engine, session, init_db
├── tests/
│   ├── unit/                          # Pure logic, no DB
│   └── integration/                   # Real PostgreSQL + TestClient
├── .env                               # Never commit
├── .env.example                       # Safe to commit
└── requirements.txt
