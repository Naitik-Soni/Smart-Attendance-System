from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/smart_attendance"

    # Security
    SECRET_KEY: str = "change-this-to-a-strong-random-secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Face Service
    FACE_SERVICE_URL: str = "http://localhost:8001"

    # Storage
    STORAGE_ROOT: str = "./storage"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]


settings = Settings()
