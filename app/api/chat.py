import json
import logging

from fastapi import APIRouter, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sse_starlette.sse import EventSourceResponse

from app.rag.graph import run_graph

logger = logging.getLogger(__name__)

router = APIRouter()

# Rate limiter: 5 requests per minute per client IP
limiter = Limiter(key_func=get_remote_address)


class ChatRequest(BaseModel):
    question: str


@router.post("/api/chat")
@limiter.limit("1/minute")
async def chat(request: Request, body: ChatRequest):
    """Chat endpoint — invokes the LangGraph RAG workflow and streams the response via SSE."""
    logger.info("Chat request: '%s'", body.question)

    async def event_generator():
        async for chunk in run_graph(body.question):
            yield {"data": json.dumps({"content": chunk})}

    return EventSourceResponse(event_generator())
