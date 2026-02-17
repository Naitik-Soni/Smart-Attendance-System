"""
Attendance service — business logic for attendance records.
Controllers call this; this talks to DB.
"""

import uuid
from datetime import date, datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.attendance import AttendanceRecord, AttendanceLog
from app.models.user import User


def mark_manual_attendance(
    db: Session,
    organization_id: uuid.UUID,
    entries: list,
) -> Tuple[int, int]:
    """
    Process a batch of manual attendance entries (Api.md § 3.7).
    Returns (processed_count, failed_count).
    """
    processed = 0
    failed = 0

    for entry in entries:
        try:
            user = (
                db.query(User)
                .filter(User.username == entry.user_id, User.is_deleted.is_(False))
                .first()
            )
            if user is None:
                failed += 1
                continue

            attendance_date = entry.timestamp.date()

            # Find or create the daily record
            record = (
                db.query(AttendanceRecord)
                .filter(
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
                    first_in_time=entry.timestamp,
                    source="MANUAL",
                )
                db.add(record)
                db.flush()

            # Update first_in / last_out
            if record.first_in_time is None or entry.timestamp < record.first_in_time:
                record.first_in_time = entry.timestamp
            if record.last_out_time is None or entry.timestamp > record.last_out_time:
                record.last_out_time = entry.timestamp

            # Add individual log
            log = AttendanceLog(
                attendance_id=record.id,
                event_type="IN",
                event_time=entry.timestamp,
                created_at=datetime.now(timezone.utc),
            )
            db.add(log)
            processed += 1

        except Exception:
            failed += 1

    db.commit()
    return processed, failed


def get_user_attendance(
    db: Session,
    user_id: uuid.UUID,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> List[dict]:
    """
    Fetch attendance records for a user (Api.md § 4.1).
    Returns list of dicts with date, status, method.
    """
    query = db.query(AttendanceRecord).filter(AttendanceRecord.user_id == user_id)

    if from_date:
        query = query.filter(AttendanceRecord.attendance_date >= from_date)
    if to_date:
        query = query.filter(AttendanceRecord.attendance_date <= to_date)

    query = query.order_by(AttendanceRecord.attendance_date.desc())
    records = query.all()

    return [
        {
            "date": str(r.attendance_date),
            "status": "present",
            "method": (r.source or "face").lower(),
        }
        for r in records
    ]
