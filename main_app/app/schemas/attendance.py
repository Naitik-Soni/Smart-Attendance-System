"""
Attendance schemas — matches Api.md § 3.7 (Manual Attendance) and § 4.1 (View Attendance).
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ── Requests ──────────────────────────────────────────

class ManualAttendanceItem(BaseModel):
    """Single entry in the bulk manual attendance request (§ 3.7)."""
    user_id: str
    attendance_type: str = "manual"
    status: str                        # "present" | "absent"
    timestamp: datetime
    reason: Optional[str] = None


class ManualAttendanceRequest(BaseModel):
    entries: List[ManualAttendanceItem]


# ── Responses ─────────────────────────────────────────

class AttendanceOut(BaseModel):
    """Single attendance record returned to the user (§ 4.1)."""
    date: str
    status: str
    method: Optional[str] = None       # "face" | "manual"

    class Config:
        from_attributes = True


class ManualAttendanceResult(BaseModel):
    processed: int
    failed: int
