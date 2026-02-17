"""
Attendance routes — Api.md § 3.6-3.7 (Ops) and § 4.1 (User).

Endpoints:
  POST /upload-image        — Upload image for processing (§ 3.6)
  POST /manual              — Mark manual attendance (§ 3.7)
  GET  /my                  — View personal attendance (§ 4.1)
"""

from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, List

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.attendance import ManualAttendanceItem
from app.schemas.common import success_response, error_response
from app.services.attendance_service import mark_manual_attendance, get_user_attendance

router = APIRouter()


# ── Upload Image (§ 3.6) ─────────────────────────────

@router.post("/upload-image")
async def upload_image(
    image: UploadFile = File(...),
    current_user: User = Depends(require_role("ADMIN", "OPERATOR")),
):
    # TODO: save to storage, forward to face_service for recognition
    return success_response(
        code="IMAGE_RECEIVED",
        message="Image uploaded successfully, processing started",
        data={
            "request_id": "img_req_pending",
            "status": "processing",
        },
    )


# ── Manual Attendance (§ 3.7) ────────────────────────

@router.post("/manual")
def manual_attendance(
    entries: List[ManualAttendanceItem],
    current_user: User = Depends(require_role("ADMIN", "OPERATOR")),
    db: Session = Depends(get_db),
):
    processed, failed = mark_manual_attendance(
        db,
        organization_id=current_user.organization_id,
        entries=entries,
    )

    return success_response(
        code="ATTENDANCE_MARKED",
        message="Attendance marked successfully",
        data={"processed": processed, "failed": failed},
        meta={"request_type": "bulk"},
    )


# ── View Personal Attendance (§ 4.1) ─────────────────

@router.get("/my")
def my_attendance(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = get_user_attendance(
        db,
        user_id=current_user.id,
        from_date=from_date,
        to_date=to_date,
    )

    return success_response(
        code="ATTENDANCE_FETCHED",
        message="Attendance records retrieved",
        data=records,
    )
