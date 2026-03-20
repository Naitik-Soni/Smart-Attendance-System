from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import FaceEmbedding, FaceImage, User


def _find_user_uuid(db: Session, organization_id: UUID | str, username: str | None) -> UUID | None:
    if not username:
        return None
    user = (
        db.query(User)
        .filter(
            User.organization_id == organization_id,
            User.username == username,
            User.is_deleted.is_(False),
        )
        .first()
    )
    return user.id if user else None


def persist_registration_metadata(
    db: Session,
    *,
    organization_id: UUID | str,
    user_id: str,
    payload: dict,
) -> dict:
    user_uuid = _find_user_uuid(db, organization_id, user_id)
    persisted = 0

    for item in payload.get("images", []):
        image = FaceImage(
            organization_id=organization_id,
            user_id=user_uuid,
            image_type=item.get("image_type", "KNOWN"),
            file_path=item.get("image_path", ""),
            captured_at=datetime.utcnow(),
        )
        db.add(image)
        db.flush()

        embedding_index = item.get("embedding_index")
        if embedding_index is not None:
            db.add(
                FaceEmbedding(
                    organization_id=organization_id,
                    user_id=user_uuid,
                    embedding_index=int(embedding_index),
                    image_id=image.id,
                )
            )
        persisted += 1

    db.commit()
    return {"images_persisted": persisted}


def persist_recognition_metadata(
    db: Session,
    *,
    organization_id: UUID | str,
    captured_at: datetime,
    payload: dict,
) -> dict:
    persisted_images = 0
    persisted_embeddings = 0

    results = payload.get("data", {}).get("results", [])
    for row in results:
        status = row.get("status")
        image_path = row.get("image_path")
        if not image_path:
            continue

        username = row.get("user_id")
        user_uuid = _find_user_uuid(db, organization_id, username)
        image_type = "KNOWN" if status == "matched" else "UNKNOWN"

        image = FaceImage(
            organization_id=organization_id,
            user_id=user_uuid,
            image_type=image_type,
            file_path=image_path,
            captured_at=captured_at.replace(tzinfo=None),
        )
        db.add(image)
        db.flush()
        persisted_images += 1

        embedding_index = row.get("embedding_index")
        if embedding_index is not None:
            db.add(
                FaceEmbedding(
                    organization_id=organization_id,
                    user_id=user_uuid,
                    embedding_index=int(embedding_index),
                    image_id=image.id,
                )
            )
            persisted_embeddings += 1

    db.commit()
    return {
        "images_persisted": persisted_images,
        "embeddings_persisted": persisted_embeddings,
    }
