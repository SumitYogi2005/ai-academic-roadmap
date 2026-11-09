"""
Document upload, extraction status, and syllabus review routes.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import get_current_user_id
from app.db.database import get_database
from app.models.document import DocumentStatus, SyllabusContent, SyllabusDocument, Unit, Topic
from app.repositories import document_repository as doc_repo
from app.services.document import storage
from app.services.document.extractor import extract_text
from app.services.ai.provider import get_ai_provider
from app.services.ai.prompts import syllabus_analysis_prompt

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["Documents"])


async def _process_document(db, doc_id: str, storage_key: str, mime_type: str) -> None:
    """Background task: extract text, call AI analysis, persist syllabus content."""
    try:
        await doc_repo.update_document_status(db, doc_id, DocumentStatus.PROCESSING)
        file_path = storage.get_file_path(storage_key)
        raw_text = extract_text(file_path, mime_type)

        if not raw_text.strip():
            await doc_repo.update_document_status(
                db, doc_id, DocumentStatus.FAILED, "Could not extract any text from the document."
            )
            return

        # AI analysis
        provider = get_ai_provider()
        prompt = syllabus_analysis_prompt(raw_text)
        try:
            ai_result = await provider.generate_structured_output(prompt, schema={})
        except Exception as ai_exc:
            logger.warning("AI analysis failed, using raw text: %s", ai_exc)
            ai_result = {
                "subject": "Unknown Subject",
                "units": [],
                "warnings": [f"AI analysis failed: {ai_exc}"],
            }

        # Build SyllabusContent from AI result
        units = []
        for u_data in ai_result.get("units", []):
            topics = [
                Topic(
                    id=t.get("id", f"t_{i}"),
                    name=t.get("name", "Topic"),
                    description=t.get("description", ""),
                    duration_hours=float(t.get("duration_hours", 1.0)),
                    objectives=t.get("objectives", []),
                )
                for i, t in enumerate(u_data.get("topics", []))
            ]
            units.append(Unit(
                id=u_data.get("id", f"u_{len(units)}"),
                name=u_data.get("name", "Unit"),
                description=u_data.get("description", ""),
                topics=topics,
                sequence=u_data.get("sequence", len(units) + 1),
            ))

        content = SyllabusContent(
            document_id=doc_id,
            raw_text=raw_text[:50000],  # cap stored text
            units=units,
            ai_warnings=ai_result.get("warnings", []),
        )
        await doc_repo.upsert_content(db, content)
        await doc_repo.update_document_status(db, doc_id, DocumentStatus.COMPLETED)
        logger.info("Document %s processed successfully: %d units", doc_id, len(units))

    except Exception as exc:
        logger.error("Document processing failed for %s: %s", doc_id, exc)
        await doc_repo.update_document_status(db, doc_id, DocumentStatus.FAILED, str(exc))


@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    subject_id: str = Form(default="unknown"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Upload a syllabus file (PDF, DOCX, PNG, JPG). Returns a document ID for status polling."""
    try:
        storage_key = await storage.save_file(file, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    doc = SyllabusDocument(
        user_id=user_id,
        subject_id=subject_id or "unknown",
        file_name=file.filename or "upload",
        storage_key=storage_key,
        mime_type=(file.content_type or "application/octet-stream").split(";")[0].strip(),
        size=file.size or 0,
        status=DocumentStatus.PENDING,
    )
    created = await doc_repo.create_document(db, doc)
    doc_id = created["_id"]

    # Process in background
    background_tasks.add_task(_process_document, db, doc_id, storage_key, doc.mime_type)

    return {
        "success": True,
        "data": {"id": doc_id, "status": "pending"},
        "message": "File uploaded. Processing has started.",
    }


@router.get("/{doc_id}/status")
async def get_document_status(
    doc_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Poll the processing status of an uploaded document."""
    doc = await doc_repo.get_document_by_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    if doc["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    return {
        "success": True,
        "data": {
            "id": doc_id,
            "status": doc["status"],
            "file_name": doc["file_name"],
            "error_message": doc.get("error_message"),
        },
    }


@router.get("/{doc_id}/extraction")
async def get_extraction(
    doc_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Return the AI-extracted syllabus structure for student review."""
    doc = await doc_repo.get_document_by_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    if doc["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    if doc["status"] != DocumentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document is not ready. Status: {doc['status']}",
        )

    content = await doc_repo.get_content_by_document_id(db, doc_id)
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extraction content not found.")

    return {"success": True, "data": content}


@router.put("/{doc_id}/extraction")
async def update_extraction(
    doc_id: str,
    body: dict,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Save student corrections to the extracted syllabus."""
    doc = await doc_repo.get_document_by_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    if doc["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    updates: dict = {}
    if "units" in body:
        updates["units"] = body["units"]
    if "verification_status" in body:
        updates["verification_status"] = body["verification_status"]

    updated = await doc_repo.update_content(db, doc_id, updates)
    return {"success": True, "data": updated, "message": "Syllabus corrections saved."}


@router.get("")
async def list_documents(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """List all documents uploaded by the authenticated student."""
    docs = await doc_repo.get_documents_by_user(db, user_id)
    return {"success": True, "data": docs}
