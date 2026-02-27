from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.core.responses import success_response
from app.schemas.admin import (
    OperatorCreate,
    OperatorUpdate,
    OrgConfigBody,
    SystemConfigBody,
)
from app.services import admin_service, audit_service


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/config-org")
@router.patch("/config-org")
def config_org(
    payload: OrgConfigBody,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    data = admin_service.upsert_org_config(db, current_user["organization_id"], payload.model_dump())
    audit_service.write_audit_log(
        db,
        organization_id=current_user["organization_id"],
        user_id=current_user["user_id"],
        action="ORG_CONFIG_UPDATED",
        entity_type="system_config",
        entity_id="org_config",
    )
    return success_response(
        code="CONFIG_UPDATED",
        message="Configuration saved successfully",
        data=data,
    )


@router.post("/system-config")
@router.patch("/system-config")
def system_config(
    payload: SystemConfigBody,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    data = admin_service.upsert_system_config(db, current_user["organization_id"], payload.model_dump())
    audit_service.write_audit_log(
        db,
        organization_id=current_user["organization_id"],
        user_id=current_user["user_id"],
        action="SYSTEM_CONFIG_UPDATED",
        entity_type="system_config",
        entity_id="system_config",
    )
    return success_response(
        code="CONFIG_UPDATED",
        message="Configuration saved successfully",
        data=data,
    )


@router.get("/system-health")
def system_health(_: dict = Depends(require_admin), db: Session = Depends(get_db)):
    data = admin_service.get_system_health(db)
    return success_response(
        code="SYSTEM_HEALTH_OK",
        message="System is healthy",
        data={k: v for k, v in data.items() if k != "checked_at"},
        meta={"checked_at": data["checked_at"]},
    )


@router.post("/operator")
def add_operator(
    payload: OperatorCreate,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    operator = admin_service.add_operator(db, current_user["organization_id"], payload)
    audit_service.write_audit_log(
        db,
        organization_id=current_user["organization_id"],
        user_id=current_user["user_id"],
        action="OPERATOR_CREATED",
        entity_type="user",
        entity_id=operator.operator_id,
    )
    return success_response(
        code="OPERATOR_CREATED",
        message="Operator added successfully",
        data={"operator_id": operator.operator_id},
    )


@router.patch("/operator/{operator_id}")
def update_operator(
    operator_id: str,
    payload: OperatorUpdate,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    updated = admin_service.update_operator(db, current_user["organization_id"], operator_id, payload)
    audit_service.write_audit_log(
        db,
        organization_id=current_user["organization_id"],
        user_id=current_user["user_id"],
        action="OPERATOR_UPDATED",
        entity_type="user",
        entity_id=operator_id,
    )
    return success_response(
        code="OPERATOR_UPDATED",
        message="Operator details updated",
        data={"operator_id": updated.operator_id, "updates": payload.model_dump(exclude_none=True)},
    )


@router.get("/operator/{operator_id}")
def get_operator(
    operator_id: str,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    operator = admin_service.get_operator(db, current_user["organization_id"], operator_id)
    return success_response(
        code="OPERATOR_FETCHED",
        message="Operator details retrieved",
        data=operator.model_dump(),
    )


@router.delete("/operator/{operator_id}")
def delete_operator(
    operator_id: str,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    admin_service.delete_operator(db, current_user["organization_id"], operator_id)
    audit_service.write_audit_log(
        db,
        organization_id=current_user["organization_id"],
        user_id=current_user["user_id"],
        action="OPERATOR_DELETED",
        entity_type="user",
        entity_id=operator_id,
    )
    return success_response(
        code="OPERATOR_DELETED",
        message="Operator deleted successfully",
        data={"operator_id": operator_id},
    )


@router.get("/operators")
def list_operators(current_user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    operators = admin_service.list_operators(db, current_user["organization_id"])
    return success_response(
        code="OPERATORS_LIST",
        message="Operators fetched successfully",
        data=[item.model_dump() for item in operators],
        meta={"total": len(operators), "page": 1, "page_size": 20},
    )
