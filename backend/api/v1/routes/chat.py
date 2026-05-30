# backend/api/v1/routes/chat.py

from __future__ import annotations
import uuid
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from backend.app.dependencies import AuthUser, DbSession
from backend.models.schemas   import ChatRequest
from backend.rag.pipeline     import RAGPipeline

router   = APIRouter()
pipeline = RAGPipeline(top_k=5)


@router.post("/query")
async def chat_query(
    body:         ChatRequest,
    request:      Request,
    current_user: AuthUser,
):
    """
    Chat endpoint — non-streaming JSON response.
    The Streamlit frontend calls this and renders the full answer at once.
    For streaming, use /query/stream.
    """
    session_id = body.session_id or str(uuid.uuid4())

    answer, sources = await pipeline.run_sync(
        query=   body.query,
        role=    current_user.role,
        user_id= current_user.user_id,
    )

    return {
        "answer":     answer,
        "sources":    sources,
        "session_id": session_id,
        "role":       current_user.role.value,
    }


@router.post("/query/stream")
async def chat_query_stream(
    body:         ChatRequest,
    current_user: AuthUser,
):
    """
    Streaming SSE chat endpoint.
    Each chunk: data: {"delta": "...", "done": false}
    Final:      data: {"delta": "", "done": true, "sources": [...]}
    """
    session_id = body.session_id or str(uuid.uuid4())

    async def event_stream():
        async for sse_chunk in pipeline.run(
            query=   body.query,
            role=    current_user.role,
            user_id= current_user.user_id,
        ):
            yield sse_chunk.encode("utf-8")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":     "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history/{session_id}")
async def chat_history(session_id: str, current_user: AuthUser):
    # Full history stored in DB — wired in Phase 7
    return []
