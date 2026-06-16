from __future__ import annotations

import uuid
from typing import Any

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion.document_loader import DocumentLoader
from repositories.document_repo import DocumentRepository
from vectorstore.chroma_store import get_chroma_store


class DocumentService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = DocumentRepository(db)

    async def list_documents(self, skip: int = 0, limit: int = 50):
        return await self.repo.list_documents(skip=skip, limit=limit)

    async def upload_document(
        self, file: UploadFile, uploaded_by: uuid.UUID
    ) -> dict[str, Any]:
        allowed_types = {
            "application/pdf": ".pdf",
            "text/plain": ".txt",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        }
        content_type = file.content_type or "application/octet-stream"
        filename = file.filename or "upload"

        if not any(filename.endswith(ext) for ext in [".pdf", ".txt", ".docx"]):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Supported formats: PDF, TXT, DOCX",
            )

        contents = await file.read()

        # Load and chunk
        loader = DocumentLoader()
        chunks = loader.extract_chunks(contents, filename=filename, content_type=content_type)

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Could not extract text from document",
            )

        # Save metadata to DB
        doc = await self.repo.create(
            filename=filename,
            source=filename,
            content_type=content_type,
            uploaded_by=uploaded_by,
            metadata={"size_bytes": len(contents), "chunk_count": len(chunks)},
        )

        # Index in ChromaDB
        store = get_chroma_store()
        collection = store.documents_collection

        batch_docs, batch_ids, batch_metas = [], [], []
        for i, chunk_text in enumerate(chunks):
            chroma_id = f"doc-{doc.id}-chunk-{i}"
            batch_docs.append(chunk_text)
            batch_ids.append(chroma_id)
            batch_metas.append({
                "document_id": str(doc.id),
                "filename": filename,
                "chunk_index": i,
            })
            await self.repo.add_chunk(
                document_id=doc.id,
                chroma_id=chroma_id,
                chunk_text=chunk_text,
                chunk_index=i,
            )

        if batch_docs:
            collection.upsert(documents=batch_docs, ids=batch_ids, metadatas=batch_metas)

        return {
            "id": doc.id,
            "filename": doc.filename,
            "chunks_indexed": len(chunks),
            "message": "Document uploaded and indexed successfully",
        }

    async def delete_document(self, doc_id: uuid.UUID) -> None:
        doc = await self.repo.get_by_id(doc_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        # Remove from ChromaDB
        store = get_chroma_store()
        try:
            chunk_ids = [f"doc-{doc_id}-chunk-{i}" for i in range(len(doc.chunks))]
            if chunk_ids:
                store.documents_collection.delete(ids=chunk_ids)
        except Exception:
            pass

        await self.repo.delete(doc_id)
