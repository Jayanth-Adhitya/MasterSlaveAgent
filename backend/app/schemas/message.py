from pydantic import BaseModel
from datetime import datetime


class MessageCreate(BaseModel):
    content: str
    session_id: str


class MessageResponse(BaseModel):
    id: int
    tenant_id: int
    user_id: int
    session_id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
