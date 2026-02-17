"""
User and UserProfile models — maps to DB Design § 1
'users' and 'user_profiles' tables.
"""

import uuid
from sqlalchemy import (
    Column, String, Boolean, SmallInteger, Integer, Text,
    ForeignKey, Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )

    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), nullable=True)
    password_hash = Column(Text, nullable=False)

    role_id = Column(SmallInteger, ForeignKey("roles.id"), nullable=False)

    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)

    # ── Relationships ─────────────────────────────────
    organization = relationship("Organization", back_populates="users")
    role = relationship("Role", back_populates="users", lazy="joined")
    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    attendance_records = relationship("AttendanceRecord", back_populates="user", lazy="dynamic")
    face_images = relationship("FaceImage", back_populates="user", lazy="dynamic")
    face_embeddings = relationship("FaceEmbedding", back_populates="user", lazy="dynamic")

    # ── Indexes (matching DB Design) ──────────────────
    __table_args__ = (
        Index("idx_users_org", "organization_id"),
        Index("idx_users_role", "role_id"),
    )

    def __repr__(self):
        return f"<User {self.username}>"


class UserProfile(TimestampMixin, Base):
    __tablename__ = "user_profiles"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=True,
    )

    full_name = Column(String(255), nullable=True)
    employee_code = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    faiss_user_id = Column(Integer, unique=True, nullable=False)

    # ── Relationships ─────────────────────────────────
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile {self.full_name}>"
