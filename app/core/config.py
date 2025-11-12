from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "Mistral OCR API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Mistral API
    MISTRAL_API_KEY: str
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "mistral_ocr"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        # Use SQLite for local development if PostgreSQL is not available
        # Override by setting SQLALCHEMY_DATABASE_URI in .env
        return f"sqlite:///./mistral_ocr.db"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"
    EXPORT_DIR: str = "exports"
    
    # OCR Settings
    OCR_MODEL: str = "mistral-ocr-latest"
    MAX_RETRIES: int = 5
    RETRY_BACKOFF: int = 1
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

