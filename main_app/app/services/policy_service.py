from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models import SystemConfig


POLICY_DEFAULTS: dict[str, Any] = {
    "recognition.threshold": 0.8,
    "attendance.min_time_minutes": 480,
    "attendance.windows": [],
    "attendance.late_grace_minutes": 0,
    "retention.days": 35,
    "camera.stream.sampling_fps": 1,
    "camera.wall.min_face_area_ratio": 0.5,
    "enrollment.images.min_count": 3,
    "enrollment.images.max_count": 5,
    "quality.min_image_width": 720,
    "quality.min_image_height": 720,
    "quality.min_face_width_px": 112,
    "quality.min_face_height_px": 112,
    "quality.min_laplacian_variance": 80.0,
    "quality.max_yaw_degrees": 25,
    "quality.max_pitch_degrees": 25,
}


def _must_number(value: Any, key: str) -> float:
    if not isinstance(value, (int, float)):
        raise AppException(422, "POLICY_VALUE_INVALID", f"Policy '{key}' must be numeric")
    return float(value)


def _validate_policy_value(key: str, value: Any) -> None:
    if key not in POLICY_DEFAULTS:
        raise AppException(404, "POLICY_KEY_NOT_FOUND", f"Policy '{key}' is not supported")

    if key in {"recognition.threshold", "camera.wall.min_face_area_ratio"}:
        n = _must_number(value, key)
        if n <= 0 or n > 1:
            raise AppException(422, "POLICY_VALUE_INVALID", f"Policy '{key}' must be in range (0, 1]")
        return

    if key in {
        "attendance.min_time_minutes",
        "attendance.late_grace_minutes",
        "retention.days",
        "camera.stream.sampling_fps",
        "enrollment.images.min_count",
        "enrollment.images.max_count",
        "quality.min_image_width",
        "quality.min_image_height",
        "quality.min_face_width_px",
        "quality.min_face_height_px",
        "quality.max_yaw_degrees",
        "quality.max_pitch_degrees",
    }:
        n = _must_number(value, key)
        if n < 0 or int(n) != n:
            raise AppException(422, "POLICY_VALUE_INVALID", f"Policy '{key}' must be a non-negative integer")
        return

    if key == "quality.min_laplacian_variance":
        n = _must_number(value, key)
        if n < 0:
            raise AppException(422, "POLICY_VALUE_INVALID", f"Policy '{key}' must be >= 0")
        return

    if key == "attendance.windows":
        if not isinstance(value, list):
            raise AppException(422, "POLICY_VALUE_INVALID", "Policy 'attendance.windows' must be a list")
        return


def _set_policy(db: Session, organization_id: str, key: str, value: Any) -> SystemConfig:
    row = (
        db.query(SystemConfig)
        .filter(SystemConfig.organization_id == organization_id, SystemConfig.config_key == key)
        .first()
    )
    if row is None:
        row = SystemConfig(organization_id=organization_id, config_key=key, config_value=value)
        db.add(row)
    else:
        row.config_value = value
    return row


def upsert_policies(db: Session, organization_id: str, policies: dict[str, Any]) -> dict[str, Any]:
    if not policies:
        raise AppException(422, "POLICY_VALUE_INVALID", "At least one policy key/value is required")

    for key, value in policies.items():
        _validate_policy_value(key, value)
        _set_policy(db, organization_id, key, value)

    db.commit()
    return get_effective_policies(db, organization_id)


def get_effective_policies(db: Session, organization_id: str) -> dict[str, Any]:
    rows = db.query(SystemConfig).filter(SystemConfig.organization_id == organization_id).all()
    values = {row.config_key: row.config_value for row in rows}
    merged = dict(POLICY_DEFAULTS)
    merged.update(values)
    return merged


def get_policy(db: Session, organization_id: str, key: str) -> Any:
    if key not in POLICY_DEFAULTS:
        raise AppException(404, "POLICY_KEY_NOT_FOUND", f"Policy '{key}' is not supported")
    row = (
        db.query(SystemConfig)
        .filter(SystemConfig.organization_id == organization_id, SystemConfig.config_key == key)
        .first()
    )
    if row is None:
        return POLICY_DEFAULTS[key]
    return row.config_value
