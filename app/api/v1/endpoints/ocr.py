from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.db.session import SessionLocal
from app.schemas.ocr import OCRRequest, OCRResponse, OCRStatus
from app.services.ocr_service import process_ocr
from app.models.document import Document as DocumentModel
from app.models.processing_job import ProcessingJob as ProcessingJobModel
from app.models.processing_job import JobStatus
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/process", response_class=FileResponse)
async def process_document_ocr(
    request: OCRRequest,
    db: Session = Depends(get_db)
):
    """
    Process OCR for a document and return the markdown file.
    
    This endpoint processes the document synchronously and returns the .md file directly.
    For asynchronous processing, use /process-async endpoint.
    """
    # Verify document exists
    document = db.query(DocumentModel).filter(DocumentModel.id == request.document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {request.document_id} not found"
        )
    
    # Process OCR
    try:
        job = process_ocr(db, request.document_id)
        
        # Check if processing was successful
        if job.status != JobStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OCR processing failed: {job.error_message or 'Unknown error'}"
            )
        
        # Verify file exists
        if not job.output_path or not os.path.exists(job.output_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Output file not found"
            )
        
        # Generate filename for download
        original_name = document.original_filename.rsplit('.', 1)[0] if '.' in document.original_filename else document.original_filename
        download_filename = f"{original_name}_ocr.md"
        
        # Return the markdown file
        return FileResponse(
            job.output_path,
            media_type="text/markdown",
            filename=download_filename,
            headers={"Content-Disposition": f'attachment; filename="{download_filename}"'}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process OCR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process OCR: {str(e)}"
        )


@router.post("/process-async", response_model=OCRStatus, status_code=status.HTTP_202_ACCEPTED)
async def process_document_ocr_async(
    request: OCRRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start OCR processing for a document asynchronously.
    
    This endpoint accepts a document ID and starts the OCR process in the background.
    Returns immediately with a job ID that can be used to check the status.
    """
    # Verify document exists
    document = db.query(DocumentModel).filter(DocumentModel.id == request.document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {request.document_id} not found"
        )
    
    # Create a new job
    from app.models.processing_job import JobStatus
    job = ProcessingJobModel(
        document_id=request.document_id,
        status=JobStatus.PENDING
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Add background task
    background_tasks.add_task(process_ocr_task, request.document_id, job.id)
    
    return OCRStatus(
        job_id=job.id,
        document_id=job.document_id,
        status=job.status
    )


def process_ocr_task(document_id: int, job_id: int):
    """Background task to process OCR."""
    db = SessionLocal()
    try:
        process_ocr(db, document_id, job_id)
    except Exception as e:
        logger.error(f"Background OCR task failed: {e}")
    finally:
        db.close()

