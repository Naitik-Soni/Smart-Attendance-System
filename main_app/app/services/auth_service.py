from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import Organization, RevokedToken, Role, User, UserProfile
from app.schemas.auth import LoginResponseData, TokenPair, UserInfo


def seed_roles(db: Session) -> None:
    role_count = db.query(func.count(Role.id)).scalar() or 0
    if role_count > 0:
        return

    db.add_all(
        [
            Role(id=1, role_name="ADMIN", description="System administrator"),
            Role(id=2, role_name="OPERATOR", description="Operations user"),
            Role(id=3, role_name="USER", description="Standard end user"),
        ]
    )
    db.commit()


def _next_faiss_user_id(db: Session) -> int:
    current = db.query(func.max(UserProfile.faiss_user_id)).scalar()
    return (current or 0) + 1


def _role_name(user: User) -> str:
    if user.role and user.role.role_name:
        return user.role.role_name.lower()
    return "user"


def _is_revoked(db: Session, jti: str) -> bool:
    return db.query(RevokedToken).filter(RevokedToken.jti == jti).first() is not None


def _revoke_token(db: Session, payload: dict) -> None:
    jti = payload["jti"]
    if _is_revoked(db, jti):
        return

    exp_ts = payload.get("exp")
    if exp_ts is None:
        raise AppException(401, "UNAUTHORIZED", "Token missing expiration")

    expires_at = datetime.fromtimestamp(exp_ts, tz=timezone.utc).replace(tzinfo=None)
    db.add(
        RevokedToken(
            jti=jti,
            token_type=payload["type"],
            user_id=payload["sub"],
            expires_at=expires_at,
        )
    )


def _issue_tokens(user: User, role: str, display_name: str) -> dict:
    data = LoginResponseData(
        user=UserInfo(user_id=user.username, role=role, name=display_name),
        tokens=TokenPair(
            access_token=create_access_token(user.username, role, user.organization_id),
            refresh_token=create_refresh_token(user.username, role, user.organization_id),
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
    )
    return data.model_dump()


def bootstrap_admin(
    db: Session,
    *,
    org_name: str,
    org_legal_name: str,
    org_code: str,
    user_id: str,
    password: str,
    name: str,
    email: str | None,
) -> dict:
    seed_roles(db)

    existing_admin = (
        db.query(User)
        .filter(User.role_id == 1, User.is_deleted.is_(False))
        .first()
    )
    if existing_admin:
        raise AppException(409, "ADMIN_ALREADY_EXISTS", "Bootstrap admin already configured")

    existing_org_code = db.query(Organization).filter(Organization.code == org_code).first()
    if existing_org_code:
        raise AppException(409, "ORG_CODE_EXISTS", "Organization code already exists")

    existing_username = db.query(User).filter(User.username == user_id).first()
    if existing_username:
        raise AppException(409, "USER_EXISTS", "User ID already exists")

    org = Organization(name=org_name, legal_name=org_legal_name, code=org_code, is_active=True)
    db.add(org)
    db.flush()

    user = User(
        organization_id=org.id,
        username=user_id,
        email=email,
        password_hash=hash_password(password),
        role_id=1,
        is_active=True,
        is_deleted=False,
    )
    db.add(user)
    db.flush()

    profile = UserProfile(
        user_id=user.id,
        full_name=name,
        employee_code=user_id,
        faiss_user_id=_next_faiss_user_id(db),
    )
    db.add(profile)
    db.commit()
    db.refresh(user)

    role = _role_name(user)
    return _issue_tokens(user, role, name)


def login(db: Session, *, user_id: str, password: str) -> dict:
    user = (
        db.query(User)
        .filter(User.username == user_id, User.is_deleted.is_(False), User.is_active.is_(True))
        .first()
    )
    if user is None or not verify_password(password, user.password_hash):
        raise AppException(401, "INVALID_CREDENTIALS", "Invalid user ID or password")

    role = _role_name(user)
    display_name = user.profile.full_name if user.profile and user.profile.full_name else user.username
    return _issue_tokens(user, role, display_name)


def refresh_tokens(db: Session, *, refresh_token: str) -> dict:
    payload = decode_refresh_token(refresh_token)
    if _is_revoked(db, payload["jti"]):
        raise AppException(401, "UNAUTHORIZED", "Refresh token has been revoked")

    user = (
        db.query(User)
        .filter(User.username == payload["sub"], User.is_deleted.is_(False), User.is_active.is_(True))
        .first()
    )
    if user is None:
        raise AppException(401, "UNAUTHORIZED", "User not found or inactive")

    _revoke_token(db, payload)
    role = _role_name(user)
    display_name = user.profile.full_name if user.profile and user.profile.full_name else user.username
    data = _issue_tokens(user, role, display_name)
    db.commit()
    return data


def logout(db: Session, *, access_token: str, refresh_token: str | None = None) -> None:
    access_payload = decode_access_token(access_token)
    _revoke_token(db, access_payload)

    if refresh_token:
        refresh_payload = decode_refresh_token(refresh_token)
        if refresh_payload.get("sub") != access_payload.get("sub"):
            raise AppException(400, "TOKEN_SUBJECT_MISMATCH", "Refresh token does not belong to current user")
        _revoke_token(db, refresh_payload)

    db.commit()


def revoke_token(db: Session, token: str) -> None:
    payload = decode_token(token)
    _revoke_token(db, payload)
    db.commit()
