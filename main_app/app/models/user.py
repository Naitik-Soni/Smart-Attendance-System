import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..core.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(SmallInteger, primary_key=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_users_org", "organization_id"),
        Index("idx_users_role", "role_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)

    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255))
    password_hash = Column(Text, nullable=False)

    role_id = Column(SmallInteger, ForeignKey("roles.id"), nullable=False)

    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    organization = relationship("Organization", back_populates="users")
    role = relationship("Role", back_populates="users")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)

    full_name = Column(String(255))
    employee_code = Column(String(100))
    department = Column(String(100))
    faiss_user_id = Column(Integer, unique=True, nullable=False)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")
