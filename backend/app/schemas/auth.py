from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int
    tenant_id: int
    email: str
    name: str
    role: str
    tenant_name: str
    tenant_type: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
