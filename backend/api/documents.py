from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from core.dependencies import AdminUser, DB
from schemas.document import DocumentListOut, DocumentOut, DocumentUploadResponse
from services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=DocumentListOut)
async def list_documents(_: AdminUser, db: DB):
    svc = DocumentService(db)
    docs, total = await svc.list_documents()
    return {"items": docs, "total": total}


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    current_user: AdminUser,
    db: DB,
    file: UploadFile = File(..., description="PDF, TXT, or DOCX file"),
):
    svc = DocumentService(db)
    result = await svc.upload_document(file=file, uploaded_by=str(current_user.id))
    return result


@router.delete("/{document_id}", status_code=204)
async def delete_document(_: AdminUser, db: DB, document_id: str):
    svc = DocumentService(db)
    await svc.delete_document(document_id)
