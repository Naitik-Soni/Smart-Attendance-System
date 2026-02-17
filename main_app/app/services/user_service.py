"""
User service — CRUD operations for users and operators.
Controllers call this; this talks to DB.
"""

import uuid
from typing import Optional, List, Tuple

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User, UserProfile
from app.models.role import Role


# ── Helpers ───────────────────────────────────────────

def _get_role_by_name(db: Session, role_name: str) -> Role | None:
    return db.query(Role).filter(Role.role_name == role_name.upper()).first()


def _next_faiss_user_id(db: Session) -> int:
    """Generate the next sequential FAISS user id."""
    max_id = db.query(UserProfile.faiss_user_id).order_by(
        UserProfile.faiss_user_id.desc()
    ).first()
    return (max_id[0] + 1) if max_id else 1


def _user_to_dict(user: User) -> dict:
    """Convert a User ORM object to the Api.md response shape."""
    profile = user.profile
    return {
        "user_id": user.username,
        "username": user.username,
        "name": profile.full_name if profile else None,
        "email": user.email,
        "role": user.role.role_name.lower(),
        "status": "active" if user.is_active else "inactive",
        "department": profile.department if profile else None,
        "employee_code": profile.employee_code if profile else None,
    }


# ── Create ────────────────────────────────────────────

def create_user(
    db: Session,
    organization_id: uuid.UUID,
    username: str,
    password: str,
    role_name: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    department: Optional[str] = None,
    employee_code: Optional[str] = None,
) -> Tuple[dict | None, str | None]:
    """
    Create a user + profile.
    Returns (user_dict, None) on success or (None, error_message) on failure.
    """
    # Check unique username
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return None, "Username already exists"

    role = _get_role_by_name(db, role_name)
    if role is None:
        return None, f"Role '{role_name}' not found"

    user = User(
        organization_id=organization_id,
        username=username,
        email=email,
        password_hash=hash_password(password),
        role_id=role.id,
    )
    db.add(user)
    db.flush()  # get user.id before creating profile

    profile = UserProfile(
        user_id=user.id,
        full_name=name,
        department=department,
        employee_code=employee_code,
        faiss_user_id=_next_faiss_user_id(db),
    )
    db.add(profile)
    db.commit()
    db.refresh(user)

    return _user_to_dict(user), None


# ── Read ──────────────────────────────────────────────

def get_user_by_username(db: Session, username: str) -> dict | None:
    user = (
        db.query(User)
        .filter(User.username == username, User.is_deleted.is_(False))
        .first()
    )
    return _user_to_dict(user) if user else None


def get_user_by_id(db: Session, user_id: uuid.UUID) -> dict | None:
    user = (
        db.query(User)
        .filter(User.id == user_id, User.is_deleted.is_(False))
        .first()
    )
    return _user_to_dict(user) if user else None


def list_users(
    db: Session,
    organization_id: uuid.UUID,
    role_name: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[dict], int]:
    """
    List users for an organization, optionally filtered by role.
    Returns (list_of_user_dicts, total_count).
    """
    query = db.query(User).filter(
        User.organization_id == organization_id,
        User.is_deleted.is_(False),
    )

    if role_name:
        role = _get_role_by_name(db, role_name)
        if role:
            query = query.filter(User.role_id == role.id)

    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()

    return [_user_to_dict(u) for u in users], total


# ── Update ────────────────────────────────────────────

def update_user(
    db: Session,
    username: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    status: Optional[str] = None,
    department: Optional[str] = None,
    employee_code: Optional[str] = None,
) -> Tuple[dict | None, str | None]:
    """Update user fields. Returns (user_dict, None) or (None, error)."""
    user = (
        db.query(User)
        .filter(User.username == username, User.is_deleted.is_(False))
        .first()
    )
    if user is None:
        return None, "User not found"

    if email is not None:
        user.email = email
    if status is not None:
        user.is_active = (status.lower() == "active")

    profile = user.profile
    if profile:
        if name is not None:
            profile.full_name = name
        if department is not None:
            profile.department = department
        if employee_code is not None:
            profile.employee_code = employee_code

    db.commit()
    db.refresh(user)
    return _user_to_dict(user), None


# ── Delete (soft) ─────────────────────────────────────

def delete_user(db: Session, username: str) -> str | None:
    """Soft-delete a user. Returns None on success or error message."""
    user = (
        db.query(User)
        .filter(User.username == username, User.is_deleted.is_(False))
        .first()
    )
    if user is None:
        return "User not found"

    user.is_deleted = True
    user.is_active = False
    db.commit()
    return None
