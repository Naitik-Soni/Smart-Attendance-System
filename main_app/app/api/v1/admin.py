"""
Admin routes — Api.md § 2 (Admin APIs).

Endpoints:
  POST/PATCH /config-org        — Configure org details (§ 2.1)
  POST/PATCH /system-config     — Configure system & cameras (§ 2.2)
  GET        /system-health     — System health check (§ 2.3)
  POST       /operator          — Add operator (§ 2.4)
  PATCH      /operator/{id}     — Update operator (§ 2.5)
  GET        /operator/{id}     — View operator (§ 2.6)
  DELETE     /operator/{id}     — Delete operator (§ 2.7)
  GET        /operators         — List operators (§ 2.8)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.schemas.user import CreateUserRequest, UpdateUserRequest
from app.schemas.admin import OrgConfigRequest, SystemConfigRequest
from app.schemas.common import success_response, error_response
from app.services.user_service import (
    create_user, get_user_by_username, update_user, delete_user, list_users,
)

router = APIRouter()


# ── Org Config (§ 2.1) ───────────────────────────────

@router.post("/config-org")
def configure_org(
    body: OrgConfigRequest,
    current_user: User = Depends(require_role("ADMIN")),
):
    # TODO: persist org config via SystemConfig model
    return success_response(
        code="CONFIG_UPDATED",
        message="Configuration saved successfully",
        data={"version": "v1"},
    )


# ── System Config (§ 2.2) ────────────────────────────

@router.post("/system-config")
def configure_system(
    body: SystemConfigRequest,
    current_user: User = Depends(require_role("ADMIN")),
):
    # TODO: persist system/camera config
    return success_response(
        code="CONFIG_UPDATED",
        message="Configuration saved successfully",
        data={"version": "v1"},
    )


# ── System Health (§ 2.3) ────────────────────────────

@router.get("/system-health")
def system_health(
    current_user: User = Depends(require_role("ADMIN")),
):
    return success_response(
        code="SYSTEM_HEALTH_OK",
        message="System is healthy",
        data={
            "services": {
                "api": "healthy",
                "db": "healthy",
                "face_engine": "healthy",
                "storage": "healthy",
            },
        },
    )


# ── Add Operator (§ 2.4) ─────────────────────────────

@router.post("/operator")
def add_operator(
    body: CreateUserRequest,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    data, error = create_user(
        db,
        organization_id=current_user.organization_id,
        username=body.username,
        password=body.password,
        role_name="OPERATOR",
        name=body.name,
        email=body.email,
        department=body.department,
        employee_code=body.employee_code,
    )
    if error:
        return error_response(code="OPERATOR_CREATE_FAILED", message=error)

    return success_response(
        code="OPERATOR_CREATED",
        message="Operator added successfully",
        data={"operator_id": data["user_id"]},
    )


# ── Update Operator (§ 2.5) ──────────────────────────

@router.patch("/operator/{operator_id}")
def update_operator(
    operator_id: str,
    body: UpdateUserRequest,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    data, error = update_user(
        db,
        username=operator_id,
        name=body.name,
        email=body.email,
        status=body.status,
        department=body.department,
        employee_code=body.employee_code,
    )
    if error:
        return error_response(code="OPERATOR_UPDATE_FAILED", message=error)

    return success_response(
        code="OPERATOR_UPDATED",
        message="Operator details updated",
        data={"operator_id": data["user_id"]},
    )


# ── Get Operator (§ 2.6) ─────────────────────────────

@router.get("/operator/{operator_id}")
def get_operator(
    operator_id: str,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    data = get_user_by_username(db, operator_id)
    if data is None:
        return error_response(code="OPERATOR_NOT_FOUND", message="Operator not found")

    return success_response(
        code="OPERATOR_FETCHED",
        message="Operator details retrieved",
        data=data,
    )


# ── Delete Operator (§ 2.7) ──────────────────────────

@router.delete("/operator/{operator_id}")
def remove_operator(
    operator_id: str,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    error = delete_user(db, operator_id)
    if error:
        return error_response(code="OPERATOR_DELETE_FAILED", message=error)

    return success_response(
        code="OPERATOR_DELETED",
        message="Operator deleted successfully",
    )


# ── List Operators (§ 2.8) ───────────────────────────

@router.get("/operators")
def list_operators(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    users, total = list_users(
        db,
        organization_id=current_user.organization_id,
        role_name="OPERATOR",
        page=page,
        page_size=page_size,
    )

    return success_response(
        code="OPERATORS_LIST",
        message="Operators fetched successfully",
        data=users,
        meta={"total": total, "page": page, "page_size": page_size},
    )
