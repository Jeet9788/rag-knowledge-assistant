"""FastAPI application entrypoint for the RAG Knowledge Assistant."""
from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .config import settings
from .db import close_db, init_db
from .embeddings import warmup
from .ingestion import delete_document, ingest_document, list_documents
from .rag import answer_stream
from .schemas import ChatRequest, DocumentOut, HealthResponse, IngestResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    try:
        warmup()
    except Exception:  # noqa: BLE001
        logger.warning("Embedding model warmup failed; will load lazily.", exc_info=True)
    yield
    close_db()


app = FastAPI(title="RAG Knowledge Assistant", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        llm_provider=settings.llm_provider,
        embedding_model=settings.embedding_model,
    )


@app.post("/documents", response_model=IngestResponse)
async def upload_document(
    file: UploadFile = File(...),
    collection: str = Form("default"),
) -> IngestResponse:
    data = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(413, f"File exceeds {settings.max_upload_mb} MB limit.")
    try:
        result = ingest_document(file.filename or "upload", data, collection)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return IngestResponse(**result)


@app.get("/documents", response_model=list[DocumentOut])
async def get_documents() -> list[DocumentOut]:
    return [DocumentOut(**d) for d in list_documents()]


@app.delete("/documents/{document_id}")
async def remove_document(document_id: str) -> dict:
    if not delete_document(document_id):
        raise HTTPException(404, "Document not found.")
    return {"deleted": document_id}


def _sse(event: dict) -> str:
    return f"event: {event['type']}\ndata: {json.dumps(event)}\n\n"


@app.post("/chat")
async def chat(req: ChatRequest) -> StreamingResponse:
    async def event_generator() -> AsyncIterator[str]:
        async for event in answer_stream(req.question, req.collection, req.top_k):
            yield _sse(event)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
