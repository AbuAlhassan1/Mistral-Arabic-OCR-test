# Run database migrations
alembic upgrade head

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

