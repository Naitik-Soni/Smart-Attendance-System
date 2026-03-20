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
    FACE_TECH_ROOT: str = "../Face-Tech"
    RETINAFACE_FALLBACK_TO_HAAR: bool = True

    # FAISS
    FAISS_INDEX_PATH: str = "./storage/embeddings/faiss.index"
    FAISS_ID_MAP_PATH: str = "./storage/embeddings/id_map.json"

    # Storage
    STORAGE_ROOT: str = "./storage"

    # Thresholds
    CONFIDENCE_THRESHOLD: float = 0.8
    WALL_MIN_FACE_AREA_RATIO: float = 0.5
    RETENTION_DAYS: int = 35

    # Enrollment quality gates
    QUALITY_MIN_IMAGE_WIDTH: int = 720
    QUALITY_MIN_IMAGE_HEIGHT: int = 720
    QUALITY_MIN_FACE_WIDTH_PX: int = 112
    QUALITY_MIN_FACE_HEIGHT_PX: int = 112
    QUALITY_MIN_LAPLACIAN_VARIANCE: float = 80.0


settings = FaceSettings()
