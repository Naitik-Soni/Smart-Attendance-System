"""
Standard API response wrapper — matches the contract from Api.md.

Every endpoint returns this shape:
{
    "success": true/false,
    "code": "LOGIN_SUCCESS",
    "message": "...",
    "data": { ... },
    "meta": { ... },
    "errors": [ ... ]
}
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class APIResponse(BaseModel):
    """Uniform envelope for all API responses."""

    success: bool
    code: str
    message: str
    data: Optional[Any] = None
    meta: Optional[Dict[str, Any]] = {}
    errors: Optional[List[Any]] = []


# ── Helper factories ──────────────────────────────────

def success_response(
    code: str,
    message: str,
    data: Any = None,
    meta: Optional[Dict[str, Any]] = None,
) -> dict:
    """Shortcut for building a successful response dict."""
    return APIResponse(
        success=True,
        code=code,
        message=message,
        data=data,
        meta=meta or {},
        errors=[],
    ).model_dump()


def error_response(
    code: str,
    message: str,
    errors: Optional[List[Any]] = None,
) -> dict:
    """Shortcut for building an error response dict."""
    return APIResponse(
        success=False,
        code=code,
        message=message,
        data=None,
        meta={},
        errors=errors or [],
    ).model_dump()
