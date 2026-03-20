from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    code: str
    message: str
    data: Optional[Any] = None
    meta: Dict[str, Any] = {}
    errors: List[Any] = []


def success_response(
    code: str,
    message: str,
    data: Any = None,
    meta: Dict[str, Any] = None,
) -> dict:
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
    errors: List[Any] = None,
) -> dict:
    return APIResponse(
        success=False,
        code=code,
        message=message,
        data=None,
        meta={},
        errors=errors or [],
    ).model_dump()
