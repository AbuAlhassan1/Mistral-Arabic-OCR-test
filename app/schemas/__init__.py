from app.schemas.document import Document, DocumentCreate, DocumentUpdate, DocumentInDB
from app.schemas.processing_job import ProcessingJob, ProcessingJobCreate, ProcessingJobUpdate, ProcessingJobInDB
from app.schemas.ocr import OCRRequest, OCRResponse, OCRStatus

__all__ = [
    "Document",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentInDB",
    "ProcessingJob",
    "ProcessingJobCreate",
    "ProcessingJobUpdate",
    "ProcessingJobInDB",
    "OCRRequest",
    "OCRResponse",
    "OCRStatus",
]

