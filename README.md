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

## RAG Flow

```text
1) Knowledge Source
   app/data/about.md
   app/data/skills.md
   app/data/experience.md
   app/data/projects.md

2) Ingestion Pipeline
   load_local() -> RecursiveCharacterTextSplitter -> HuggingFaceEmbeddings

3) Embedding Model
   sentence-transformers/paraphrase-MiniLM-L3-v2
   Converts each text chunk into a vector embedding

4) Vector Store
   ChromaDB persists embeddings in vector_db/
   Collection: lipun_knowledge

5) User Question
   POST /api/chat or /api/chat/sync

6) Query Flow in LangGraph
   validate_query
   -> if greeting: greeting_response
   -> else: retrieve_context
   -> generate_answer

7) Retrieval
   Question is embedded with the same sentence-transformers model
   and the top 3 most relevant chunks are fetched from ChromaDB

8) Answer Generation
   GPT-4o-mini reads the retrieved context and answers using only that context
```

### Actual runtime flow in this project

- `app/ingestion/ingest_pipeline.py` loads all markdown files and chunks them with `RecursiveCharacterTextSplitter`.
- `sentence-transformers/paraphrase-MiniLM-L3-v2` is used to generate embeddings.
- The vectors are stored in ChromaDB under `vector_db/`.
- `app/rag/retriever.py` loads the persisted vector store and returns a retriever with `k=3`.
- `app/rag/graph.py` validates the input, retrieves relevant context, and sends it to `ChatOpenAI(model="gpt-4o-mini")` for answer generation.
- The app also includes a `check_relevance` function in `graph.py`, but the current compiled graph routes directly from retrieval to answer generation.

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
2. **Chunk** — `RecursiveCharacterTextSplitter` splits documents into chunks of 600 characters with a 120-character overlap
3. **Embed** — `sentence-transformers/paraphrase-MiniLM-L3-v2` converts each chunk into a vector embedding locally
4. **Store** — Vectors are saved into the ChromaDB collection named `lipun_knowledge` inside `vector_db/`

### Query Flow (Every Chat Request)

When a user sends a question to `POST /api/chat` or `POST /api/chat/sync`:

1. **validate_query** — Rejects empty/invalid questions and detects greeting messages
2. **greeting_response** — If the message is a greeting, a friendly answer is returned immediately
3. **retrieve_context** — The incoming question is embedded with the same `paraphrase-MiniLM-L3-v2` model and the top 3 matching chunks are fetched from ChromaDB
4. **generate_answer** — `gpt-4o-mini` generates a response using only the retrieved context

> The codebase contains a `check_relevance` helper, but the active LangGraph flow currently goes directly from retrieval to answer generation.

---

## Tech Stack

| Technology | Role |
|---|---|
| **FastAPI** | HTTP server, SSE streaming, CORS |
| **LangGraph** | Runtime Q&A workflow as a stateful graph |
| **LangChain** | Document loading, text chunking, ChromaDB wrapper, prompt chaining |
| **ChromaDB** | Persistent vector database for document retrieval |
| **SentenceTransformers** | Local embedding model: `sentence-transformers/paraphrase-MiniLM-L3-v2` |
| **OpenAI GPT-4o-mini** | LLM used for answer generation, with a relevance-check step also implemented in code |
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

- Python 3.12.x only
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

Or simply run the automated setup script:

```bash
./setup.sh
```

### Configure Environment

Copy `.env.example` to `.env` and fill in values:

```bash
cp .env.example .env
```

### macOS / Apple Silicon notes

If you are running this project on macOS Apple Silicon, the `sentence-transformers` dependency can require a compatible PyTorch wheel. If you see an error about `libtorch_cpu.dylib` when starting the app, install PyTorch from the official CPU wheel index first:

```bash
source venv/bin/activate
python -m pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

If you already installed `sentence-transformers`, rerun the PyTorch install command and then reinstall `sentence-transformers`.

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

### Troubleshooting

If deployment fails with `ZIP does not support timestamps before 1980`, fix file timestamps before deploying:

```bash
cd RAG-ChatBot-Backend
find . -not -path './.git/*' -exec touch {} +
```

Then re-run the deploy command.

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
