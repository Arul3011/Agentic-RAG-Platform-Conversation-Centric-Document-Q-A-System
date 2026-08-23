# 🤖 Agentic RAG — Intelligent Document Q&A Platform

A full-stack **Agentic Retrieval-Augmented Generation (RAG)** application that lets you upload documents into conversations and ask questions against them. Unlike traditional RAG systems that blindly run vector search for every query, this platform uses an **AI agent** to intelligently decide *whether* to retrieve and *which retrieval strategy* to use.

---

## What Is This Application?

Agentic RAG is a **conversation-centric knowledge platform**. You create a conversation, upload your documents (PDFs, Word files, text files), and then chat with an AI that answers questions using the content of those documents as its knowledge base.

The key difference from a basic chatbot or simple RAG system:

| Feature | Basic Chatbot | Simple RAG | **Agentic RAG** |
|---------|--------------|-----------|-----------------|
| Uses your documents | ❌ | ✅ | ✅ |
| Decides *if* retrieval is needed | ❌ | ❌ | ✅ |
| Chooses retrieval strategy | ❌ | ❌ | ✅ |
| Multiple retrieval methods | ❌ | ❌ | ✅ |
| Shows sources + pages | ❌ | Partial | ✅ |
| Conversation memory | ❌ | ❌ | ✅ |

---

## How It Works

### The Big Picture

```
You upload documents
        ↓
Text is extracted → split into chunks → embedded into vectors → stored in PostgreSQL
        ↓
You ask a question
        ↓
AI Agent analyses the question + conversation history
        ↓
Agent decides: Does this need retrieval? Which strategy?
        ↓
Relevant chunks are fetched from the database
        ↓
AI generates an answer using those chunks as context
        ↓
Answer is returned with source citations (document name, page number)
```

---

### Step-by-Step Flow

#### 1. Document Ingestion

When you upload a document:

```
PDF / DOCX / TXT / MD
        ↓
Text Extraction
        ↓
Split into 700-character overlapping chunks
        ↓
Keywords extracted from each chunk
        ↓
Metadata detected (document type, version, date)
        ↓
Google Gemini generates a vector embedding for each chunk
        ↓
Chunks + embeddings stored in PostgreSQL with pgvector
        ↓
Document status → READY
```

#### 2. Agentic Retrieval Decision

When you send a message, an AI agent (powered by OpenRouter) first analyses your question:

```
"What is the maximum JWT expiration time?"
        ↓
Agent sees: question is specific, technical, needs exact info
        ↓
Agent decides:
{
  "requires_retrieval": true,
  "strategy": "keyword",
  "search_query": "JWT expiration maximum",
  "top_k": 10
}
```

```
"Can you explain that more simply?"
        ↓
Agent sees: follow-up question, answer is in conversation history
        ↓
Agent decides:
{
  "requires_retrieval": false,
  "strategy": "none"
}
```

#### 3. Four Retrieval Strategies

| Strategy | How It Works | Best For |
|----------|-------------|----------|
| **Vector** | Cosine similarity on Gemini embeddings | Conceptual, meaning-based questions |
| **Keyword** | PostgreSQL full-text search | Specific terms, names, codes |
| **Metadata** | JSONB filter on document properties | Filtering by doc type or section |
| **Hybrid** | All three combined + RRF reranking | Complex, multi-faceted questions |

#### 4. Answer Generation

```
System prompt
+ Conversation summary (compressed history)
+ Recent messages
+ Retrieved document chunks (with source labels)
+ Your question
        ↓
OpenRouter LLM generates answer
        ↓
Answer + source citations returned to UI
```

#### 5. Conversation Memory

Long conversations are automatically summarised so the LLM context stays efficient:

```
After every 20 messages:
Old messages → OpenRouter summary model → Compact summary
                                                ↓
                              Stored in conversations.summary
                                                ↓
                    Future prompts use: summary + last 8 messages
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│              React Frontend              │
│  Conversation List │ Chat │ Documents   │
└──────────────────┬──────────────────────┘
                   │ HTTP REST
                   ▼
┌─────────────────────────────────────────┐
│             FastAPI Backend              │
│         Routes → Services               │
│                                         │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │  Document   │  │   Chat Service   │  │
│  │  Service    │  │  (orchestrator)  │  │
│  └──────┬──────┘  └────────┬─────────┘  │
│         │                  │            │
│         ▼                  ▼            │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │   Gemini    │  │  LangGraph Agent │  │
│  │ Embeddings  │  │ (retrieval decision) │
│  └──────┬──────┘  └────────┬─────────┘  │
│         │                  │            │
│         │         ┌────────┴─────────┐  │
│         │         │  Vector │ Keyword │  │
│         │         │ Metadata│ Hybrid  │  │
│         │         └────────┬─────────┘  │
│         │                  │            │
│         └──────────────────┤            │
│                            ▼            │
│                   ┌─────────────────┐   │
│                   │   Repository    │   │
│                   └────────┬────────┘   │
└────────────────────────────┼────────────┘
                             ▼
              ┌──────────────────────────┐
              │        PostgreSQL        │
              │                          │
              │  conversations           │
              │  messages                │
              │  documents               │
              │  document_chunks         │
              │  retrieval_logs          │
              │  pgvector (embeddings)   │
              └──────────────────────────┘
```

---

## Technology Stack

### Backend
| Layer | Technology |
|-------|-----------|
| API Framework | FastAPI (Python) |
| Database | PostgreSQL 14+ |
| Vector Search | pgvector extension |
| ORM | SQLAlchemy 2.0 |
| DB Driver | psycopg 3 |
| Agent Framework | LangGraph + LangChain |
| Embeddings | Google Gemini (`gemini-embedding-2`) |
| LLM Provider | OpenRouter (configurable model) |
| Config | pydantic-settings + `.env` |
| PDF Parsing | pypdf |
| DOCX Parsing | python-docx |

### Frontend
| Layer | Technology |
|-------|-----------|
| Framework | React 18 + TypeScript |
| Build Tool | Vite |
| Data Fetching | TanStack Query (React Query) |
| HTTP Client | Axios |
| Styling | Tailwind CSS v3 |
| Icons | Lucide React |
| File Upload | React Dropzone |

### AI Models
| Function | Provider | Model |
|----------|----------|-------|
| Document embeddings | Google Gemini | `gemini-embedding-2` |
| Retrieval decision | OpenRouter | Configurable |
| Answer generation | OpenRouter | Configurable |
| Conversation summary | OpenRouter | Configurable |

---

## Project Structure

```
rag-app/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI app entry point
│   │   ├── core/
│   │   │   ├── config.py               # All settings from .env
│   │   │   └── logging.py
│   │   ├── routes/
│   │   │   ├── conversation_routes.py  # GET/POST /conversations
│   │   │   ├── chat_routes.py          # POST /conversations/{id}/messages
│   │   │   └── document_routes.py      # POST /conversations/{id}/documents
│   │   ├── services/
│   │   │   ├── chat_service.py         # Main RAG orchestration
│   │   │   ├── document_service.py     # Upload + ingestion pipeline
│   │   │   ├── embedding_service.py    # Gemini wrapper
│   │   │   ├── agent_service.py        # LangGraph runner
│   │   │   ├── retrieval_service.py    # Strategy dispatcher
│   │   │   └── summary_service.py      # Conversation summariser
│   │   ├── agents/
│   │   │   ├── rag_agent.py            # LangGraph state graph
│   │   │   ├── prompts.py              # All LLM prompts
│   │   │   └── state.py                # Agent state definition
│   │   ├── retrieval/
│   │   │   ├── vector_retriever.py     # pgvector cosine search
│   │   │   ├── keyword_retriever.py    # PostgreSQL full-text search
│   │   │   ├── metadata_retriever.py   # JSONB filtering
│   │   │   ├── hybrid_retriever.py     # Combines all three
│   │   │   └── reranker.py             # Reciprocal Rank Fusion
│   │   ├── document_processing/
│   │   │   ├── extractors/             # PDF, DOCX, TXT extractors
│   │   │   ├── chunker.py              # Overlapping text chunking
│   │   │   ├── keyword_extractor.py    # Frequency-based keywords
│   │   │   └── metadata_extractor.py   # Heuristic metadata detection
│   │   ├── integrations/
│   │   │   ├── gemini_client.py        # Google Gemini SDK wrapper
│   │   │   └── openrouter_client.py    # OpenRouter API wrapper
│   │   ├── models/                     # SQLAlchemy ORM models
│   │   ├── schemas/                    # Pydantic request/response schemas
│   │   ├── repositories/               # Database access layer
│   │   └── db/
│   │       └── database.py             # Engine, session, init_db
│   ├── tests/
│   │   ├── unit/                       # 27 unit tests
│   │   └── integration/                # 19 integration tests
│   ├── .env                            # Your secrets (never commit)
│   ├── .env.example                    # Template (safe to commit)
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── api/                        # Axios API calls
    │   ├── components/
    │   │   ├── chat/                   # ChatWindow, MessageBubble, Input
    │   │   ├── conversations/          # Sidebar conversation list
    │   │   ├── documents/              # Drag-and-drop upload panel
    │   │   ├── layout/                 # AppShell (two-column layout)
    │   │   └── ui/                     # Button, Spinner, Badge, EmptyState
    │   ├── hooks/                      # TanStack Query hooks
    │   ├── types/                      # TypeScript interfaces
    │   └── utils/                      # formatters, label helpers
    ├── .env.local                      # VITE_API_URL
    └── package.json
```

---

## Setup & Installation

### Prerequisites

- Python 3.12
- Node.js 18+
- PostgreSQL 14+ with pgvector extension
- Google Gemini API key → [Google AI Studio](https://aistudio.google.com/apikey)
- OpenRouter API key → [openrouter.ai/keys](https://openrouter.ai/keys)

---

### Backend Setup

```bash
cd backend

# Create virtual environment with Python 3.12
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1        # Windows
# source .venv/bin/activate       # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
```

Edit `.env` with your actual values:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ragdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ragdb

GEMINI_API_KEY=your_gemini_key_here
OPENROUTER_API_KEY=your_openrouter_key_here

OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
OPENROUTER_AGENT_MODEL=meta-llama/llama-3.1-8b-instruct:free
OPENROUTER_SUMMARY_MODEL=meta-llama/llama-3.1-8b-instruct:free

VECTOR_DIMENSION=3072
```

Enable pgvector in PostgreSQL:

```sql
-- Connect to your database first, then run:
CREATE EXTENSION IF NOT EXISTS vector;
```

Start the backend:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Verify it works: [http://localhost:8000/health](http://localhost:8000/health)
Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure API URL
copy .env.example .env.local
# VITE_API_URL=http://localhost:8000/api/v1

# Start dev server
npm run dev
```

Open: [http://localhost:5173](http://localhost:5173)

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/conversations` | Create a new conversation |
| GET | `/api/v1/conversations` | List all conversations |
| GET | `/api/v1/conversations/{id}` | Get a conversation |
| DELETE | `/api/v1/conversations/{id}` | Delete a conversation |
| POST | `/api/v1/conversations/{id}/messages` | Send a message (triggers RAG) |
| GET | `/api/v1/conversations/{id}/messages` | Get message history |
| POST | `/api/v1/conversations/{id}/documents` | Upload a document |
| GET | `/api/v1/conversations/{id}/documents` | List documents |
| DELETE | `/api/v1/conversations/documents/{id}` | Delete a document |

---

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | — | Google AI Studio key for embeddings |
| `GEMINI_EMBEDDING_MODEL` | `gemini-embedding-2` | Embedding model |
| `VECTOR_DIMENSION` | `3072` | Must match embedding model output |
| `OPENROUTER_API_KEY` | — | OpenRouter key for all LLM calls |
| `OPENROUTER_MODEL` | — | Model for answer generation |
| `OPENROUTER_AGENT_MODEL` | — | Model for retrieval decisions (can be smaller) |
| `OPENROUTER_SUMMARY_MODEL` | — | Model for conversation summarisation |
| `CHUNK_SIZE` | `700` | Characters per document chunk |
| `CHUNK_OVERLAP` | `100` | Overlap between chunks |
| `TOP_K` | `10` | Chunks fetched per retrieval strategy |
| `FINAL_CONTEXT_K` | `5` | Chunks passed to LLM after reranking |
| `MAX_HISTORY_MESSAGES` | `20` | Messages kept in context |
| `SUMMARY_TRIGGER_MESSAGES` | `20` | Messages before auto-summarisation |
| `MAX_FILE_SIZE_MB` | `25` | Maximum upload file size |

---

## Free Model Options

OpenRouter offers free-tier models. Set these in `.env`:

```env
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
OPENROUTER_AGENT_MODEL=meta-llama/llama-3.1-8b-instruct:free
OPENROUTER_SUMMARY_MODEL=meta-llama/llama-3.1-8b-instruct:free
```

Check current free models at: [openrouter.ai/models?supported_parameters=free](https://openrouter.ai/models?supported_parameters=free)

---

## Supported File Types

| Type | Extension | Notes |
|------|-----------|-------|
| PDF | `.pdf` | Text extraction per page |
| Word | `.docx` | Full document text |
| Plain text | `.txt` | UTF-8 encoding |
| Markdown | `.md` | Treated as plain text |

Maximum file size: **25 MB** (configurable)

---

## Running Tests

```bash
cd backend
.venv\Scripts\Activate.ps1

# Unit tests only (no database needed)
python -m pytest tests/unit/ -v

# All tests (requires PostgreSQL running)
python -m pytest tests/ -v
```

46 tests total — 27 unit tests, 19 integration tests.

---

## Security Notes

- API keys live only in `.env` — never committed to Git
- OpenRouter and Gemini keys are **never sent to the frontend**
- All LLM calls go through the backend: `Browser → FastAPI → OpenRouter`
- `.env` is listed in `.gitignore`
- File uploads are validated by type and size before processing
- All database queries use SQLAlchemy ORM (parameterised, no raw string injection)

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `uvicorn not recognised` | Run `python -m uvicorn` instead |
| `psycopg-binary` install fails | Make sure you are using Python 3.12, not 3.13/3.14 |
| `pydantic-core` build fails | Python version issue — use `py -3.12 -m venv .venv` |
| `vector extension not found` | Run `CREATE EXTENSION vector;` in your PostgreSQL database |
| Embeddings not working | Check `GEMINI_API_KEY` is set correctly in `.env` |
| LLM not responding | Check `OPENROUTER_API_KEY` and selected model name |
| Frontend can't reach backend | Ensure backend runs on port 8000 and CORS is enabled |
| Documents stuck in `processing` | Check backend logs for embedding errors |

---

## License

MIT — free to use, modify, and distribute.