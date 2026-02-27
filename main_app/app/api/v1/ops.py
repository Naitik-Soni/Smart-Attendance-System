from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_operator
from app.core.exceptions import AppException
from app.core.responses import success_response
from app.schemas.ops import ManualAttendanceItem
from app.schemas.user import UserCreate, UserUpdate
from app.services import attendance_service, audit_service, face_client, face_metadata_service, user_service


router = APIRouter(prefix="/ops", tags=["Operations"])


@router.post("/user")
def add_user(
    payload: UserCreate,
    current_user: dict = Depends(require_operator),
    db: Session = Depends(get_db),
):
    created = user_service.create_user(db, current_user["organization_id"], payload)
    audit_service.write_audit_log(
        db,
        organization_id=current_user["organization_id"],
        user_id=current_user["user_id"],
        action="USER_CREATED",
        entity_type="user",
        entity_id=created.user_id,
    )
    return success_response(
        code="USER_CREATED",
        message="User added successfully",
        data={"user_id": created.user_id},
    )


@router.get("/users")
def list_users(current_user: dict = Depends(require_operator), db: Session = Depends(get_db)):
    users = user_service.list_users(db, current_user["organization_id"])
    return success_response(
        code="USERS_LIST",
        message="Users fetched successfully",
        data=[user.model_dump() for user in users],
        meta={"total": len(users), "page": 1, "page_size": 20},
    )


@router.patch("/user/{user_id}")
def update_user(
    user_id: str,
    payload: UserUpdate,
    current_user: dict = Depends(require_operator),
    db: Session = Depends(get_db),
):
    updated = user_service.update_user(db, current_user["organization_id"], user_id, payload)
    audit_service.write_audit_log(
        db,
        organization_id=current_user["organization_id"],
        user_id=current_user["user_id"],
        action="USER_UPDATED",
        entity_type="user",
        entity_id=updated.user_id,
    )
    return success_response(
        code="USER_UPDATED",
        message="User details updated",
        data={"user_id": updated.user_id, "updates": payload.model_dump(exclude_none=True)},
    )


@router.delete("/user/{user_id}")
def delete_user(
    user_id: str,
    current_user: dict = Depends(require_operator),
    db: Session = Depends(get_db),
):
    user_service.delete_user(db, current_user["organization_id"], user_id)
    audit_service.write_audit_log(
        db,
        organization_id=current_user["organization_id"],
        user_id=current_user["user_id"],
        action="USER_DELETED",
        entity_type="user",
        entity_id=user_id,
    )
    return success_response(
        code="USER_DELETED",
        message="User deleted successfully",
        data={"user_id": user_id},
    )


@router.get("/get-user/{user_id}")
def get_user(user_id: str, current_user: dict = Depends(require_operator), db: Session = Depends(get_db)):
    user = user_service.get_user(db, current_user["organization_id"], user_id)
    return success_response(
        code="USER_FETCHED",
        message="User details retrieved",
        data=user.model_dump(),
    )


@router.post("/upload-image")
async def upload_image(
    source_type: str = Form("upload_image"),
    source_id: str = Form("MANUAL_UPLOAD_1"),
    timestamp: datetime | None = Form(None),
    user_id: str | None = Form(None),
    image: UploadFile | None = File(None),
    images: list[UploadFile] | None = File(None),
    current_user: dict = Depends(require_operator),
    db: Session = Depends(get_db),
):
    ts = timestamp or datetime.now(timezone.utc)

    if user_id:
        register_images = images or ([image] if image is not None else [])
        if not register_images:
            raise AppException(400, "IMAGE_REQUIRED", "At least one image is required for registration")

        result = await face_client.register_faces(user_id=user_id, files=register_images)
        if "error" in result:
            status_code = result["error"].get("status_code", 502)
            raise AppException(status_code, "FACE_REGISTER_FAILED", "Face registration failed")

        persist = face_metadata_service.persist_registration_metadata(
            db,
            organization_id=current_user["organization_id"],
            user_id=user_id,
            payload=result.get("data", {}),
        )

        return success_response(
            code="FACE_REGISTERED",
            message="Face registration completed",
            data=result,
            meta={"user_id": user_id, "images_sent": len(register_images), **persist},
        )

    recognize_image = image or (images[0] if images else None)
    if recognize_image is None:
        raise AppException(400, "IMAGE_REQUIRED", "Image file is required for recognition")

    result = await face_client.recognize_faces(
        source_type=source_type,
        source_id=source_id,
        timestamp=ts,
        image=recognize_image,
    )
    if "error" in result:
        status_code = result["error"].get("status_code", 502)
        raise AppException(status_code, "FACE_RECOGNIZE_FAILED", "Face recognition failed")

    persist = face_metadata_service.persist_recognition_metadata(
        db,
        organization_id=current_user["organization_id"],
        captured_at=ts,
        payload=result,
    )

    return success_response(
        code="FACE_RECOGNIZED",
        message="Image processed successfully",
        data=result,
        meta={"source_type": source_type, "source_id": source_id, "timestamp": ts.isoformat(), **persist},
    )


@router.post("/manual_attendance")
def manual_attendance(
    items: list[ManualAttendanceItem],
    current_user: dict = Depends(require_operator),
    db: Session = Depends(get_db),
):
    summary = attendance_service.mark_manual_attendance(db, current_user["organization_id"], items)
    audit_service.write_audit_log(
        db,
        organization_id=current_user["organization_id"],
        user_id=current_user["user_id"],
        action="ATTENDANCE_MARKED",
        entity_type="attendance",
    )
    return success_response(
        code="ATTENDANCE_MARKED",
        message="Attendance marked successfully",
        data=summary,
        meta={"request_type": "bulk"},
    )


@router.get("/get-logs")
def get_logs(current_user: dict = Depends(require_operator), db: Session = Depends(get_db)):
    logs = audit_service.list_audit_logs(db, current_user["organization_id"])
    return success_response(
        code="LOGS_FETCHED",
        message="Audit logs retrieved",
        data=logs,
        meta={"total": len(logs)},
    )
