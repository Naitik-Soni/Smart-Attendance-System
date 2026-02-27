from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models import SystemConfig, SystemHealth
from app.schemas.admin import OperatorCreate, OperatorOut, OperatorUpdate
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import create_user, delete_user, get_user, list_users, update_user


def upsert_org_config(db: Session, organization_id: str, config: dict) -> dict:
    row = (
        db.query(SystemConfig)
        .filter(SystemConfig.organization_id == organization_id, SystemConfig.config_key == "org_config")
        .first()
    )
    if row is None:
        row = SystemConfig(organization_id=organization_id, config_key="org_config", config_value=config)
        db.add(row)
    else:
        row.config_value = config
    db.commit()
    db.refresh(row)
    return {"version": "v1", "updated_at": row.updated_at.isoformat(), "config": row.config_value}


def upsert_system_config(db: Session, organization_id: str, config: dict) -> dict:
    row = (
        db.query(SystemConfig)
        .filter(SystemConfig.organization_id == organization_id, SystemConfig.config_key == "system_config")
        .first()
    )
    if row is None:
        row = SystemConfig(organization_id=organization_id, config_key="system_config", config_value=config)
        db.add(row)
    else:
        row.config_value = config
    db.commit()
    db.refresh(row)
    return {"version": "v1", "updated_at": row.updated_at.isoformat(), "config": row.config_value}


def get_system_health(db: Session) -> dict:
    latest = db.query(SystemHealth).order_by(SystemHealth.recorded_at.desc()).all()
    services = {}
    for row in latest:
        if row.service_name and row.service_name not in services:
            services[row.service_name] = (row.status or "UNKNOWN").lower()

    if not services:
        services = {"api": "healthy", "db": "healthy", "face_engine": "healthy", "storage": "healthy"}

    return {
        "services": services,
        "uptime_seconds": 0,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def add_operator(db: Session, organization_id: str, payload: OperatorCreate) -> OperatorOut:
    created = create_user(
        db,
        organization_id,
        UserCreate(
            user_id=payload.operator_id,
            name=payload.name,
            email=payload.email,
            password=payload.password,
            role="operator",
            status=payload.status,
        ),
    )
    return OperatorOut(
        operator_id=created.user_id,
        name=created.name,
        email=created.email,
        role=created.role,
        status=created.status,
    )


def update_operator(db: Session, organization_id: str, operator_id: str, payload: OperatorUpdate) -> OperatorOut:
    updated = update_user(
        db,
        organization_id,
        operator_id,
        UserUpdate(name=payload.name, email=payload.email, status=payload.status, role="operator"),
    )
    return OperatorOut(
        operator_id=updated.user_id,
        name=updated.name,
        email=updated.email,
        role=updated.role,
        status=updated.status,
    )


def get_operator(db: Session, organization_id: str, operator_id: str) -> OperatorOut:
    out = get_user(db, organization_id, operator_id)
    if out.role != "operator":
        raise AppException(404, "OPERATOR_NOT_FOUND", "Operator not found")
    return OperatorOut(
        operator_id=out.user_id,
        name=out.name,
        email=out.email,
        role=out.role,
        status=out.status,
    )


def delete_operator(db: Session, organization_id: str, operator_id: str) -> None:
    out = get_user(db, organization_id, operator_id)
    if out.role != "operator":
        raise AppException(404, "OPERATOR_NOT_FOUND", "Operator not found")
    delete_user(db, organization_id, operator_id)


def list_operators(db: Session, organization_id: str) -> list[OperatorOut]:
    users = list_users(db, organization_id)
    operators = [u for u in users if u.role == "operator"]
    return [
        OperatorOut(
            operator_id=u.user_id,
            name=u.name,
            email=u.email,
            role=u.role,
            status=u.status,
        )
        for u in operators
    ]
