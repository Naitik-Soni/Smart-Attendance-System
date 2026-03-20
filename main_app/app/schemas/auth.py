from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    user_id: str = Field(min_length=1)
    password: str = Field(min_length=1)


class BootstrapAdminRequest(BaseModel):
    org_name: str = Field(min_length=1)
    org_legal_name: str = Field(min_length=1)
    org_code: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    password: str = Field(min_length=8)
    name: str = Field(min_length=1)
    email: str | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


class UserInfo(BaseModel):
    user_id: str
    role: str
    name: str


class LoginResponseData(BaseModel):
    user: UserInfo
    tokens: TokenPair


class LoginResponse(BaseModel):
    success: bool
    code: str
    message: str
    data: LoginResponseData
    meta: dict = {}
    errors: list = []
