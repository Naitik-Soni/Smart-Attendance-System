from pydantic_settings import BaseSettings, SettingsConfigDict

class FaceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Model
    MODEL_PATH: str = "./models/arc.onnx"
    EMBEDDING_DIM: int = 512

    # FAISS
    FAISS_INDEX_PATH: str = "./storage/embeddings/faiss.index"
    FAISS_ID_MAP_PATH: str = "./storage/embeddings/id_map.json"

    # Storage
    STORAGE_ROOT: str = "./storage"

    # Thresholds
    CONFIDENCE_THRESHOLD: float = 0.65


settings = FaceSettings()
