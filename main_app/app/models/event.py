import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
import sqlalchemy as sa

from ..core.database import Base


json_type = JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), "sqlite")


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)

    event_type = Column(String(50))
    severity = Column(String(20))

    reference_id = Column(UUID(as_uuid=True), nullable=True)
    metadata_ = Column("metadata", json_type)

    created_at = Column(DateTime, default=func.now())


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"))

    channel = Column(String(20))
    status = Column(String(20))

    created_at = Column(DateTime, default=func.now())
