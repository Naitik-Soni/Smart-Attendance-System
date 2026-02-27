import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (Index("idx_attendance_user_date", "user_id", "attendance_date"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    attendance_date = Column(Date, nullable=False)

    first_in_time = Column(DateTime)
    last_out_time = Column(DateTime)

    total_minutes = Column(Integer)

    source = Column(String(50))
    confidence = Column(Numeric(5, 2))

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    logs = relationship("AttendanceLog", back_populates="record", cascade="all, delete-orphan")


class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attendance_id = Column(UUID(as_uuid=True), ForeignKey("attendance_records.id"))

    event_type = Column(String(10))
    event_time = Column(DateTime, nullable=False)

    camera_id = Column(UUID(as_uuid=True), nullable=True)
    confidence = Column(Numeric(5, 2))

    created_at = Column(DateTime, default=func.now())

    record = relationship("AttendanceRecord", back_populates="logs")
