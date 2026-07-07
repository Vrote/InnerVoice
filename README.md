# 🧠 InnerVoice — AI Psychological Companion

> *A single-screen conversational AI that secretly runs a deep agentic reasoning system in the background — built with LangGraph, FastAPI, and Next.js.*

---

## 🌟 What is InnerVoice?

InnerVoice looks and feels exactly like a simple chat app. But beneath the surface it runs a **14-tool multi-node AI reasoning loop** that:

- **Mirrors your writing style** — learns your tone, vocabulary, and sentence patterns
- **Remembers you across months** — hybrid SQLite + vector semantic memory
- **Tracks your emotional journey** — mood scoring, emotion detection, pattern analysis
- **Manages your goals** — detects goals in your messages, tracks progress
- **Generates monthly self-portraits** — the "Mirror Me" dashboard shows mood trends, key themes, lessons, and a word cloud of your language

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│              Next.js Frontend                │
│  /chat  ·  /mirror-me  ·  /auth             │
└────────────────┬────────────────────────────┘
                 │ REST API (Axios + envelope unwrapping)
┌────────────────▼────────────────────────────┐
│              FastAPI Backend                 │
│  /api/chat  /api/history  /api/mirror-me    │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│         LangGraph StateGraph (v4.0)          │
│                                              │
│  crisis_node → plan_node → execute_tool     │
│  → reflect_node → respond_node              │
└────────────────┬────────────────────────────┘
                 │
    ┌────────────┴──────────────┐
    │         14 AI Tools        │
    │  voice_profile             │
    │  memory_retrieve           │
    │  memory_save               │
    │  emotion_analyze           │
    │  pattern_detect            │
    │  mood_analytics            │
    │  goal_tracker              │
    │  reflection_generate       │
    │  plan_generator            │
    │  weekly_summary            │
    │  mirror_me_report          │
    │  followup_manager          │
    │  crisis_support            │
    │  context_builder           │
    └───────────────────────────┘
                 │
    ┌────────────┴──────────────┐
    │       Persistence          │
    │  SQLite (aiosqlite)        │
    │  ChromaDB (vector store)   │
    │  APScheduler (bg jobs)     │
    └───────────────────────────┘
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS |
| **Backend** | FastAPI, Python 3.11+ |
| **AI Orchestration** | LangGraph (StateGraph) |
| **LLM** | Groq API (llama-3.1-8b-instant) |
| **Database** | SQLite + aiosqlite (async) |
| **Vector Store** | ChromaDB (in-memory fallback if not installed) |
| **Auth** | JWT (python-jose) + bcrypt |
| **Scheduler** | APScheduler |
| **State Management** | Zustand (frontend) |

---

## ✨ Key Features

### 💬 Chat Interface
- Single-screen design — no sidebars, no clutter
- Typewriter effect for AI responses
- Collapsible reasoning panel (see which tools ran)
- Inline follow-up questions from the AI
- Crisis detection with helpline resources

### 📅 Monthly Partitioning
- Conversations are automatically separated by month
- Past months are read-only archives — browsable via dropdown
- Each month gets its own Mirror Me analysis

### 🪞 Mirror Me Dashboard
- Monthly self-portrait report generated from your conversations
- Mood ring (average score visualization)
- Word cloud of your language patterns
- Key themes, lessons learned, self-care recommendations
- Supportive closing message from your InnerVoice
- "Refresh with latest chats" button — always up to date

### 🔒 Safety First
- Dedicated `crisis_node` at the entry point of every conversation
- Routes directly to crisis support/helplines for severe distress
- Bypasses the normal conversational flow entirely

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- A [Groq API key](https://console.groq.com)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/InnerVoice.git
cd InnerVoice
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Frontend Setup

```bash
cd frontend
npm install

# Configure environment
cp .env.local.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Run the Project

**Terminal 1 — Backend:**
```bash
# From the project root
.\backend\venv\Scripts\python.exe -m backend.main
# Backend runs at http://localhost:8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
# Frontend runs at http://localhost:3000
```

---

## 📁 Project Structure

```
InnerVoice/
├── backend/
│   ├── agent/
│   │   ├── reasoning_loop.py     # LangGraph StateGraph (5 nodes)
│   │   ├── state.py              # AgentState TypedDict
│   │   └── tools/                # 14 AI tools
│   │       ├── voice_profile.py
│   │       ├── memory_retrieve.py
│   │       ├── memory_save.py
│   │       ├── emotion_analyze.py
│   │       ├── pattern_detect.py
│   │       ├── mood_analytics.py
│   │       ├── goal_tracker.py
│   │       └── ...
│   ├── core/
│   │   ├── config.py             # Settings (pydantic)
│   │   └── security.py           # JWT auth
│   ├── database/
│   │   ├── connection.py         # Async SQLAlchemy engine
│   │   └── models.py             # 10 SQLAlchemy models
│   ├── jobs/
│   │   └── scheduler.py          # APScheduler background jobs
│   ├── routes/
│   │   ├── chat.py               # POST /api/chat
│   │   ├── history.py            # GET  /api/history
│   │   ├── mirror_me.py          # GET/POST /api/mirror-me
│   │   └── users.py              # Auth endpoints
│   ├── services/
│   │   ├── llm_service.py        # Groq LLM wrapper
│   │   ├── embedding_service.py  # Embedding + fallback
│   │   ├── vector_store.py       # ChromaDB operations
│   │   └── mirror_me_service.py  # Monthly report generation
│   ├── main.py                   # FastAPI app entry point
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── chat/page.tsx         # Main chat interface
│   │   ├── mirror-me/page.tsx    # Monthly insights dashboard
│   │   └── auth/                 # Login / Register
│   ├── components/
│   ├── lib/
│   │   └── api.ts                # Axios + envelope unwrapping
│   └── stores/
│       └── authStore.ts          # Zustand auth store
│
└── README.md
```

---

## 🔑 Environment Variables

### Backend (`backend/.env`)

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_ORCHESTRATOR_MODEL=llama-3.1-8b-instant
GROQ_TOOL_MODEL=llama-3.1-8b-instant
DATABASE_URL=sqlite+aiosqlite:///./innervoice.db
SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080
APP_ENV=development
BACKEND_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000
MAX_REASONING_ITERATIONS=8
```

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🧪 API Overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Create a new account |
| `POST` | `/api/auth/login` | Login and get JWT |
| `POST` | `/api/chat` | Send a message, triggers agent loop |
| `POST` | `/api/chat/reply` | Reply to an AI follow-up question |
| `GET` | `/api/history` | Paginated chat history (by month) |
| `GET` | `/api/mirror-me/status` | Qualification status for the month |
| `POST` | `/api/mirror-me/generate` | Generate/refresh monthly report |
| `GET` | `/api/mirror-me/{year}/{month}` | Fetch a specific month's report |

---


<p align="center">Built with ❤️ using LangGraph, FastAPI & Next.js</p>
