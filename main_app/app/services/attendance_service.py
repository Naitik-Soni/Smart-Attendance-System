from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models import AttendanceLog, AttendanceRecord, User
from app.schemas.ops import AttendanceOut, ManualAttendanceItem


def _find_user(db: Session, organization_id: str, user_id: str) -> User:
    user = (
        db.query(User)
        .filter(
            User.organization_id == organization_id,
            User.username == user_id,
            User.is_deleted.is_(False),
        )
        .first()
    )
    if user is None:
        raise AppException(404, "USER_NOT_FOUND", f"User '{user_id}' not found")
    return user


def mark_manual_attendance(db: Session, organization_id: str, items: list[ManualAttendanceItem]) -> dict:
    processed = 0
    failed = 0

    for item in items:
        try:
            user = _find_user(db, organization_id, item.user_id)
            event_ts = item.timestamp.replace(tzinfo=None)
            attendance_date = event_ts.date()

            record = (
                db.query(AttendanceRecord)
                .filter(
                    AttendanceRecord.organization_id == organization_id,
                    AttendanceRecord.user_id == user.id,
                    AttendanceRecord.attendance_date == attendance_date,
                )
                .first()
            )
            if record is None:
                record = AttendanceRecord(
                    organization_id=organization_id,
                    user_id=user.id,
                    attendance_date=attendance_date,
                    source="MANUAL",
                )
                db.add(record)
                db.flush()

            if item.status.lower() == "present":
                if record.first_in_time is None or event_ts < record.first_in_time:
                    record.first_in_time = event_ts
                if record.last_out_time is None or event_ts > record.last_out_time:
                    record.last_out_time = event_ts
                if record.first_in_time and record.last_out_time:
                    delta = record.last_out_time - record.first_in_time
                    record.total_minutes = max(int(delta.total_seconds() // 60), 0)

            db.add(
                AttendanceLog(
                    attendance_id=record.id,
                    event_type="IN" if item.status.lower() == "present" else "OUT",
                    event_time=event_ts,
                    confidence=None,
                )
            )
            processed += 1
        except AppException:
            failed += 1

    db.commit()
    return {"processed": processed, "failed": failed}


def get_user_attendance(db: Session, organization_id: str, user_id: str) -> list[AttendanceOut]:
    user = _find_user(db, organization_id, user_id)
    records = (
        db.query(AttendanceRecord)
        .filter(
            AttendanceRecord.organization_id == organization_id,
            AttendanceRecord.user_id == user.id,
        )
        .order_by(AttendanceRecord.attendance_date.desc())
        .all()
    )

    result = []
    for row in records:
        status = "present" if row.first_in_time else "absent"
        method = (row.source or "manual").lower()
        result.append(
            AttendanceOut(
                date=row.attendance_date.isoformat(),
                status=status,
                method=method,
            )
        )
    return result
