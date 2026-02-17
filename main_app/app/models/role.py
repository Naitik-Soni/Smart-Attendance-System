"""
Role model — maps to DB Design § 1 'roles' table.

Seed data:
    1 → ADMIN
    2 → OPERATOR
    3 → USER
"""

from sqlalchemy import Column, SmallInteger, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(SmallInteger, primary_key=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # ── Relationships ─────────────────────────────────
    users = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role {self.role_name}>"
