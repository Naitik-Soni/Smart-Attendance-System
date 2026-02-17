"""
User / Operations routes — Api.md § 3 (Operations APIs).

Endpoints:
  POST   /user          — Add user (§ 3.1)
  GET    /users         — List users (§ 3.2)
  PATCH  /user/{id}     — Update user (§ 3.3)
  DELETE /user/{id}     — Delete user (§ 3.4)
  GET    /get-user/{id} — Get user details (§ 3.5)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.schemas.user import CreateUserRequest, UpdateUserRequest
from app.schemas.common import success_response, error_response
from app.services.user_service import (
    create_user, get_user_by_username, update_user, delete_user, list_users,
)

router = APIRouter()


# ── Add User (§ 3.1) ─────────────────────────────────

@router.post("/user")
def add_user(
    body: CreateUserRequest,
    current_user: User = Depends(require_role("ADMIN", "OPERATOR")),
    db: Session = Depends(get_db),
):
    data, error = create_user(
        db,
        organization_id=current_user.organization_id,
        username=body.username,
        password=body.password,
        role_name=body.role.upper(),
        name=body.name,
        email=body.email,
        department=body.department,
        employee_code=body.employee_code,
    )
    if error:
        return error_response(code="USER_CREATE_FAILED", message=error)

    return success_response(
        code="USER_CREATED",
        message="User added successfully",
        data={"user_id": data["user_id"]},
    )


# ── List Users (§ 3.2) ───────────────────────────────

@router.get("/users")
def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role("ADMIN", "OPERATOR")),
    db: Session = Depends(get_db),
):
    users, total = list_users(
        db,
        organization_id=current_user.organization_id,
        page=page,
        page_size=page_size,
    )

    return success_response(
        code="USERS_LIST",
        message="Users fetched successfully",
        data=users,
        meta={"total": total, "page": page, "page_size": page_size},
    )


# ── Update User (§ 3.3) ──────────────────────────────

@router.patch("/user/{user_id}")
def modify_user(
    user_id: str,
    body: UpdateUserRequest,
    current_user: User = Depends(require_role("ADMIN", "OPERATOR")),
    db: Session = Depends(get_db),
):
    data, error = update_user(
        db,
        username=user_id,
        name=body.name,
        email=body.email,
        status=body.status,
        department=body.department,
        employee_code=body.employee_code,
    )
    if error:
        return error_response(code="USER_UPDATE_FAILED", message=error)

    return success_response(
        code="USER_UPDATED",
        message="User details updated",
        data={"user_id": data["user_id"]},
    )


# ── Delete User (§ 3.4) ──────────────────────────────

@router.delete("/user/{user_id}")
def remove_user(
    user_id: str,
    current_user: User = Depends(require_role("ADMIN", "OPERATOR")),
    db: Session = Depends(get_db),
):
    error = delete_user(db, user_id)
    if error:
        return error_response(code="USER_DELETE_FAILED", message=error)

    return success_response(
        code="USER_DELETED",
        message="User deleted successfully",
    )


# ── Get User Details (§ 3.5) ─────────────────────────

@router.get("/get-user/{user_id}")
def get_user_detail(
    user_id: str,
    current_user: User = Depends(require_role("ADMIN", "OPERATOR")),
    db: Session = Depends(get_db),
):
    data = get_user_by_username(db, user_id)
    if data is None:
        return error_response(code="USER_NOT_FOUND", message="User not found")

    return success_response(
        code="USER_FETCHED",
        message="User details retrieved",
        data=data,
    )
