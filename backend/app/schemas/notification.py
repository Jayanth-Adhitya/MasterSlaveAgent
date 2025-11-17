from pydantic import BaseModel
from datetime import datetime


class NotificationResponse(BaseModel):
    id: int
    tenant_id: int
    from_user_id: int
    from_user_name: str | None = None
    to_user_id: int
    message: str
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True
