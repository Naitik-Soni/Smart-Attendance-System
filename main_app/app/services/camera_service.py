from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models import SystemConfig


def _camera_key(camera_id: str) -> str:
    return f"camera.device.{camera_id}"


def upsert_camera(db: Session, organization_id: str, camera: dict) -> dict:
    camera_id = camera["camera_id"]
    key = _camera_key(camera_id)
    row = (
        db.query(SystemConfig)
        .filter(SystemConfig.organization_id == organization_id, SystemConfig.config_key == key)
        .first()
    )
    payload = {
        "camera_id": camera_id,
        "camera_type": camera["camera_type"],
        "source": camera["source"],
        "location": camera.get("location"),
        "gate_id": camera.get("gate_id"),
        "direction": camera.get("direction", "both"),
        "enabled": bool(camera.get("enabled", True)),
    }
    if row is None:
        row = SystemConfig(organization_id=organization_id, config_key=key, config_value=payload)
        db.add(row)
    else:
        row.config_value = payload
    db.commit()
    return payload


def update_camera(db: Session, organization_id: str, camera_id: str, updates: dict) -> dict:
    key = _camera_key(camera_id)
    row = (
        db.query(SystemConfig)
        .filter(SystemConfig.organization_id == organization_id, SystemConfig.config_key == key)
        .first()
    )
    if row is None:
        raise AppException(404, "CAMERA_NOT_FOUND", f"Camera '{camera_id}' not found")
    current = row.config_value or {}
    current.update({k: v for k, v in updates.items() if v is not None})
    current["camera_id"] = camera_id
    row.config_value = current
    db.commit()
    return current


def get_camera(db: Session, organization_id: str, camera_id: str) -> dict:
    key = _camera_key(camera_id)
    row = (
        db.query(SystemConfig)
        .filter(SystemConfig.organization_id == organization_id, SystemConfig.config_key == key)
        .first()
    )
    if row is None:
        raise AppException(404, "CAMERA_NOT_FOUND", f"Camera '{camera_id}' not found")
    return row.config_value or {}


def list_cameras(db: Session, organization_id: str) -> list[dict]:
    rows = (
        db.query(SystemConfig)
        .filter(
            SystemConfig.organization_id == organization_id,
            SystemConfig.config_key.like("camera.device.%"),
        )
        .all()
    )
    return [row.config_value or {} for row in rows]
