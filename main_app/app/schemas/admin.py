from pydantic import BaseModel, Field


class OrgConfigBody(BaseModel):
    org: dict
    security: dict
    face_registration: dict
    data_policy: dict
    limits: dict


class SystemConfigBody(BaseModel):
    cameras: dict
    image_upload: dict


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
