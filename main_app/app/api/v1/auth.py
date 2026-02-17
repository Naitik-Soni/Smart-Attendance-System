"""
Auth routes — Api.md § 1 (Authorization APIs).
POST /api/v1/auth/login
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import LoginRequest
from app.schemas.common import success_response, error_response
from app.services.auth_service import authenticate_user, build_login_response

router = APIRouter()


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """
    Authorize users based on credentials.
    Authority: Anyone
    """
    user = authenticate_user(db, body.user_id, body.password)
    if user is None:
        return error_response(
            code="INVALID_CREDENTIALS",
            message="Invalid user ID or password",
        )

    data = build_login_response(user)
    return success_response(
        code="LOGIN_SUCCESS",
        message="Login successful",
        data=data,
    )
