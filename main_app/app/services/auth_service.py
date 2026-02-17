"""
Auth service — handles login and token creation.
Controllers call this; this talks to DB.
"""

from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token
from app.core.config import get_settings
from app.models.user import User, UserProfile

settings = get_settings()


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """
    Look up a user by username, verify their password.
    Returns the User ORM object or None.
    """
    user = (
        db.query(User)
        .filter(User.username == username, User.is_active.is_(True), User.is_deleted.is_(False))
        .first()
    )
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def build_login_response(user: User) -> dict:
    """
    Given an authenticated user, build the full login response payload
    matching Api.md § 1.1.
    """
    profile: UserProfile | None = user.profile
    display_name = profile.full_name if profile else user.username

    # Create JWT with subject = user id
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "user": {
            "user_id": user.username,
            "role": user.role.role_name.lower(),
            "name": display_name,
        },
        "tokens": {
            "access_token": access_token,
            "refresh_token": None,  # TODO: implement refresh tokens
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        },
    }
