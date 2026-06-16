from __future__ import annotations

import io
import logging

from ingestion.chunker import split_text

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Extracts text from PDF, DOCX, and TXT files and returns chunks."""

    def extract_chunks(
        self, content: bytes, filename: str, content_type: str
    ) -> list[str]:
        try:
            if filename.endswith(".pdf") or "pdf" in content_type:
                text = self._extract_pdf(content)
            elif filename.endswith(".docx"):
                text = self._extract_docx(content)
            else:
                text = content.decode("utf-8", errors="replace")

            if not text.strip():
                return []

            return split_text(text)
        except Exception as e:
            logger.error(f"Document extraction failed for '{filename}': {e}")
            return []

    def _extract_pdf(self, content: bytes) -> str:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(content))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)

    def _extract_docx(self, content: bytes) -> str:
        from docx import Document as DocxDocument
        doc = DocxDocument(io.BytesIO(content))
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
