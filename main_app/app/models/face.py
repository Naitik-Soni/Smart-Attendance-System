"""
Face-related models — maps to DB Design § 4 and § 5
'face_images' and 'face_embeddings' tables.
"""

import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class FaceImage(Base):
    """Metadata for a stored face image (file lives on filesystem)."""

    __tablename__ = "face_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,   # NULL for unknown faces
    )

    image_type = Column(String(20), nullable=False)    # KNOWN / UNKNOWN
    file_path = Column(Text, nullable=False)

    captured_at = Column(DateTime, nullable=True)
    camera_id = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(DateTime, nullable=True)

    # ── Relationships ─────────────────────────────────
    user = relationship("User", back_populates="face_images")
    embeddings = relationship("FaceEmbedding", back_populates="image")

    def __repr__(self):
        return f"<FaceImage {self.image_type} user={self.user_id}>"


class FaceEmbedding(Base):
    """
    Maps a FAISS index slot back to a user and image.
    Critical for rebuilding the FAISS index if it gets corrupted.
    """

    __tablename__ = "face_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    embedding_index = Column(Integer, nullable=False)   # FAISS index id
    image_id = Column(
        UUID(as_uuid=True),
        ForeignKey("face_images.id"),
        nullable=True,
    )

    created_at = Column(DateTime, nullable=True)

    # ── Relationships ─────────────────────────────────
    user = relationship("User", back_populates="face_embeddings")
    image = relationship("FaceImage", back_populates="embeddings")

    def __repr__(self):
        return f"<FaceEmbedding idx={self.embedding_index} user={self.user_id}>"
