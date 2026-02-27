from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    user_id: str
    name: str
    email: str | None = None
    password: str = Field(min_length=8)
    role: str = "user"
    status: str = "active"


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    role: str | None = None
    status: str | None = None


class UserOut(BaseModel):
    user_id: str
    name: str
    email: str | None = None
    role: str
    status: str

    model_config = {"from_attributes": True}
