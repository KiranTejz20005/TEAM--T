"""
Configuration settings for FinMDA-Bot application.
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "FinMDA-Bot"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # API Keys
    gemini_api_key: str = "default-key-change-in-env"
    
    # Database
    database_url: str = "sqlite:///./finmda.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # File Upload
    max_file_size_mb: int = 50
    allowed_file_types: List[str] = ["pdf", "xlsx", "xls", "csv"]
    upload_directory: str = "./uploads"
    
    # ChromaDB
    chroma_persist_directory: str = "./chromadb"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # CORS
    cors_origins: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

