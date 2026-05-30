# 🏦 FinSolve AI — RBAC RAG Chatbot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-1.9-DC244C?style=for-the-badge&logo=qdrant&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Llama3.2-000000?style=for-the-badge&logo=ollama&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A secure, role-aware AI chatbot that answers questions from your company documents — and only shows each employee what their role is authorized to see.**

[Features](#-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [Demo](#-demo-credentials) • [Docs](#-project-structure)

</div>

---

## 📌 What is This?

FinSolve AI is a **production-ready RAG (Retrieval-Augmented Generation) chatbot** built for enterprise teams. It solves a real problem: employees waste 30–45 minutes daily hunting for information locked in department silos.

The system lets every employee ask natural language questions and get instant, accurate answers — but **only from documents their role is authorized to access**. A Finance analyst asking about HR salaries gets `"I don't have that information for your role."` A C-Level executive asking the same question gets the full answer.

Every response is **grounded in real company documents** with source citations. No hallucinations. No data leaks. Full audit trail.

---

## ✨ Features

- 🔐 **JWT Authentication** — secure login with bcrypt password hashing and account lockout
- 🛡️ **Role-Based Access Control (RBAC)** — 6 roles, enforced at the vector database layer
- 🤖 **RAG Pipeline** — semantic search over your documents using Qdrant + nomic-embed-text
- 🦙 **Local LLM** — powered by Llama 3.2 via Ollama — no API keys, no data leaving your machine
- 📄 **Source Citations** — every answer links to the source document and page number
- 💬 **Role-Aware Chat UI** — suggestion chips, typing indicators, and message bubbles tailored per role
- 🔍 **Prompt Injection Defense** — 14 regex patterns block adversarial queries
- 📋 **Audit Logging** — every query logged with user, role, retrieved docs, and latency
- 🐳 **Docker Ready** — Qdrant runs in Docker; full containerisation coming in v2

---

## 🏗️ Architecture

```
User → Streamlit UI → FastAPI Backend → RBAC Gate → RAG Pipeline → Ollama LLM
                                                  ↓
                                            Qdrant (role-filtered vector search)
                                                  ↓
                                        Company Documents (by department)
```

### Security layers (defense in depth)

```
Layer 1  Network       HTTPS · CORS allowlist
Layer 2  Rate Limit    60 req/min per user (Redis sliding window)
Layer 3  Auth          JWT RS256 · bcrypt cost=12 · account lockout
Layer 4  RBAC          Role policy · Qdrant metadata filter · deny by default
Layer 5  Application   Injection guard · response sanitizer · audit log
Layer 6  Data          AES-256 at rest · append-only audit table
```

### Access Control Matrix

| Role | Finance | HR | Engineering | Marketing | Executive | General |
|---|---|---|---|---|---|---|
| `finance` | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| `hr` | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| `engineering` | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| `marketing` | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| `employee` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| `c_level` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.11+ | [python.org](https://python.org) |
| Docker | Latest | [docker.com](https://docker.com/get-started) |
| Ollama | Latest | [ollama.com](https://ollama.com/download) |
| Git | Latest | [git-scm.com](https://git-scm.com) |

---

### Step 1 — Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/finsolve-rag-chatbot.git
cd finsolve-rag-chatbot
```

---

### Step 2 — Set up Python environment

```bash
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
# .venv\Scripts\activate         # Windows

pip install -r requirements-backend.txt
pip install -r requirements-frontend.txt
```

---

### Step 3 — Configure environment variables

```bash
cp .env.example .env
```

The defaults work out of the box for local development. No changes needed to get started.

```env
ENVIRONMENT=development
JWT_SECRET_KEY=finsolve-dev-secret-change-in-production
DATABASE_URL=sqlite+aiosqlite:///./finsolve.db
QDRANT_URL=http://localhost:6333
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

---

### Step 4 — Start Qdrant (vector database)

```bash
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -v $(pwd)/qdrant_data:/qdrant/storage \
  qdrant/qdrant
```

Verify → open `http://localhost:6333/dashboard` ✅

---

### Step 5 — Start Ollama and pull models

```bash
# Pull models (one-time, ~2.3GB total)
ollama pull llama3.2
ollama pull nomic-embed-text

# Start Ollama server
ollama serve
```

Verify → `http://localhost:11434` should show "Ollama is running" ✅

---

### Step 6 — Start the FastAPI backend

Open a new terminal:

```bash
uvicorn backend.app.main:app --reload --port 8000
```

On first run you'll see:
```
🚀  FinSolve API starting...
✅  Database ready
✅  Demo users seeded (password: Password123!)
✅  Qdrant ready
INFO:  Uvicorn running on http://127.0.0.1:8000
```

Swagger docs available at `http://localhost:8000/docs` ✅

---

### Step 7 — Ingest sample documents

```bash
python -m backend.ingestion.ingest --dir sample_docs
```

Expected output:
```
Found 5 files — starting ingestion...
[1/5] ✅ Q3_2024_Financial_Report.txt    → 8 chunks | dept: finance
[2/5] ✅ HR_Policy_Handbook_2024.txt     → 9 chunks | dept: hr
[3/5] ✅ Engineering_Architecture.txt    → 7 chunks | dept: engineering
[4/5] ✅ Marketing_Strategy_Q3_2024.txt  → 8 chunks | dept: marketing
[5/5] ✅ Employee_Handbook_2024.txt      → 6 chunks | dept: general
🎉 Ingestion complete!
```

---

### Step 8 — Start the Streamlit frontend

Open another new terminal:

```bash
cd frontend
streamlit run app.py
```

Open `http://localhost:8501` in your browser ✅

---

## 🎭 Demo Credentials

All demo users share the password: **`Password123!`**

| Username | Role | What they can access |
|---|---|---|
| `alice.finance` | 💼 Finance | Financial reports, budgets, forecasts + general |
| `bob.hr` | 👥 HR | HR policies, headcount, compensation + general |
| `carol.eng` | ⚙️ Engineering | Architecture docs, runbooks, sprints + general |
| `david.mktg` | 📣 Marketing | Campaign data, brand guidelines, market research + general |
| `eve.ceo` | 🏛️ C-Level | **Everything** across all departments |
| `frank.emp` | 🧑‍💼 Employee | General company policies only |

### Try the RBAC in action

1. Log in as **alice.finance** → ask *"What was our Q3 revenue?"* → gets full financial data
2. Log in as **alice.finance** → ask *"What is the leave policy?"* → gets `"I don't have that information for your role"`
3. Log in as **eve.ceo** → ask *"What is the leave policy?"* → gets the full HR answer
4. Log in as **bob.hr** → ask *"What is our burn rate?"* → gets `"I don't have that information for your role"`

---

## 📁 Project Structure

```
finsolve-rag-chatbot/
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app factory + startup
│   │   ├── config.py            # All settings via pydantic-settings
│   │   └── dependencies.py      # FastAPI dependency injection
│   │
│   ├── api/
│   │   ├── middleware/
│   │   │   ├── auth_middleware.py    # JWT validation on every request
│   │   │   └── rate_limiter.py       # Redis sliding-window rate limiting
│   │   └── v1/routes/
│   │       ├── auth.py          # /login /refresh /logout
│   │       ├── chat.py          # /query /query/stream
│   │       └── health.py        # /live /ready
│   │
│   ├── auth/
│   │   ├── jwt_handler.py       # Sign + verify JWT tokens
│   │   ├── password_handler.py  # bcrypt hash + verify
│   │   └── session_manager.py   # Redis refresh token store
│   │
│   ├── rbac/
│   │   ├── roles.py             # Role enum
│   │   └── access_matrix.py     # Single source of truth for permissions
│   │
│   ├── rag/
│   │   ├── pipeline.py          # Orchestrates full RAG flow
│   │   ├── embedder.py          # nomic-embed-text via Ollama
│   │   ├── retriever.py         # Role-filtered Qdrant search
│   │   ├── generator.py         # Llama 3.2 via Ollama (streaming)
│   │   └── injection_guard.py   # Prompt injection defense
│   │
│   ├── prompts/
│   │   └── prompt_builder.py    # Role-aware system prompts
│   │
│   ├── vector_db/
│   │   └── qdrant_client.py     # Qdrant singleton + collection setup
│   │
│   ├── ingestion/
│   │   └── ingest.py            # Document → chunks → embeddings → Qdrant
│   │
│   ├── models/
│   │   ├── user.py              # SQLAlchemy User model
│   │   └── schemas.py           # Pydantic request/response schemas
│   │
│   ├── db/
│   │   └── database.py          # Async SQLAlchemy + SQLite/PostgreSQL
│   │
│   └── scripts/
│       └── seed_users.py        # Auto-seed 6 demo users on startup
│
├── frontend/
│   ├── app.py                   # Streamlit entry point
│   ├── pages/
│   │   ├── 1_Login.py           # Login page with demo credential panel
│   │   └── 2_Chat.py            # Role-aware chat UI with streaming
│   ├── components/
│   │   ├── sidebar.py           # Role badge, session info, logout
│   │   └── source_card.py       # Expandable source citation cards
│   └── utils/
│       ├── api_client.py        # httpx client for FastAPI
│       └── session_state.py     # Streamlit session helpers + role config
│
├── sample_docs/
│   ├── finance/                 # Q3 Financial Report (finance + c_level)
│   ├── hr/                      # HR Policy Handbook (hr + c_level)
│   ├── engineering/             # Architecture Runbook (engineering + c_level)
│   ├── marketing/               # Marketing Strategy (marketing + c_level)
│   └── general/                 # Employee Handbook (all roles)
│
├── .env.example                 # Environment variable template
├── requirements-backend.txt     # Backend Python dependencies
├── requirements-frontend.txt    # Frontend Python dependencies
└── README.md
```

---

## 🔌 API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/login` | ❌ | Login with username + password |
| `POST` | `/api/v1/auth/refresh` | ❌ | Refresh access token |
| `POST` | `/api/v1/auth/logout` | ✅ | Invalidate session |
| `POST` | `/api/v1/chat/query` | ✅ | Ask a question (JSON response) |
| `POST` | `/api/v1/chat/query/stream` | ✅ | Ask a question (SSE stream) |
| `GET` | `/api/v1/health/live` | ❌ | Liveness probe |
| `GET` | `/api/v1/health/ready` | ❌ | Readiness probe (checks DB + Qdrant) |
| `GET` | `/docs` | ❌ | Swagger UI (dev only) |

Full interactive docs at `http://localhost:8000/docs` when running locally.

---

## ➕ Adding Your Own Documents

1. Create a subfolder under `sample_docs/` named after the department:
   ```
   sample_docs/
   └── finance/
       └── my_report.txt   ← access: finance + c_level
   ```

2. Supported departments (auto-detected from folder name):
   - `finance` → finance + c_level only
   - `hr` → hr + c_level only
   - `engineering` → engineering + c_level only
   - `marketing` → marketing + c_level only
   - `general` → all roles
   - `executive` → c_level only

3. Run ingestion:
   ```bash
   python -m backend.ingestion.ingest --dir sample_docs
   ```

Supported file types: `.txt`, `.pdf` (PDF support requires `pip install pymupdf`)

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|---|---|---|
| Backend API | FastAPI | 0.111 |
| ASGI Server | Uvicorn | 0.30 |
| Frontend | Streamlit | 1.35 |
| LLM | Llama 3.2 via Ollama | Latest |
| Embeddings | nomic-embed-text via Ollama | Latest |
| Vector DB | Qdrant | 1.9 |
| Auth | JWT (python-jose) + bcrypt | HS256 (dev) / RS256 (prod) |
| ORM | SQLAlchemy async | 2.0 |
| Database | SQLite (dev) / PostgreSQL (prod) | - |
| HTTP Client | httpx | 0.27 |
| Settings | pydantic-settings | 2.3 |

---

## 🔒 Production Hardening Checklist

Before deploying to production:

- [ ] Change `JWT_SECRET_KEY` to a strong random secret (or switch to RS256 keypair)
- [ ] Switch `DATABASE_URL` from SQLite to PostgreSQL
- [ ] Set `USE_REDIS=true` and configure `REDIS_URL` for session management
- [ ] Set `DEBUG=false` and `ENVIRONMENT=production`
- [ ] Enable HTTPS / TLS termination at your load balancer
- [ ] Restrict `CORS_ORIGINS` to your actual frontend domain
- [ ] Rotate the `QDRANT_API_KEY` from the default empty string
- [ ] Set up log aggregation (Elasticsearch / CloudWatch)
- [ ] Enable Prometheus metrics scraping at `/metrics`

---

## 🗺️ Roadmap

- [ ] **v1.1** — PostgreSQL + Redis in Docker Compose (one command setup)
- [ ] **v1.2** — PDF ingestion with PyMuPDF (currently `.txt` only)
- [ ] **v1.3** — Streaming chat UI (SSE frontend integration)
- [ ] **v1.4** — Admin panel — upload documents via UI (no CLI needed)
- [ ] **v2.0** — Docker Compose for full stack (backend + frontend + Qdrant + Redis)
- [ ] **v2.1** — OpenAI provider support (swap Ollama for GPT-4o with one config change)
- [ ] **v2.2** — Multi-tenant support (multiple organisations, isolated data)
- [ ] **v3.0** — Kubernetes Helm chart for production deployment

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

Please make sure your code:
- Follows the existing folder structure and naming conventions
- Includes docstrings on all functions
- Doesn't break existing demo credentials or RBAC behaviour

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

Free to use, modify, and distribute. Attribution appreciated but not required.

---

## 👤 Author

Built by **Abhishek Latawa**

If this project helped you, consider giving it a ⭐ on GitHub!

---

<div align="center">

**FinSolve AI** — Intelligence for every financial decision

*Built with FastAPI · Streamlit · Llama 3.2 · Qdrant*

</div>
