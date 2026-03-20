from datetime import time

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models import AttendanceLog, AttendanceRecord, User
from app.schemas.ops import AttendanceOut, ManualAttendanceItem
from app.services.policy_service import get_policy


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
    min_time_minutes = int(get_policy(db, organization_id, "attendance.min_time_minutes"))
    windows = get_policy(db, organization_id, "attendance.windows") or []
    late_grace_minutes = int(get_policy(db, organization_id, "attendance.late_grace_minutes"))

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

            status = (item.status or "").lower()
            if status in {"entry", "present"}:
                if record.first_in_time is None or event_ts < record.first_in_time:
                    record.first_in_time = event_ts
            if status in {"exit", "present"}:
                if record.last_out_time is None or event_ts > record.last_out_time:
                    record.last_out_time = event_ts

            if record.first_in_time and record.last_out_time:
                delta = record.last_out_time - record.first_in_time
                record.total_minutes = max(int(delta.total_seconds() // 60), 0)
            record.attendance_status = _calculate_status(
                record.first_in_time,
                record.total_minutes,
                min_time_minutes,
                windows,
                late_grace_minutes,
            )

            db.add(
                AttendanceLog(
                    attendance_id=record.id,
                    event_type="ENTRY" if status in {"entry", "present"} else "EXIT",
                    event_time=event_ts,
                    confidence=None,
                )
            )
            processed += 1
        except AppException:
            failed += 1

    db.commit()
    return {"processed": processed, "failed": failed}


def mark_recognized_attendance(
    db: Session,
    organization_id: str,
    payload: dict,
    event_ts,
    source_type: str,
) -> dict:
    min_time_minutes = int(get_policy(db, organization_id, "attendance.min_time_minutes"))
    windows = get_policy(db, organization_id, "attendance.windows") or []
    late_grace_minutes = int(get_policy(db, organization_id, "attendance.late_grace_minutes"))
    threshold = float(get_policy(db, organization_id, "recognition.threshold"))

    matched_total = 0
    marked = 0
    skipped_low_conf = 0
    skipped_duplicate = 0
    failed = 0

    rows = payload.get("data", {}).get("results", [])
    for row in rows:
        if row.get("status") != "matched":
            continue
        matched_total += 1

        confidence = float(row.get("confidence") or 0.0)
        if confidence <= threshold:
            skipped_low_conf += 1
            continue

        username = row.get("user_id")
        if not username:
            failed += 1
            continue

        try:
            user = _find_user(db, organization_id, username)
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
                    source=(source_type or "UPLOAD_IMAGE").upper(),
                )
                db.add(record)
                db.flush()

            existing_entry = (
                db.query(AttendanceLog)
                .filter(
                    AttendanceLog.attendance_id == record.id,
                    AttendanceLog.event_type == "ENTRY",
                )
                .first()
            )
            if existing_entry is not None:
                skipped_duplicate += 1
                continue

            if record.first_in_time is None or event_ts < record.first_in_time:
                record.first_in_time = event_ts
            if record.last_out_time is None or event_ts > record.last_out_time:
                record.last_out_time = event_ts
            if record.first_in_time and record.last_out_time:
                delta = record.last_out_time - record.first_in_time
                record.total_minutes = max(int(delta.total_seconds() // 60), 0)

            record.attendance_status = _calculate_status(
                record.first_in_time,
                record.total_minutes,
                min_time_minutes,
                windows,
                late_grace_minutes,
            )

            db.add(
                AttendanceLog(
                    attendance_id=record.id,
                    event_type="ENTRY",
                    event_time=event_ts,
                    confidence=confidence,
                )
            )
            marked += 1
        except AppException:
            failed += 1

    db.commit()
    return {
        "matched_total": matched_total,
        "marked": marked,
        "skipped_low_confidence": skipped_low_conf,
        "skipped_duplicate": skipped_duplicate,
        "failed": failed,
    }


def mark_camera_attendance_event(
    db: Session,
    organization_id: str,
    *,
    user_id: str,
    event_type: str,
    event_ts,
    source_type: str,
    confidence: float | None = None,
) -> dict:
    min_time_minutes = int(get_policy(db, organization_id, "attendance.min_time_minutes"))
    windows = get_policy(db, organization_id, "attendance.windows") or []
    late_grace_minutes = int(get_policy(db, organization_id, "attendance.late_grace_minutes"))

    user = _find_user(db, organization_id, user_id)
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
            source=(source_type or "CAMERA").upper(),
        )
        db.add(record)
        db.flush()

    kind = (event_type or "").upper()
    if kind == "ENTRY":
        if record.first_in_time is None or event_ts < record.first_in_time:
            record.first_in_time = event_ts
    elif kind == "EXIT":
        if record.last_out_time is None or event_ts > record.last_out_time:
            record.last_out_time = event_ts
    else:
        raise AppException(400, "INVALID_EVENT_TYPE", f"Unsupported event type '{event_type}'")

    if record.first_in_time and record.last_out_time:
        delta = record.last_out_time - record.first_in_time
        record.total_minutes = max(int(delta.total_seconds() // 60), 0)
    record.attendance_status = _calculate_status(
        record.first_in_time,
        record.total_minutes,
        min_time_minutes,
        windows,
        late_grace_minutes,
    )

    db.add(
        AttendanceLog(
            attendance_id=record.id,
            event_type=kind,
            event_time=event_ts,
            confidence=confidence,
        )
    )
    db.commit()
    return {
        "user_id": user_id,
        "event_type": kind,
        "date": attendance_date.isoformat(),
        "status": record.attendance_status,
        "total_minutes": int(record.total_minutes or 0),
    }


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
        status = row.attendance_status or ("present" if row.first_in_time else "absent")
        method = (row.source or "manual").lower()
        result.append(
            AttendanceOut(
                date=row.attendance_date.isoformat(),
                status=status,
                method=method,
            )
        )
    return result


def _parse_hhmm(value: str) -> time | None:
    if not isinstance(value, str) or ":" not in value:
        return None
    parts = value.split(":")
    if len(parts) != 2:
        return None
    try:
        hour = int(parts[0])
        minute = int(parts[1])
        return time(hour=hour, minute=minute)
    except Exception:
        return None


def _window_for_day(windows: list, weekday: int) -> dict | None:
    for w in windows:
        if not isinstance(w, dict):
            continue
        days = w.get("days")
        if isinstance(days, list) and weekday not in days:
            continue
        start = _parse_hhmm(w.get("start"))
        end = _parse_hhmm(w.get("end"))
        if start and end:
            return {"start": start, "end": end}
    return None


def _calculate_status(
    first_in_time,
    total_minutes: int | None,
    min_time_minutes: int,
    windows: list,
    late_grace_minutes: int,
) -> str:
    if first_in_time is None:
        return "absent"

    total = int(total_minutes or 0)
    if total < min_time_minutes:
        return "partial"

    window = _window_for_day(windows, first_in_time.weekday())
    if window is None:
        return "present"

    start_minutes = window["start"].hour * 60 + window["start"].minute
    first_minutes = first_in_time.hour * 60 + first_in_time.minute
    if first_minutes > (start_minutes + late_grace_minutes):
        return "late"
    return "present"
