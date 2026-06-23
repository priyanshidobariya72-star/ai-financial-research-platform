from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from app.api.schemas import AnalyzeRequest, AnalyzeResponse, ChatRequest, ChatResponse, CompareRequest, CompareResponse
from app.api.service import ChatService, CompanyAnalysisService
from app.rag.schemas import IngestResponse
from app.rag.service import DocumentRAGService

router = APIRouter(tags=["platform"])
analysis_service = CompanyAnalysisService()
chat_service = ChatService()
rag_service = DocumentRAGService()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return chat_service.answer(query=request.query, k=request.k)


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    return analysis_service.analyze_company(request.ticker)


@router.post("/compare", response_model=CompareResponse)
def compare(request: CompareRequest) -> CompareResponse:
    return analysis_service.compare_companies(request.ticker1, request.ticker2)


@router.post("/upload", response_model=IngestResponse)
async def upload(file: UploadFile = File(...)) -> IngestResponse:
    return await rag_service.ingest_upload(file)
