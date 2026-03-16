---
title: RAG ChatBot Backend
emoji: 🏆
colorFrom: pink
colorTo: blue
sdk: docker
pinned: false
license: mit
short_description: RAG-ChatBot-Backend
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# RAG ChatBot Backend

A LangGraph-based Retrieval-Augmented Generation (RAG) chatbot backend that answers questions about Lipun Patel using knowledge ingested from multiple sources.

Built with **FastAPI**, **LangGraph**, **LangChain**, **ChromaDB**, and **SentenceTransformers**.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   INGESTION SIDE                     │
│                                                      │
│  APScheduler (every 24h)                             │
│       │                                              │
│       ▼                                              │
│  ingest_pipeline.py                                  │
│       │                                              │
│       ├── github_loader.py   (PyGithub)              │
│       ├── website_loader.py  (BeautifulSoup)         │
│       ├── resume_loader.py   (pypdf)                 │
│       └── local_loader.py    (pathlib)               │
│       │                                              │
│       ▼                                              │
│  SentenceTransformers → ChromaDB (vector_db/)        │
└──────────────────────┬──────────────────────────────┘
                       │ shared ChromaDB collection
┌──────────────────────▼──────────────────────────────┐
│                   QUERY SIDE (Runtime)               │
│                                                      │
│  FastAPI POST /api/chat                              │
│       │                                              │
│       ▼                                              │
│  LangGraph StateGraph                                │
│       │                                              │
│       ├── validate_query     (guard node)            │
│       ├── retrieve_context   (ChromaDB retriever)    │
│       ├── check_relevance    (LLM-based check)       │
│       └── generate_answer    (LLM + context → SSE)   │
└─────────────────────────────────────────────────────┘
```

---

## Project Structure

```
app/
├── api/
│   └── chat.py                 # POST /api/chat endpoint, SSE streaming, rate limiting
├── rag/
│   ├── graph.py                # LangGraph StateGraph — 4-node Q&A workflow
│   └── retriever.py            # ChromaDB + HuggingFace embeddings → LangChain retriever
├── ingestion/
│   ├── ingest_pipeline.py      # Orchestrates all loaders → chunk → embed → store
│   ├── github_loader.py        # Loads repos from GitHub via PyGithub
│   ├── website_loader.py       # Scrapes portfolio website via BeautifulSoup
│   ├── resume_loader.py        # Extracts text from resume PDF via pypdf
│   ├── local_loader.py         # Reads markdown files from app/data/
│   └── scheduler.py            # APScheduler — runs ingestion every 24 hours
├── data/
│   ├── about.md                # Knowledge about Lipun Patel
│   ├── skills.md               # Skills and technologies
│   └── experience.md           # Experience and projects
└── main.py                     # FastAPI app — CORS, rate limiting, lifespan, entry point

vector_db/                      # ChromaDB persistent storage (auto-generated, gitignored)
requirements.txt                # Python dependencies
.env                            # Environment variables (gitignored)
.env.example                    # Template for .env
Procfile                        # Render.com start command
```

---

## How It Works

### Ingestion Flow (Startup + Every 24 Hours)

1. **Collect** — Four loaders gather documents from GitHub repos, portfolio website, resume PDF, and local markdown files
2. **Chunk** — `RecursiveCharacterTextSplitter` splits documents into 1000-character chunks with 200-character overlap
3. **Embed** — `all-MiniLM-L6-v2` (SentenceTransformers) converts chunks into vectors locally (no API key needed)
4. **Store** — Vectors are saved to ChromaDB at `vector_db/`

### Query Flow (Every Chat Request)

When a user sends a question to `POST /api/chat`:

1. **validate_query** — Rejects empty or invalid questions
2. **retrieve_context** — Converts the question to a vector using the same `all-MiniLM-L6-v2` model, searches ChromaDB for the 5 most similar chunks
3. **check_relevance** — GPT-4o-mini verifies the retrieved context is relevant to the question
4. **generate_answer** — GPT-4o-mini generates an answer using only the retrieved context, streamed back as SSE events

---

## Tech Stack

| Technology | Role |
|---|---|
| **FastAPI** | HTTP server, SSE streaming, CORS |
| **LangGraph** | Runtime Q&A workflow as a directed StateGraph |
| **LangChain** | Document model, text splitters, ChromaDB wrapper, LLM interface |
| **ChromaDB** | Persistent vector database (local, embedded) |
| **SentenceTransformers** | Local embedding model (`all-MiniLM-L6-v2`) — free, no API key |
| **OpenAI GPT-4o-mini** | LLM for relevance checking and answer generation |
| **APScheduler** | Background scheduler for periodic ingestion |
| **PyGithub** | GitHub API client for loading repository data |
| **BeautifulSoup** | HTML parsing for portfolio website scraping |
| **pypdf** | PDF text extraction for resume |
| **slowapi** | Rate limiting (5 requests/minute per IP) |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Send a question, receive SSE streamed answer |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI (auto-generated) |
| `GET` | `/redoc` | ReDoc API docs (auto-generated) |

### POST /api/chat

**Request:**
```json
{
  "question": "What are Lipun's skills?"
}
```

**Response:** Server-Sent Events stream
```
data: {"content": "Lipun Patel has expe"}
data: {"content": "rtise in Angular, Ty"}
data: {"content": "peScript, Python..."}
```

---

## Run Locally

### Prerequisites

- Python 3.12+
- OpenAI API key

### Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/chatbot-backend.git
cd chatbot-backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configure Environment

Copy `.env.example` to `.env` and fill in values:

```bash
cp .env.example .env
```

```env
OPENAI_API_KEY=sk-your-key-here        # Required — for GPT-4o-mini
GITHUB_TOKEN=ghp_your-token            # Optional — for GitHub repo ingestion
PORTFOLIO_URL=https://your-site.com    # Optional — for website scraping
RESUME_PATH=app/data/resume.pdf        # Optional — for resume ingestion
```

Only `OPENAI_API_KEY` is required. The other sources are optional — local markdown files in `app/data/` are always loaded.

### Start the Server

```bash
uvicorn app.main:app --port 3000 --reload
```

The server will:
1. Run initial ingestion (load documents → embed → store in ChromaDB)
2. Start the 24-hour scheduler
3. Listen on `http://localhost:3000`

### Test

```bash
# Health check
curl http://localhost:3000/health

# Chat (SSE stream)
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What are Lipun skills?"}'
```

Or open `http://localhost:3000/docs` for the Swagger UI.

### Debug in VS Code

Use the included launch configuration (`.vscode/launch.json`):

1. Open **Run and Debug** panel (Ctrl+Shift+D)
2. Select **"Debug FastAPI"**
3. Press F5

---

## Deploy to Render.com (Free)

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: LangGraph RAG chatbot backend"
git remote add origin https://github.com/YOUR_USERNAME/chatbot-backend.git
git branch -M main
git push -u origin main
```

### Step 2: Create Render Web Service

1. Go to [render.com](https://render.com) → Sign up with GitHub
2. Click **New → Web Service**
3. Connect your `chatbot-backend` repo
4. Configure:

| Setting | Value |
|---|---|
| Runtime | Python |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | Free |

### Step 3: Add Environment Variables

In the Render dashboard → Environment tab:

| Key | Value |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `GITHUB_TOKEN` | Your GitHub token (optional) |
| `PORTFOLIO_URL` | Your portfolio URL (optional) |
| `RESUME_PATH` | `app/data/resume.pdf` (optional) |

### Step 4: Deploy

Click **Deploy**. Your API will be live at:

```
https://your-app-name.onrender.com
```

### Free Tier Notes

- App sleeps after 15 minutes of inactivity — first request after sleep takes ~30-60 seconds
- `vector_db/` is ephemeral (wiped on redeploy) — rebuilt automatically on each startup
- The 24h scheduler won't fire (app sleeps first) — but ingestion runs on every cold start
- Embedding model (`all-MiniLM-L6-v2`, ~90MB) is re-downloaded on each cold start

---

## Adding Knowledge

### Local Markdown Files

Add `.md` files to `app/data/`. They are automatically loaded on the next ingestion run or server restart.

### GitHub Repositories

Set `GITHUB_TOKEN` in `.env`. All your public repos (name, description, README, languages) are ingested automatically.

### Portfolio Website

Set `PORTFOLIO_URL` in `.env`. Pages `/about`, `/skills`, and `/projects` are scraped and ingested.

### Resume PDF

Place your resume PDF in `app/data/` and set `RESUME_PATH=app/data/resume.pdf` in `.env`.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT-4o-mini |
| `GITHUB_TOKEN` | No | GitHub personal access token |
| `PORTFOLIO_URL` | No | Portfolio website base URL |
| `RESUME_PATH` | No | Path to resume PDF file |
