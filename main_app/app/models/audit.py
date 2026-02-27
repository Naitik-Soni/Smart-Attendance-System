from sqlalchemy import Column, DateTime, Numeric, BigInteger, String, Text
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.sql import func
import sqlalchemy as sa

from ..core.database import Base


json_type = JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), "sqlite")
inet_type = INET().with_variant(sa.String(length=45), "sqlite")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)

    action = Column(String(100))
    entity_type = Column(String(100))
    entity_id = Column(String(100))

    ip_address = Column(inet_type)
    user_agent = Column(Text)

    created_at = Column(DateTime, default=func.now())


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    log_level = Column(String(20))
    service_name = Column(String(100))

    message = Column(Text)
    metadata_ = Column("metadata", json_type)

    created_at = Column(DateTime, default=func.now())


class SystemHealth(Base):
    __tablename__ = "system_health"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    service_name = Column(String(100))
    status = Column(String(20))

    cpu_usage = Column(Numeric(5, 2))
    memory_usage = Column(Numeric(5, 2))

    recorded_at = Column(DateTime, default=func.now())
