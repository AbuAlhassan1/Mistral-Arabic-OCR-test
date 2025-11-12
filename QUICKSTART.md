# Quick Start Guide - FastAPI OCR API

## Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] PostgreSQL installed and running
- [ ] Mistral AI API key obtained

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp env.example .env

# Edit .env and add your Mistral API key
# MISTRAL_API_KEY=your_key_here
```

### 3. Set Up Database

Make sure PostgreSQL is running, then update `.env` with your database credentials:

```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=mistral_ocr
```

### 4. Run Database Migrations

```bash
alembic upgrade head
```

This will create all necessary database tables.

### 5. Start the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Quick Test

### Using curl:

1. **Upload a PDF:**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

2. **Start OCR processing:**
```bash
curl -X POST "http://localhost:8000/api/v1/ocr/process-async" \
  -H "Content-Type: application/json" \
  -d '{"document_id": 1}'
```

3. **Check status:**
```bash
curl "http://localhost:8000/api/v1/jobs/1/status"
```

4. **Download result:**
```bash
curl "http://localhost:8000/api/v1/jobs/1/download" -o result.md
```

### Using Python:

```python
import requests

# Upload document
with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/documents/upload",
        files={"file": f}
    )
document = response.json()
print(f"Document ID: {document['id']}")

# Process OCR
response = requests.post(
    "http://localhost:8000/api/v1/ocr/process-async",
    json={"document_id": document["id"]}
)
job = response.json()
print(f"Job ID: {job['job_id']}")

# Check status (poll until complete)
import time
while True:
    response = requests.get(
        f"http://localhost:8000/api/v1/jobs/{job['job_id']}/status"
    )
    status = response.json()
    print(f"Status: {status['status']}")
    if status['status'] in ['completed', 'failed']:
        break
    time.sleep(2)

# Download result
if status['status'] == 'completed':
    response = requests.get(
        f"http://localhost:8000/api/v1/jobs/{job['job_id']}/download"
    )
    with open("result.md", "wb") as f:
        f.write(response.content)
    print("Result saved to result.md")
```

## Docker Quick Start

```bash
# 1. Copy and configure .env
cp env.example .env
# Edit .env and add MISTRAL_API_KEY

# 2. Start services
docker-compose up -d

# 3. Run migrations
docker-compose exec api alembic upgrade head

# 4. Check logs
docker-compose logs -f api
```

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check database credentials in `.env`
- Verify database exists: `createdb mistral_ocr`

### API Key Error
- Verify `MISTRAL_API_KEY` is set in `.env`
- Check API key is valid and active

### Port Already in Use
- Change port: `uvicorn app.main:app --port 8001`
- Or stop the process using port 8000

### Migration Errors
- Reset database: `alembic downgrade base && alembic upgrade head`
- Check database connection settings

## Next Steps

- Read [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference
- Explore interactive docs at http://localhost:8000/docs
- Check the main [README.md](README.md) for project overview

