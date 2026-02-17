"""
Central model registry — import all models here so Alembic
and SQLAlchemy metadata can auto-discover them.
"""

from app.core.database import Base  # noqa: F401
from app.models.base import TimestampMixin  # noqa: F401

from app.models.organization import Organization  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.user import User, UserProfile  # noqa: F401
from app.models.attendance import AttendanceRecord, AttendanceLog  # noqa: F401
from app.models.face import FaceImage, FaceEmbedding  # noqa: F401
from app.models.audit import AuditLog, SystemLog, SystemHealth  # noqa: F401
from app.models.event import Event, Notification  # noqa: F401
from app.models.config_model import SystemConfig, ApplicationSetting  # noqa: F401
