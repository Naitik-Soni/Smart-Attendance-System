from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import bearer
from app.core.exceptions import AppException
from app.core.responses import success_response
from app.schemas.auth import BootstrapAdminRequest, LoginRequest, LogoutRequest, RefreshTokenRequest
from app.services import auth_service


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    data = auth_service.login(db, user_id=payload.user_id, password=payload.password)
    return success_response(
        code="LOGIN_SUCCESS",
        message="Login successful",
        data=data,
    )


@router.post("/bootstrap-admin")
def bootstrap_admin(payload: BootstrapAdminRequest, db: Session = Depends(get_db)):
    data = auth_service.bootstrap_admin(
        db,
        org_name=payload.org_name,
        org_legal_name=payload.org_legal_name,
        org_code=payload.org_code,
        user_id=payload.user_id,
        password=payload.password,
        name=payload.name,
        email=payload.email,
    )
    return success_response(
        code="ADMIN_BOOTSTRAPPED",
        message="Bootstrap admin created successfully",
        data=data,
    )


@router.post("/refresh")
def refresh_tokens(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    data = auth_service.refresh_tokens(db, refresh_token=payload.refresh_token)
    return success_response(
        code="TOKEN_REFRESHED",
        message="Token refreshed successfully",
        data=data,
    )


@router.post("/logout")
def logout(
    payload: LogoutRequest,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
):
    if credentials is None:
        raise AppException(401, "UNAUTHORIZED", "Missing bearer token")

    auth_service.logout(db, access_token=credentials.credentials, refresh_token=payload.refresh_token)
    return success_response(
        code="LOGOUT_SUCCESS",
        message="Logged out successfully",
        data={"revoked": True},
    )
