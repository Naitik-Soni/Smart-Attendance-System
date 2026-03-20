from pydantic import BaseModel, Field
from typing import Any


class OrgConfigBody(BaseModel):
    org: dict
    security: dict
    face_registration: dict
    data_policy: dict
    limits: dict


class SystemConfigBody(BaseModel):
    cameras: dict
    image_upload: dict


class PolicyConfigBody(BaseModel):
    policies: dict[str, Any]


class CameraConfigBody(BaseModel):
    camera_id: str
    camera_type: str = Field(pattern="^(wall_camera|ceiling_camera)$")
    source: str
    location: str | None = None
    gate_id: str | None = None
    direction: str = Field(default="both", pattern="^(entry|exit|both)$")
    enabled: bool = True


class CameraUpdateBody(BaseModel):
    camera_type: str | None = Field(default=None, pattern="^(wall_camera|ceiling_camera)$")
    source: str | None = None
    location: str | None = None
    gate_id: str | None = None
    direction: str | None = Field(default=None, pattern="^(entry|exit|both)$")
    enabled: bool | None = None


class OperatorCreate(BaseModel):
    operator_id: str
    name: str
    email: str | None = None
    password: str = Field(min_length=8)
    role: str = "operator"
    status: str = "active"


class OperatorUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    status: str | None = None


class OperatorOut(BaseModel):
    operator_id: str
    name: str
    email: str | None = None
    role: str
    status: str
