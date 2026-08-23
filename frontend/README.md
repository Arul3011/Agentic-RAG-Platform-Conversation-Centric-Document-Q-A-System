# Agentic RAG — Frontend

React + TypeScript frontend for the Agentic RAG platform. Built with Vite, TanStack Query, Tailwind CSS, and Lucide icons.

## Quick Start

```bash
cd frontend
npm install

# Configure API URL (copy and edit)
cp .env.example .env.local
# VITE_API_URL=http://localhost:8000/api/v1

npm run dev
# Opens at http://localhost:5173
```

Make sure the backend is running at port 8000 before starting the frontend.

---

## Features

| Feature | Description |
|---------|-------------|
| **Conversation sidebar** | Create, switch, delete conversations |
| **Chat window** | Send messages, see AI answers with streaming-style UX |
| **Source cards** | Every AI answer shows which documents + pages were retrieved |
| **Retrieval badge** | Shows which strategy the agent chose (Semantic / Keyword / Hybrid / None) |
| **Document panel** | Drag-and-drop upload (PDF · DOCX · TXT · MD), live processing status |
| **Multi-doc support** | Add more documents to an existing conversation at any time |
| **Auto-poll** | Documents in processing state are polled every 3 s until ready |
| **Conversation summary** | Displayed under the conversation title when available |
| **Keyboard shortcuts** | Enter to send, Shift+Enter for newline |

---

## Design System

| Token | Value | Usage |
|-------|-------|-------|
| `base-950` | `#080B11` | Deepest background |
| `base-900` | `#0F1117` | App background |
| `base-800` | `#161B27` | Message bubbles, cards |
| `base-700` | `#1E2A3B` | Borders |
| `indigo-500` | `#6366F1` | Primary accent, send button, active states |
| `emerald-400` | `#34D399` | Ready status, keyword retrieval |
| `amber-400` | `#FBBF24` | Metadata retrieval |
| `rose-400` | `#FB7185` | Error states, delete actions |

Fonts: **Inter** for UI, **JetBrains Mono** for badges and technical labels.

---

## Folder Structure

```
src/
├── api/
│   ├── client.ts           # Axios instance with error interceptor
│   ├── conversations.ts    # Conversation + message API calls
│   └── documents.ts        # Document upload / list / delete
├── components/
│   ├── chat/
│   │   ├── ChatWindow.tsx      # Main chat layout (messages + input + doc panel)
│   │   ├── MessageBubble.tsx   # User and assistant message rendering
│   │   ├── ChatInput.tsx       # Auto-resize textarea with send + attach
│   │   ├── SourceCard.tsx      # Retrieved source evidence cards
│   │   ├── RetrievalBadge.tsx  # Strategy label badge
│   │   └── TypingIndicator.tsx # Animated thinking dots
│   ├── conversations/
│   │   └── ConversationList.tsx # Sidebar list with create / delete
│   ├── documents/
│   │   └── DocumentPanel.tsx    # Dropzone + document list with status
│   ├── layout/
│   │   └── AppShell.tsx         # Two-column layout: sidebar + chat
│   └── ui/
│       ├── Spinner.tsx
│       ├── Badge.tsx
│       ├── Button.tsx
│       └── EmptyState.tsx
├── hooks/
│   ├── useConversations.ts  # TanStack Query hooks for conversations
│   ├── useMessages.ts       # TanStack Query hooks for messages + send
│   └── useDocuments.ts      # TanStack Query hooks for documents + upload
├── types/
│   └── index.ts             # Shared TypeScript interfaces
└── utils/
    └── format.ts            # formatFileSize, formatRelativeTime, strategyLabel…
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000/api/v1` | Backend API base URL |

---

## Scripts

```bash
npm run dev      # Start dev server (port 5173, with API proxy to :8000)
npm run build    # Production build → dist/
npm run preview  # Serve production build locally
npm run lint     # ESLint
```
