from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str
    tenant_id: int


class UserResponse(BaseModel):
    id: int
    tenant_id: int
    email: EmailStr
    name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
