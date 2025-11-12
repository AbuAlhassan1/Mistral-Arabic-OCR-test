from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.processing_job import JobStatus


class ProcessingJobBase(BaseModel):
    document_id: int
    status: JobStatus = JobStatus.PENDING


class ProcessingJobCreate(ProcessingJobBase):
    pass


class ProcessingJobUpdate(BaseModel):
    status: Optional[JobStatus] = None
    output_path: Optional[str] = None
    markdown_content: Optional[str] = None
    error_message: Optional[str] = None
    attempts: Optional[int] = None
    completed_at: Optional[datetime] = None


class ProcessingJobInDB(ProcessingJobBase):
    id: int
    output_path: Optional[str] = None
    markdown_content: Optional[str] = None
    error_message: Optional[str] = None
    attempts: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProcessingJob(ProcessingJobInDB):
    pass

