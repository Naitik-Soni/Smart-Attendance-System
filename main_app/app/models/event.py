"""
Event and notification models — maps to DB Design § 7
'events' and 'notifications' tables.
"""

import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class Event(Base):
    """
    Immutable facts emitted by the system.
    Examples: UNKNOWN_FACE_DETECTED, CAMERA_OFFLINE, LOW_CONFIDENCE_MATCH.
    """

    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=True,
    )

    event_type = Column(String(50), nullable=False)    # UNKNOWN_FACE, LOW_CONFIDENCE, etc.
    severity = Column(String(20), nullable=True)

    reference_id = Column(UUID(as_uuid=True), nullable=True)  # face_image_id, attendance_id, etc.
    extra_metadata = Column("metadata", JSONB, nullable=True)

    created_at = Column(DateTime, nullable=True)

    # ── Relationships ─────────────────────────────────
    notifications = relationship("Notification", back_populates="event", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Event {self.event_type}>"


class Notification(Base):
    """Delivery tracking for a given event (per channel)."""

    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(
        UUID(as_uuid=True),
        ForeignKey("events.id"),
        nullable=True,
    )

    channel = Column(String(20), nullable=True)   # EMAIL / SMS / DASHBOARD
    status = Column(String(20), nullable=True)     # SENT / FAILED / PENDING

    created_at = Column(DateTime, nullable=True)

    # ── Relationships ─────────────────────────────────
    event = relationship("Event", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.channel}: {self.status}>"
