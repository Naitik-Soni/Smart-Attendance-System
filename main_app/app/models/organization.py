"""
Organization model — maps to DB Design § 1 'organizations' table.
"""

import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Organization(TimestampMixin, Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    legal_name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)

    # ── Relationships ─────────────────────────────────
    users = relationship("User", back_populates="organization", lazy="dynamic")
    system_configs = relationship("SystemConfig", back_populates="organization", lazy="dynamic")

    def __repr__(self):
        return f"<Organization {self.code}>"
