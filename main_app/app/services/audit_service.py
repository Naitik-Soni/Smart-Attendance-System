from datetime import timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import AuditLog, User


def _resolve_actor_uuid(db: Session, actor: str | None) -> UUID | None:
    if actor is None:
        return None
    try:
        return UUID(actor)
    except Exception:
        pass

    user = db.query(User).filter(User.username == actor).first()
    return user.id if user else None


def write_audit_log(
    db: Session,
    *,
    organization_id: str | None,
    user_id: str | None,
    action: str,
    entity_type: str | None = None,
    entity_id: str | None = None,
) -> None:
    db.add(
        AuditLog(
            organization_id=organization_id,
            user_id=_resolve_actor_uuid(db, user_id),
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
        )
    )
    db.commit()


def list_audit_logs(db: Session, organization_id: str, limit: int = 100) -> list[dict]:
    rows = (
        db.query(AuditLog)
        .filter(AuditLog.organization_id == organization_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "action": row.action or "UNKNOWN",
            "actor": str(row.user_id) if row.user_id else "system",
            "timestamp": row.created_at.replace(tzinfo=timezone.utc).isoformat()
            if row.created_at and row.created_at.tzinfo is None
            else (row.created_at.isoformat() if row.created_at else None),
        }
        for row in rows
    ]
