from __future__ import annotations

from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    document_id: str
    filename: str
    chunks_indexed: int
    collection_name: str


class IngestFileRequest(BaseModel):
    file_path: str = Field(min_length=1)


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)
    k: int = Field(default=4, ge=1, le=20)


class Citation(BaseModel):
    source: str
    page: int | None = None
    chunk_id: str | None = None


class RetrievedChunk(BaseModel):
    content: str
    score: float | None = None
    citation: Citation


class QueryResponse(BaseModel):
    query: str
    chunks: list[RetrievedChunk]
