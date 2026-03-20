from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AppException
from app.core.security import decode_access_token
from app.models import RevokedToken, User


bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> dict:
    if credentials is None:
        raise AppException(401, "UNAUTHORIZED", "Missing bearer token")

    payload = decode_access_token(credentials.credentials)
    username = payload["sub"]
    token_jti = payload["jti"]

    revoked = db.query(RevokedToken).filter(RevokedToken.jti == token_jti).first()
    if revoked is not None:
        raise AppException(401, "UNAUTHORIZED", "Token has been revoked")

    user = (
        db.query(User)
        .filter(User.username == username, User.is_deleted.is_(False), User.is_active.is_(True))
        .first()
    )
    if user is None:
        raise AppException(401, "UNAUTHORIZED", "User not found or inactive")

    role = user.role.role_name.lower() if user.role else "user"
    name = user.profile.full_name if user.profile and user.profile.full_name else user.username
    return {
        "user_id": user.username,
        "role": role,
        "name": name,
        "organization_id": user.organization_id,
        "token_jti": token_jti,
    }


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] != "admin":
        raise AppException(403, "FORBIDDEN", "Admin access required")
    return current_user


def require_operator(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] not in {"admin", "operator"}:
        raise AppException(403, "FORBIDDEN", "Operator access required")
    return current_user
