"""
Attendance models — maps to DB Design § 2
'attendance_records' and 'attendance_logs' tables.
"""

import uuid
from sqlalchemy import (
    Column, String, Integer, Date, Numeric,
    ForeignKey, Index, DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class AttendanceRecord(TimestampMixin, Base):
    """Daily attendance summary per user."""

    __tablename__ = "attendance_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    attendance_date = Column(Date, nullable=False)

    first_in_time = Column(DateTime, nullable=True)
    last_out_time = Column(DateTime, nullable=True)

    total_minutes = Column(Integer, nullable=True)

    source = Column(String(50), nullable=True)       # CAMERA / MANUAL / API
    confidence = Column(Numeric(5, 2), nullable=True)

    # ── Relationships ─────────────────────────────────
    user = relationship("User", back_populates="attendance_records")
    logs = relationship("AttendanceLog", back_populates="record", cascade="all, delete-orphan")

    # ── Indexes ───────────────────────────────────────
    __table_args__ = (
        Index("idx_attendance_user_date", "user_id", "attendance_date"),
    )

    def __repr__(self):
        return f"<AttendanceRecord user={self.user_id} date={self.attendance_date}>"


class AttendanceLog(Base):
    """Individual in/out event linked to a daily record."""

    __tablename__ = "attendance_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attendance_id = Column(
        UUID(as_uuid=True),
        ForeignKey("attendance_records.id"),
        nullable=True,
    )

    event_type = Column(String(10), nullable=False)    # IN / OUT
    event_time = Column(DateTime, nullable=False)

    camera_id = Column(UUID(as_uuid=True), nullable=True)
    confidence = Column(Numeric(5, 2), nullable=True)

    created_at = Column(DateTime, nullable=True)

    # ── Relationships ─────────────────────────────────
    record = relationship("AttendanceRecord", back_populates="logs")

    def __repr__(self):
        return f"<AttendanceLog {self.event_type} @ {self.event_time}>"
