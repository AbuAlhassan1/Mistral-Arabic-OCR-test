import base64
import os
import logging
import time
from datetime import datetime
from typing import Optional
from mistralai import Mistral
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.document import Document, DocumentStatus
from app.models.processing_job import ProcessingJob, JobStatus
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Initialize Mistral client
mistral_client = Mistral(api_key=settings.MISTRAL_API_KEY)


def ensure_directories():
    """Ensure upload and export directories exist."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.EXPORT_DIR, exist_ok=True)


def encode_pdf_to_base64(file_path: str) -> Optional[str]:
    """Encode PDF file to base64 string."""
    try:
        with open(file_path, "rb") as pdf_file:
            return base64.b64encode(pdf_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to encode PDF {file_path}: {e}")
        return None


def process_ocr(
    db: Session,
    document_id: int,
    job_id: Optional[int] = None
) -> ProcessingJob:
    """
    Process OCR on a document.
    
    Args:
        db: Database session
        document_id: ID of the document to process
        job_id: Optional job ID if resuming an existing job
    
    Returns:
        ProcessingJob instance
    """
    ensure_directories()
    
    # Get document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise ValueError(f"Document {document_id} not found")
    
    # Get or create job
    if job_id:
        job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
    else:
        job = ProcessingJob(document_id=document_id, status=JobStatus.PENDING)
        db.add(job)
        db.commit()
        db.refresh(job)
    
    # Update document status
    document.status = DocumentStatus.PROCESSING
    db.commit()
    
    # Update job status
    job.status = JobStatus.PROCESSING
    job.attempts += 1
    db.commit()
    
    try:
        # Encode PDF
        b64_content = encode_pdf_to_base64(document.file_path)
        if not b64_content:
            raise RuntimeError("Failed to encode PDF file")
        
        # Call Mistral OCR API with retry logic
        backoff = settings.RETRY_BACKOFF
        last_error = None
        
        for attempt in range(1, settings.MAX_RETRIES + 1):
            try:
                logger.info(f"Processing document {document_id}, attempt {attempt}")
                
                response = mistral_client.ocr.process(
                    model=settings.OCR_MODEL,
                    document={
                        "type": "document_url",
                        "document_url": f"data:application/pdf;base64,{b64_content}"
                    },
                    include_image_base64=False
                )
                
                # Combine all pages into markdown
                markdown_content = ""
                for page in response.pages:
                    markdown_content += f"## Page {page.index + 1}\n\n"
                    markdown_content += page.markdown + "\n\n"
                
                # Save markdown to file
                output_filename = f"{document.filename.rsplit('.', 1)[0]}_{job.id}.md"
                output_path = os.path.join(settings.EXPORT_DIR, output_filename)
                
                with open(output_path, 'w', encoding='utf-8') as md_file:
                    md_file.write(markdown_content)
                
                # Update job with success
                job.status = JobStatus.COMPLETED
                job.output_path = output_path
                job.markdown_content = markdown_content
                job.completed_at = datetime.now()
                job.error_message = None
                
                # Update document status
                document.status = DocumentStatus.COMPLETED
                document.error_message = None
                
                db.commit()
                db.refresh(job)
                
                logger.info(f"Successfully processed document {document_id}")
                return job
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"Attempt {attempt} failed for document {document_id}: {last_error}")
                
                if attempt < settings.MAX_RETRIES:
                    logger.info(f"Retrying in {backoff} seconds...")
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    raise
        
        # If all retries failed
        raise Exception(f"All {settings.MAX_RETRIES} attempts failed. Last error: {last_error}")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to process document {document_id}: {error_msg}")
        
        # Update job with failure
        job.status = JobStatus.FAILED
        job.error_message = error_msg
        
        # Update document status
        document.status = DocumentStatus.FAILED
        document.error_message = error_msg
        
        db.commit()
        db.refresh(job)
        
        raise


def get_job_status(db: Session, job_id: int) -> Optional[ProcessingJob]:
    """Get processing job status."""
    return db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()

