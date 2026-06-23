from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.config.settings import settings
from app.logger import get_logger
from app.rag.schemas import Citation, IngestResponse, QueryResponse, RetrievedChunk

logger = get_logger(__name__)


class DocumentRAGService:
    """Ingest PDFs into Chroma and retrieve relevant chunks with citations."""

    def __init__(
        self,
        documents_dir: str | Path | None = None,
        persist_dir: str | Path | None = None,
        collection_name: str | None = None,
        embedding_model_name: str | None = None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        self.documents_dir = Path(documents_dir or settings.rag_documents_dir)
        self.persist_dir = Path(persist_dir or settings.chroma_persist_dir)
        self.collection_name = collection_name or settings.chroma_collection_name
        self.embedding_model_name = embedding_model_name or settings.embedding_model_name
        self.chunk_size = chunk_size or settings.rag_chunk_size
        self.chunk_overlap = chunk_overlap or settings.rag_chunk_overlap

    async def ingest_upload(self, file: UploadFile) -> IngestResponse:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")

        self.documents_dir.mkdir(parents=True, exist_ok=True)
        document_id = uuid4().hex
        target_path = self.documents_dir / f"{document_id}_{Path(file.filename).name}"
        content = await file.read()
        target_path.write_bytes(content)
        logger.info("Saved PDF for ingestion at %s", target_path)
        return self.ingest_pdf(target_path, document_id=document_id, original_filename=file.filename)

    def ingest_pdf(
        self,
        file_path: str | Path,
        document_id: str | None = None,
        original_filename: str | None = None,
    ) -> IngestResponse:
        source_path = Path(file_path)
        if not source_path.exists():
            raise HTTPException(status_code=404, detail=f"PDF not found: {source_path}")

        documents = self._extract_pdf_documents(source_path)
        chunks = self._chunk_documents(documents)
        doc_id = document_id or uuid4().hex

        for index, chunk in enumerate(chunks):
            metadata = getattr(chunk, "metadata", {})
            metadata["document_id"] = doc_id
            metadata["chunk_id"] = f"{doc_id}-chunk-{index}"
            metadata["source"] = metadata.get("source") or str(source_path)
            chunk.metadata = metadata

        vectorstore = self._get_vectorstore()
        vectorstore.add_documents(chunks)
        self._persist_vectorstore(vectorstore)
        logger.info("Indexed %s chunks for %s", len(chunks), source_path)

        return IngestResponse(
            document_id=doc_id,
            filename=original_filename or source_path.name,
            chunks_indexed=len(chunks),
            collection_name=self.collection_name,
        )

    def retrieve(self, query: str, k: int = 4) -> QueryResponse:
        vectorstore = self._get_vectorstore()
        results = vectorstore.similarity_search_with_relevance_scores(query, k=k)
        chunks: list[RetrievedChunk] = []

        for document, score in results:
            metadata = getattr(document, "metadata", {}) or {}
            chunks.append(
                RetrievedChunk(
                    content=getattr(document, "page_content", ""),
                    score=score,
                    citation=Citation(
                        source=metadata.get("source", "unknown"),
                        page=self._normalize_page(metadata.get("page")),
                        chunk_id=metadata.get("chunk_id"),
                    ),
                )
            )

        return QueryResponse(query=query, chunks=chunks)

    def _extract_pdf_documents(self, file_path: Path) -> list[Any]:
        try:
            from langchain_community.document_loaders import PyPDFLoader
        except ImportError as exc:
            raise RuntimeError(
                "Missing dependency: install langchain-community and pypdf to enable PDF extraction."
            ) from exc

        return PyPDFLoader(str(file_path)).load()

    def _chunk_documents(self, documents: list[Any]) -> list[Any]:
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
        except ImportError as exc:
            raise RuntimeError(
                "Missing dependency: install langchain-text-splitters to enable chunking."
            ) from exc

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        return splitter.split_documents(documents)

    def _get_vectorstore(self) -> Any:
        try:
            from langchain_chroma import Chroma
        except ImportError as exc:
            raise RuntimeError("Missing dependency: install langchain-chroma and chromadb.") from exc

        self.persist_dir.mkdir(parents=True, exist_ok=True)
        return Chroma(
            collection_name=self.collection_name,
            persist_directory=str(self.persist_dir),
            embedding_function=self._get_embeddings(),
        )

    def _get_embeddings(self) -> Any:
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError as exc:
            raise RuntimeError(
                "Missing dependency: install langchain-huggingface and sentence-transformers."
            ) from exc

        return HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            encode_kwargs={"normalize_embeddings": True},
        )

    @staticmethod
    def _persist_vectorstore(vectorstore: Any) -> None:
        persist = getattr(vectorstore, "persist", None)
        if callable(persist):
            persist()

    @staticmethod
    def _normalize_page(page: Any) -> int | None:
        if page is None:
            return None
        if isinstance(page, int):
            return page + 1
        try:
            return int(page) + 1
        except (TypeError, ValueError):
            return None
