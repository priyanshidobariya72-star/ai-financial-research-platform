from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch

from fastapi import HTTPException

from app.rag.schemas import QueryResponse
from app.rag.service import DocumentRAGService


class DocumentRAGServiceTests(TestCase):
    def test_ingest_pdf_adds_document_and_chunk_metadata(self) -> None:
        with TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir) / "sample.pdf"
            pdf_path.write_bytes(b"%PDF-1.4 sample")

            service = DocumentRAGService(documents_dir=tmpdir, persist_dir=tmpdir)
            documents = [SimpleNamespace(page_content="page 1", metadata={"page": 0})]
            chunks = [SimpleNamespace(page_content="chunk 1", metadata={"page": 0})]
            vectorstore = Mock()

            with (
                patch.object(service, "_extract_pdf_documents", return_value=documents),
                patch.object(service, "_chunk_documents", return_value=chunks),
                patch.object(service, "_get_vectorstore", return_value=vectorstore),
            ):
                response = service.ingest_pdf(pdf_path, document_id="doc-123")

            self.assertEqual(response.document_id, "doc-123")
            self.assertEqual(response.chunks_indexed, 1)
            self.assertEqual(chunks[0].metadata["document_id"], "doc-123")
            self.assertEqual(chunks[0].metadata["chunk_id"], "doc-123-chunk-0")
            self.assertEqual(chunks[0].metadata["source"], str(pdf_path))
            vectorstore.add_documents.assert_called_once_with(chunks)

    def test_ingest_pdf_raises_404_for_missing_file(self) -> None:
        service = DocumentRAGService()

        with self.assertRaises(HTTPException) as exc:
            service.ingest_pdf("missing.pdf")

        self.assertEqual(exc.exception.status_code, 404)

    def test_retrieve_returns_source_citations(self) -> None:
        service = DocumentRAGService()
        vectorstore = Mock()
        document = SimpleNamespace(
            page_content="Revenue increased year over year.",
            metadata={"source": "acme_10k.pdf", "page": 4, "chunk_id": "doc-1-chunk-7"},
        )
        vectorstore.similarity_search_with_relevance_scores.return_value = [(document, 0.92)]

        with patch.object(service, "_get_vectorstore", return_value=vectorstore):
            response = service.retrieve("What does the filing say about revenue growth?", k=1)

        self.assertIsInstance(response, QueryResponse)
        self.assertEqual(response.query, "What does the filing say about revenue growth?")
        self.assertEqual(len(response.chunks), 1)
        self.assertEqual(response.chunks[0].citation.source, "acme_10k.pdf")
        self.assertEqual(response.chunks[0].citation.page, 5)
        self.assertEqual(response.chunks[0].citation.chunk_id, "doc-1-chunk-7")
        self.assertEqual(response.chunks[0].score, 0.92)
