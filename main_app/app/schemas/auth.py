"""
Auth schemas — matches Api.md § 1 (Authorization APIs).
"""

from pydantic import BaseModel
from typing import Optional


# ── Requests ──────────────────────────────────────────

class LoginRequest(BaseModel):
    user_id: str          # username
    password: str


# ── Response sub-models ───────────────────────────────

class LoginUserInfo(BaseModel):
    user_id: str
    role: str
    name: Optional[str] = None

    class Config:
        from_attributes = True


class TokenPair(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: int       # seconds
