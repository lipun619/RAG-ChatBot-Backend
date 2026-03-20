import json
import logging

from fastapi import APIRouter, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sse_starlette.sse import EventSourceResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Rate limiter: 5 requests per minute per client IP
limiter = Limiter(key_func=get_remote_address)


class ChatRequest(BaseModel):
    question: str


@router.post("/api/chat")
@limiter.limit("5/minute")
async def chat(request: Request, body: ChatRequest):
    """Chat endpoint — invokes the LangGraph RAG workflow and streams the response via SSE."""
    logger.info("Chat request: '%s'", body.question)

    from app.rag.graph import run_graph

    async def event_generator():
        async for chunk in run_graph(body.question):
            yield {"data": json.dumps({"content": chunk})}

    return EventSourceResponse(event_generator())


@router.post("/api/ingest")
async def ingest():
    """Trigger the ingestion pipeline to rebuild the vector DB from local data."""
    from app.ingestion.ingest_pipeline import run_ingestion

    try:
        run_ingestion()
        return {"status": "success", "message": "Ingestion complete"}
    except Exception as e:
        logger.error("Ingestion failed: %s", e)
        return {"status": "error", "message": str(e)}
