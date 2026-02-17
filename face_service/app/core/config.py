from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Application ───────────────────────────────────
    APP_NAME: str = "Face Recognition Service"
    APP_VERSION: str = "1.0.0"

    # ── Model ─────────────────────────────────────────
    MODEL_PATH: str = "./models/arc.onnx"
    EMBEDDING_DIM: int = 512

    # ── FAISS ─────────────────────────────────────────
    FAISS_INDEX_PATH: str = "./storage/embeddings/faiss.index"
    FAISS_ID_MAP_PATH: str = "./storage/embeddings/id_map.json"

    # ── Storage ───────────────────────────────────────
    STORAGE_ROOT: str = "./storage"

    # ── Thresholds ────────────────────────────────────
    CONFIDENCE_THRESHOLD: float = 0.65

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
