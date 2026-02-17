"""
Audit and system log models — maps to DB Design § 3
'audit_logs', 'system_logs', and 'system_health' tables.
"""

from sqlalchemy import (
    Column, BigInteger, String, Text, Numeric, DateTime,
)
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB

from app.core.database import Base


class AuditLog(Base):
    """Tracks who did what and when — security-critical, append-only."""

    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)

    action = Column(String(100), nullable=True)
    entity_type = Column(String(100), nullable=True)
    entity_id = Column(String(100), nullable=True)

    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_id}>"


class SystemLog(Base):
    """Service-level log entries with optional JSON metadata."""

    __tablename__ = "system_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    log_level = Column(String(20), nullable=True)    # INFO / WARN / ERROR
    service_name = Column(String(100), nullable=True)

    message = Column(Text, nullable=True)
    extra_metadata = Column("metadata", JSONB, nullable=True)

    created_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<SystemLog [{self.log_level}] {self.service_name}>"


class SystemHealth(Base):
    """Periodic health snapshots for monitoring."""

    __tablename__ = "system_health"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    service_name = Column(String(100), nullable=True)
    status = Column(String(20), nullable=True)       # UP / DOWN / DEGRADED

    cpu_usage = Column(Numeric(5, 2), nullable=True)
    memory_usage = Column(Numeric(5, 2), nullable=True)

    recorded_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<SystemHealth {self.service_name}: {self.status}>"
