from __future__ import annotations

from fastapi import APIRouter

from app.rag.schemas import IngestFileRequest, IngestResponse, QueryRequest, QueryResponse
from app.rag.service import DocumentRAGService

router = APIRouter(prefix="/rag", tags=["rag"])
service = DocumentRAGService()


@router.post("/ingest", response_model=IngestResponse)
def ingest_document(request: IngestFileRequest) -> IngestResponse:
    """Index a local PDF into the document vector store."""
    return service.ingest_pdf(request.file_path)


@router.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest) -> QueryResponse:
    """Retrieve the most relevant document chunks with source citations."""
    return service.retrieve(query=request.query, k=request.k)
