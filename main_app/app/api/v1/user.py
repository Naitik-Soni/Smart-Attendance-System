from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.responses import success_response
from app.services import attendance_service


router = APIRouter(prefix="/user", tags=["User"])


@router.get("/get-attendance")
def get_attendance(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    records = attendance_service.get_user_attendance(
        db,
        organization_id=current_user["organization_id"],
        user_id=current_user["user_id"],
    )
    return success_response(
        code="ATTENDANCE_FETCHED",
        message="Attendance records retrieved",
        data=[row.model_dump() for row in records],
        meta={"user_id": current_user["user_id"]},
    )
