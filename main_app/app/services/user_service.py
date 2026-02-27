from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import AppException
from app.core.security import hash_password
from app.models import User, UserProfile
from app.schemas.user import UserCreate, UserOut, UserUpdate


ROLE_TO_ID = {"admin": 1, "operator": 2, "user": 3}


def _next_faiss_user_id(db: Session) -> int:
    current = db.query(func.max(UserProfile.faiss_user_id)).scalar()
    return (current or 0) + 1


def _user_to_schema(user: User) -> UserOut:
    role = user.role.role_name.lower() if user.role else "user"
    status = "active" if user.is_active else "inactive"
    name = user.profile.full_name if user.profile and user.profile.full_name else user.username
    return UserOut(
        user_id=user.username,
        name=name,
        email=user.email,
        role=role,
        status=status,
    )


def create_user(db: Session, organization_id: str, payload: UserCreate) -> UserOut:
    if db.query(User).filter(User.username == payload.user_id).first():
        raise AppException(409, "USER_EXISTS", "User ID already exists")

    role_id = ROLE_TO_ID.get(payload.role.lower())
    if role_id is None:
        raise AppException(400, "INVALID_ROLE", "Unsupported role")

    password = payload.password
    user = User(
        organization_id=organization_id,
        username=payload.user_id,
        email=payload.email,
        password_hash=hash_password(password),
        role_id=role_id,
        is_active=payload.status.lower() == "active",
        is_deleted=False,
    )
    db.add(user)
    db.flush()

    profile = UserProfile(
        user_id=user.id,
        full_name=payload.name,
        employee_code=payload.user_id,
        faiss_user_id=_next_faiss_user_id(db),
    )
    db.add(profile)
    db.commit()
    db.refresh(user)
    return _user_to_schema(user)


def list_users(db: Session, organization_id: str) -> list[UserOut]:
    users = (
        db.query(User)
        .options(joinedload(User.role), joinedload(User.profile))
        .filter(User.organization_id == organization_id, User.is_deleted.is_(False))
        .order_by(User.created_at.desc())
        .all()
    )
    return [_user_to_schema(user) for user in users]


def get_user(db: Session, organization_id: str, user_id: str) -> UserOut:
    user = (
        db.query(User)
        .options(joinedload(User.role), joinedload(User.profile))
        .filter(
            User.organization_id == organization_id,
            User.username == user_id,
            User.is_deleted.is_(False),
        )
        .first()
    )
    if user is None:
        raise AppException(404, "USER_NOT_FOUND", "User not found")
    return _user_to_schema(user)


def update_user(db: Session, organization_id: str, user_id: str, payload: UserUpdate) -> UserOut:
    user = (
        db.query(User)
        .options(joinedload(User.role), joinedload(User.profile))
        .filter(
            User.organization_id == organization_id,
            User.username == user_id,
            User.is_deleted.is_(False),
        )
        .first()
    )
    if user is None:
        raise AppException(404, "USER_NOT_FOUND", "User not found")

    if payload.email is not None:
        user.email = payload.email

    if payload.status is not None:
        user.is_active = payload.status.lower() == "active"

    if payload.role is not None:
        role_id = ROLE_TO_ID.get(payload.role.lower())
        if role_id is None:
            raise AppException(400, "INVALID_ROLE", "Unsupported role")
        user.role_id = role_id

    if payload.name is not None:
        if user.profile is None:
            user.profile = UserProfile(
                user_id=user.id,
                employee_code=user.username,
                faiss_user_id=_next_faiss_user_id(db),
            )
        user.profile.full_name = payload.name

    db.commit()
    db.refresh(user)
    return _user_to_schema(user)


def delete_user(db: Session, organization_id: str, user_id: str) -> None:
    user = (
        db.query(User)
        .filter(
            User.organization_id == organization_id,
            User.username == user_id,
            User.is_deleted.is_(False),
        )
        .first()
    )
    if user is None:
        raise AppException(404, "USER_NOT_FOUND", "User not found")

    user.is_deleted = True
    user.is_active = False
    db.commit()

