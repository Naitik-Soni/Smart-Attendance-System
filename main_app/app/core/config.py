from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # ── Application ───────────────────────────────────
    APP_NAME: str = "Smart Attendance System"
    APP_VERSION: str = "1.0.0"

    # ── Database ──────────────────────────────────────
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/smart_attendance"

    # ── Redis ─────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Security / JWT ────────────────────────────────
    SECRET_KEY: str = "change-this-to-a-strong-random-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── Storage (filesystem for face images) ──────────
    STORAGE_ROOT: str = "./storage"

    # ── Face Recognition Service ──────────────────────
    FACE_SERVICE_URL: str = "http://localhost:8001"

    # ── CORS ──────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()