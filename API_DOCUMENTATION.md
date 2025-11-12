# FastAPI API Documentation

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Mistral AI API Key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Pythonation/Mistral-Arabic-OCR-test.git
cd Mistral-Arabic-OCR-test
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp env.example .env
# Edit .env and add your MISTRAL_API_KEY
```

4. **Set up database**
```bash
# Make sure PostgreSQL is running
# Update .env with your database credentials
```

5. **Run migrations**
```bash
alembic upgrade head
```

6. **Start the server**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Using Docker

```bash
# Copy env.example to .env and configure
cp env.example .env

# Start services
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head
```

## 📚 API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Interactive Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 📄 Documents Endpoints

### Upload Document
**POST** `/documents/upload`

Upload a PDF file for OCR processing.

**Request:**
- Content-Type: `multipart/form-data`
- Body: PDF file (max 50MB)

**Response:**
```json
{
  "id": 1,
  "filename": "uuid.pdf",
  "original_filename": "document.pdf",
  "file_path": "uploads/uuid.pdf",
  "file_size": 1024000,
  "status": "uploaded",
  "error_message": null,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

---

### List Documents
**GET** `/documents/`

Get a list of all uploaded documents.

**Query Parameters:**
- `skip` (int, default: 0): Number of records to skip
- `limit` (int, default: 100): Maximum number of records to return

**Response:**
```json
[
  {
    "id": 1,
    "filename": "uuid.pdf",
    "original_filename": "document.pdf",
    "file_size": 1024000,
    "status": "uploaded",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

---

### Get Document
**GET** `/documents/{document_id}`

Get details of a specific document.

**Response:**
```json
{
  "id": 1,
  "filename": "uuid.pdf",
  "original_filename": "document.pdf",
  "file_path": "uploads/uuid.pdf",
  "file_size": 1024000,
  "status": "completed",
  "error_message": null,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

---

### Delete Document
**DELETE** `/documents/{document_id}`

Delete a document and its associated files.

**Response:** 204 No Content

---

## 🔍 OCR Endpoints

### Process Document (Synchronous)
**POST** `/ocr/process`

Start OCR processing for a document. This endpoint processes the document immediately and returns the result.

**Request:**
```json
{
  "document_id": 1
}
```

**Response:**
```json
{
  "job_id": 1,
  "document_id": 1,
  "status": "completed",
  "markdown_content": "## Page 1\n\n...",
  "output_path": "exports/document_1.md",
  "error_message": null
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/ocr/process" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"document_id": 1}'
```

---

### Process Document (Asynchronous)
**POST** `/ocr/process-async`

Start OCR processing for a document asynchronously. Returns immediately with a job ID.

**Request:**
```json
{
  "document_id": 1
}
```

**Response:**
```json
{
  "job_id": 1,
  "document_id": 1,
  "status": "pending"
}
```

---

## 📊 Jobs Endpoints

### Get Job Status
**GET** `/jobs/{job_id}`

Get full details of a processing job.

**Response:**
```json
{
  "id": 1,
  "document_id": 1,
  "status": "completed",
  "output_path": "exports/document_1.md",
  "markdown_content": "## Page 1\n\n...",
  "error_message": null,
  "attempts": 1,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "completed_at": "2024-01-01T00:05:00"
}
```

---

### Get Job Status (Simple)
**GET** `/jobs/{job_id}/status`

Get simplified status of a processing job.

**Response:**
```json
{
  "job_id": 1,
  "document_id": 1,
  "status": "completed",
  "error_message": null
}
```

---

### Download Result
**GET** `/jobs/{job_id}/download`

Download the markdown result file.

**Response:** File download (text/markdown)

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/jobs/1/download" \
  -o result.md
```

---

### Get Document Jobs
**GET** `/jobs/document/{document_id}`

Get all processing jobs for a specific document.

**Response:**
```json
[
  {
    "id": 1,
    "document_id": 1,
    "status": "completed",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

---

## 📋 Status Values

### Document Status
- `uploaded`: Document uploaded successfully
- `processing`: OCR processing in progress
- `completed`: OCR processing completed successfully
- `failed`: OCR processing failed

### Job Status
- `pending`: Job created, waiting to be processed
- `processing`: OCR processing in progress
- `completed`: OCR processing completed successfully
- `failed`: OCR processing failed

---

## 🔄 Typical Workflow

1. **Upload a PDF document**
   ```bash
   POST /api/v1/documents/upload
   ```
   Returns: `document_id`

2. **Start OCR processing (async)**
   ```bash
   POST /api/v1/ocr/process-async
   Body: {"document_id": 1}
   ```
   Returns: `job_id`

3. **Check job status**
   ```bash
   GET /api/v1/jobs/{job_id}/status
   ```
   Poll until `status` is `completed` or `failed`

4. **Download result**
   ```bash
   GET /api/v1/jobs/{job_id}/download
   ```

---

## 🐛 Error Handling

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `201 Created`: Resource created successfully
- `202 Accepted`: Request accepted for processing
- `400 Bad Request`: Invalid request
- `404 Not Found`: Resource not found
- `413 Payload Too Large`: File exceeds size limit
- `500 Internal Server Error`: Server error

Error responses include a `detail` field with error message:
```json
{
  "detail": "Document 1 not found"
}
```

---

## 🔒 Environment Variables

See `env.example` for all available configuration options.

**Required:**
- `MISTRAL_API_KEY`: Your Mistral AI API key

**Optional:**
- Database configuration (defaults to local PostgreSQL)
- CORS origins
- File upload settings
- OCR retry settings

---

## 🧪 Testing

You can test the API using:
- Swagger UI at `/docs`
- curl commands (see examples above)
- Postman or any HTTP client
- Python `requests` library

**Example Python client:**
```python
import requests

# Upload document
with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/documents/upload",
        files={"file": f}
    )
document = response.json()
document_id = document["id"]

# Process OCR
response = requests.post(
    "http://localhost:8000/api/v1/ocr/process-async",
    json={"document_id": document_id}
)
job = response.json()
job_id = job["job_id"]

# Check status
response = requests.get(f"http://localhost:8000/api/v1/jobs/{job_id}/status")
print(response.json())
```

---

## 📝 Notes

- The API uses PostgreSQL for data persistence
- Uploaded files are stored in the `uploads/` directory
- Processed markdown files are stored in the `exports/` directory
- OCR processing includes automatic retry logic (configurable)
- All timestamps are in UTC timezone

