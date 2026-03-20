from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import FaceEmbedding, FaceImage
from app.services.policy_service import get_policy


def cleanup_recognition_metadata(db: Session, organization_id: str, retention_days: int | None = None) -> dict:
    keep_days = int(retention_days or get_policy(db, organization_id, "retention.days"))
    cutoff = (datetime.now(timezone.utc) - timedelta(days=keep_days)).replace(tzinfo=None)

    old_unknown_images = (
        db.query(FaceImage)
        .filter(
            FaceImage.organization_id == organization_id,
            FaceImage.image_type == "UNKNOWN",
            FaceImage.captured_at.isnot(None),
            FaceImage.captured_at < cutoff,
        )
        .all()
    )
    image_ids = [row.id for row in old_unknown_images]
    files = [row.file_path for row in old_unknown_images]

    deleted_embeddings = 0
    if image_ids:
        deleted_embeddings = (
            db.query(FaceEmbedding)
            .filter(
                FaceEmbedding.organization_id == organization_id,
                FaceEmbedding.image_id.in_(image_ids),
            )
            .delete(synchronize_session=False)
        )

    deleted_images = 0
    if image_ids:
        deleted_images = (
            db.query(FaceImage)
            .filter(
                FaceImage.organization_id == organization_id,
                FaceImage.id.in_(image_ids),
            )
            .delete(synchronize_session=False)
        )

    db.commit()
    return {
        "retention_days": keep_days,
        "cutoff": cutoff.isoformat(),
        "deleted_images": int(deleted_images),
        "deleted_embeddings": int(deleted_embeddings),
        "deleted_file_paths": files,
    }
