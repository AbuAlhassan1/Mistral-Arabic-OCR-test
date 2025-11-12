from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.processing_job import ProcessingJob
from app.schemas.ocr import OCRStatus
from app.models.processing_job import ProcessingJob as ProcessingJobModel, JobStatus
from app.models.document import Document as DocumentModel
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{job_id}", response_model=ProcessingJob)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """Get processing job status by job ID."""
    job = db.query(ProcessingJobModel).filter(ProcessingJobModel.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    return job


@router.get("/{job_id}/status", response_model=OCRStatus)
def get_job_status(
    job_id: int,
    db: Session = Depends(get_db)
):
    """Get processing job status."""
    job = db.query(ProcessingJobModel).filter(ProcessingJobModel.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    return OCRStatus(
        job_id=job.id,
        document_id=job.document_id,
        status=job.status,
        error_message=job.error_message
    )


@router.get("/{job_id}/download")
def download_result(
    job_id: int,
    db: Session = Depends(get_db)
):
    """Download the markdown result file."""
    job = db.query(ProcessingJobModel).filter(ProcessingJobModel.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job {job_id} is not completed yet. Status: {job.status}"
        )
    
    if not job.output_path or not os.path.exists(job.output_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Output file not found"
        )
    
    return FileResponse(
        job.output_path,
        media_type="text/markdown",
        filename=os.path.basename(job.output_path)
    )


@router.get("/document/{document_id}", response_model=List[ProcessingJob])
def get_document_jobs(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get all processing jobs for a specific document."""
    # Verify document exists
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    
    jobs = db.query(ProcessingJobModel).filter(
        ProcessingJobModel.document_id == document_id
    ).order_by(ProcessingJobModel.created_at.desc()).all()
    
    return jobs

