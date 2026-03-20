from datetime import datetime, timedelta, timezone
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import AppException


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(
    subject: str,
    role: str,
    organization_id: str,
    expires_delta: timedelta,
    token_type: str,
) -> str:
    expire_at = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": subject,
        "role": role,
        "org_id": str(organization_id),
        "type": token_type,
        "jti": uuid.uuid4().hex,
        "exp": int(expire_at.timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str, role: str, organization_id: str) -> str:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(
        subject=subject,
        role=role,
        organization_id=organization_id,
        expires_delta=expires_delta,
        token_type="access",
    )


def create_refresh_token(subject: str, role: str, organization_id: str) -> str:
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token(
        subject=subject,
        role=role,
        organization_id=organization_id,
        expires_delta=expires_delta,
        token_type="refresh",
    )


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise AppException(401, "UNAUTHORIZED", "Invalid or expired token") from exc

    if not payload.get("sub") or not payload.get("jti") or not payload.get("type"):
        raise AppException(401, "UNAUTHORIZED", "Invalid token payload")

    return payload


def decode_access_token(token: str) -> dict:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise AppException(401, "UNAUTHORIZED", "Invalid token type")
    return payload


def decode_refresh_token(token: str) -> dict:
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise AppException(401, "UNAUTHORIZED", "Invalid token type")
    return payload

