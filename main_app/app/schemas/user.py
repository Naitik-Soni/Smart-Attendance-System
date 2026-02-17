"""
User schemas — matches Api.md § 2.4-2.8 (Operator) and § 3.1-3.5 (User CRUD).
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


# ── Requests ──────────────────────────────────────────

class CreateUserRequest(BaseModel):
    """Used by both Add Operator (§ 2.4) and Add User (§ 3.1)."""
    username: str
    name: str
    email: Optional[str] = None
    password: str
    role: str                          # "ADMIN" | "OPERATOR" | "USER"
    department: Optional[str] = None
    employee_code: Optional[str] = None


class UpdateUserRequest(BaseModel):
    """Used by Update Operator (§ 2.5) and Update User (§ 3.3)."""
    name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None       # "active" | "inactive"
    department: Optional[str] = None
    employee_code: Optional[str] = None


# ── Responses ─────────────────────────────────────────

class UserOut(BaseModel):
    user_id: str
    username: str
    name: Optional[str] = None
    email: Optional[str] = None
    role: str
    status: str
    department: Optional[str] = None
    employee_code: Optional[str] = None

    class Config:
        from_attributes = True


class UserBrief(BaseModel):
    """Compact user row for list endpoints."""
    user_id: str
    name: Optional[str] = None
    status: str

    class Config:
        from_attributes = True
