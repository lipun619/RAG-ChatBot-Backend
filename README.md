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

A LangGraph-based Retrieval-Augmented Generation (RAG) chatbot backend that answers questions about Lipun Patel using knowledge ingested from local markdown files.

Built with **FastAPI**, **LangGraph**, **LangChain**, **ChromaDB**, and **SentenceTransformers**. Deployed on **Google Cloud Run**.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   INGESTION SIDE                     │
│                                                      │
│  POST /api/ingest  (on-demand)                       │
│       │                                              │
│       ▼                                              │
│  ingest_pipeline.py                                  │
│       │                                              │
│       └── local_loader.py    (markdown files)        │
│       │                                              │
│       ▼                                              │
│  SentenceTransformers → ChromaDB (vector_db/)        │
└──────────────────────┬──────────────────────────────┘
                       │ pre-built vector_db baked
                       │ into Docker image
┌──────────────────────▼──────────────────────────────┐
│                   QUERY SIDE (Runtime)               │
│                                                      │
│  FastAPI POST /api/chat or /api/chat/sync            │
│       │                                              │
│       ▼                                              │
│  LangGraph StateGraph                                │
│       │                                              │
│       ├── validate_query     (guard + greeting)      │
│       ├── greeting_response  (instant reply)         │
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
│   └── chat.py                 # POST /api/chat, /api/chat/sync, /api/ingest endpoints
├── rag/
│   ├── graph.py                # LangGraph StateGraph — greeting + RAG workflow
│   └── retriever.py            # ChromaDB + HuggingFace embeddings → cached retriever
├── ingestion/
│   ├── ingest_pipeline.py      # Orchestrates local loader → chunk → embed → store
│   └── local_loader.py         # Reads markdown files from app/data/
├── data/
│   ├── about.md                # Knowledge about Lipun Patel
│   ├── skills.md               # Skills and technologies
│   └── experience.md           # Experience and projects
└── main.py                     # FastAPI app — CORS, rate limiting, entry point

vector_db/                      # Pre-built ChromaDB storage (committed, baked into Docker image)
Dockerfile                      # Docker image for Cloud Run deployment
.dockerignore                   # Docker build exclusions
requirements.txt                # Python dependencies
.env                            # Environment variables (gitignored)
.env.example                    # Template for .env
Procfile                        # Gunicorn start command
```

---

## How It Works

### Ingestion Flow (On-Demand via `POST /api/ingest`)

1. **Collect** — Loads markdown files from `app/data/`
2. **Chunk** — `RecursiveCharacterTextSplitter` splits documents into 1000-character chunks with 200-character overlap
3. **Embed** — `all-MiniLM-L6-v2` (SentenceTransformers) converts chunks into vectors locally (no API key needed)
4. **Store** — Vectors are saved to ChromaDB at `vector_db/` (committed and baked into Docker image)

### Query Flow (Every Chat Request)

When a user sends a question to `POST /api/chat` or `POST /api/chat/sync`:

1. **validate_query** — Rejects empty/invalid questions; detects greetings
2. **greeting_response** — If greeting detected, returns instant friendly reply (skips RAG)
3. **retrieve_context** — Converts the question to a vector using `all-MiniLM-L6-v2`, searches ChromaDB for the 5 most similar chunks
4. **check_relevance** — GPT-4o-mini verifies the retrieved context is relevant to the question
5. **generate_answer** — GPT-4o-mini generates an answer using only the retrieved context

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
| **Docker** | Containerized deployment with pre-built vector DB |
| **Google Cloud Run** | Serverless hosting |
| **slowapi** | Rate limiting (5 requests/minute per IP) |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Send a question, receive SSE streamed answer |
| `POST` | `/api/chat/sync` | Send a question, receive JSON answer |
| `POST` | `/api/ingest` | Trigger vector DB rebuild from local markdown files |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI (auto-generated) |

### POST /api/chat (SSE Streaming)

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

### POST /api/chat/sync (JSON)

**Request:**
```json
{
  "question": "What are Lipun's skills?"
}
```

**Response:**
```json
{
  "answer": "Lipun Patel has expertise in Angular, TypeScript, Python..."
}
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
```

### Start the Server

```bash
uvicorn app.main:app --port 3000 --reload
```

The server will listen on `http://localhost:3000`.

To build the vector DB (first time or after updating markdown files):

```bash
curl -X POST http://localhost:3000/api/ingest
```

### Test

```bash
# Health check
curl http://localhost:3000/health

# Chat (JSON response — recommended)
curl -X POST http://localhost:3000/api/chat/sync \
  -H "Content-Type: application/json" \
  -d '{"question": "What are Lipun skills?"}'

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

## Docker (Local Testing)

### Build

```bash
docker build -t rag-bot .
```

### Run

```bash
docker run -p 3000:8080 -e "OPENAI_API_KEY=open-api-key" rag-bot
```

App will be available at `http://localhost:3000`.

### View Logs

```bash
docker logs --tail 50 $(docker ps -q -l)
```

---

## Deploy to Google Cloud Run

### Prerequisites

- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) installed
- A Google Cloud project with billing enabled

### Step 1: Build Vector DB Locally

Run ingestion locally to generate the `vector_db/` directory:

```bash
curl -X POST http://localhost:3000/api/ingest
```

The `vector_db/` is committed to the repo and baked into the Docker image.

### Step 2: Deploy

```bash
gcloud run deploy rag-chatbot-backend \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --no-cpu-throttling \
  --memory 1Gi \
  --timeout 300 \
  --set-env-vars "OPENAI_API_KEY=open-api-key"
```

This builds the Docker image in Cloud Build, pushes it to Artifact Registry, and deploys to Cloud Run.

### Step 3: Test

```bash
curl -X POST https://YOUR-CLOUD-RUN-URL/api/chat/sync \
  -H "Content-Type: application/json" \
  -d '{"question": "Who is Lipun?"}'
```

### View Logs

```bash
gcloud run services logs read rag-chatbot-backend --region asia-south1 --limit 30
```

### Notes

- The `all-MiniLM-L6-v2` embedding model is pre-downloaded during Docker build (no HuggingFace downloads at runtime)
- The retriever is cached as a singleton — first request initializes it, subsequent requests are fast
- `--no-cpu-throttling` keeps the CPU active during SSE streaming
- To update data: edit markdown files in `app/data/` → run ingestion locally → redeploy

---

## Adding Knowledge

Add or edit `.md` files in `app/data/`. Then rebuild the vector DB:

```bash
# Run locally
curl -X POST http://localhost:3000/api/ingest

# Redeploy to Cloud Run
gcloud run deploy rag-chatbot-backend --source . --region asia-south1
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT-4o-mini |
