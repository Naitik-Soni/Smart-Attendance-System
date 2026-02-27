import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from ..core.database import Base


class FaceImage(Base):
    __tablename__ = "face_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    image_type = Column(String(20))
    file_path = Column(Text, nullable=False)

    captured_at = Column(DateTime)
    camera_id = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(DateTime, default=func.now())


class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    embedding_index = Column(Integer, nullable=False)
    image_id = Column(UUID(as_uuid=True), ForeignKey("face_images.id"))

    created_at = Column(DateTime, default=func.now())
