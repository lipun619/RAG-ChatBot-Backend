FROM python:3.12-slim

WORKDIR /app

# Install system dependencies required by chromadb and sentence-transformers
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and pre-built vector_db
COPY app/ app/
COPY vector_db/ vector_db/

# Cloud Run sets PORT env var (default 8080)
ENV PORT=8080

EXPOSE ${PORT}

CMD exec gunicorn app.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
