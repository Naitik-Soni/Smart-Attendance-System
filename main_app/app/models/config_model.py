"""
Configuration models — maps to DB Design § 6
'system_configs' and 'application_settings' tables.
"""

import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base
from app.models.base import TimestampMixin


class SystemConfig(TimestampMixin, Base):
    """Organization-scoped key-value configs (cached in Redis)."""

    __tablename__ = "system_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=True,
    )

    config_key = Column(String(100), nullable=False)
    config_value = Column(JSONB, nullable=True)

    # ── Relationships ─────────────────────────────────
    from sqlalchemy.orm import relationship
    organization = relationship("Organization", back_populates="system_configs")

    # ── Constraints ───────────────────────────────────
    __table_args__ = (
        UniqueConstraint("organization_id", "config_key", name="uq_org_config_key"),
    )

    def __repr__(self):
        return f"<SystemConfig {self.config_key}>"


class ApplicationSetting(Base):
    """Global application-level settings (not org-scoped)."""

    __tablename__ = "application_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(JSONB, nullable=True)

    updated_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<ApplicationSetting {self.setting_key}>"
