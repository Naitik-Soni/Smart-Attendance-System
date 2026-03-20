from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ManualAttendanceItem(BaseModel):
    user_id: str
    attendance_type: str = "manual"
    status: str = "present"
    timestamp: datetime
    reason: Optional[str] = None

class AttendanceOut(BaseModel):
    date: str
    status: str
    method: str

class AuditLogOut(BaseModel):
    action: str
    actor: str
    timestamp: datetime

class ImageUploadResponse(BaseModel):
    request_id: str
    status: str
