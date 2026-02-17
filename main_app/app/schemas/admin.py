"""
Admin/config schemas — matches Api.md § 2.1 (Org Config) and § 2.2 (System Config).
"""

from pydantic import BaseModel
from typing import Any, Dict, Optional


# ── Organization Config (§ 2.1) ──────────────────────

class OrgConfigRequest(BaseModel):
    org: Optional[Dict[str, Any]] = None
    security: Optional[Dict[str, Any]] = None
    face_registration: Optional[Dict[str, Any]] = None
    data_policy: Optional[Dict[str, Any]] = None
    limits: Optional[Dict[str, Any]] = None


# ── System / Camera Config (§ 2.2) ───────────────────

class SystemConfigRequest(BaseModel):
    cameras: Optional[Dict[str, Any]] = None
    image_upload: Optional[Dict[str, Any]] = None
