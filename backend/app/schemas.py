"""Pydantic request/response models for the API."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DocumentOut(BaseModel):
    id: str
    filename: str
    collection: str
    num_chunks: int
    created_at: datetime


class IngestResponse(BaseModel):
    document_id: str
    filename: str
    collection: str
    num_chunks: int


class Citation(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    page: int | None = None
    chunk_index: int
    score: float
    snippet: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    collection: str = "default"
    top_k: int | None = None


class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    embedding_model: str
