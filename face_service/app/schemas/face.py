from datetime import datetime

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    user_id: str = Field(min_length=1)
    image_count: int = Field(ge=3, le=5)


class RecognizeRequest(BaseModel):
    source_type: str
    source_id: str
    timestamp: datetime
    image: str


class FaceResult(BaseModel):
    face_index: int
    status: str
    face_id: str | None = None
    user_id: str | None = None
    embedding_index: int | None = None
    image_path: str | None = None
    confidence: float | None = None
    action: str | None = None
    unknown_id: str | None = None


class RecognizeResponse(BaseModel):
    source_type: str
    results: list[FaceResult]
    errors: list[dict] = []


class RegisterResponse(BaseModel):
    face_id: str
    user_id: str
    face_registered: bool
