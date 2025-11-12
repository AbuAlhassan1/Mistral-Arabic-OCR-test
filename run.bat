@echo off
echo Running database migrations...
alembic upgrade head

echo Starting FastAPI server...
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

