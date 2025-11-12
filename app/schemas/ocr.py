from typing import Optional
from pydantic import BaseModel
from app.models.processing_job import JobStatus


class OCRRequest(BaseModel):
    document_id: int


class OCRStatus(BaseModel):
    job_id: int
    document_id: int
    status: JobStatus
    progress: Optional[float] = None
    error_message: Optional[str] = None


class OCRResponse(BaseModel):
    job_id: int
    document_id: int
    status: JobStatus
    markdown_content: Optional[str] = None
    output_path: Optional[str] = None
    error_message: Optional[str] = None

