from pydantic import BaseModel, Field
from typing import Literal


class NotifyUserAction(BaseModel):
    type: Literal["notify_user"] = "notify_user"
    user_id: int = Field(..., description="The user ID to notify")
    message: str = Field(..., description="The notification message")


class LogEventAction(BaseModel):
    type: Literal["log_event"] = "log_event"
    event: str = Field(..., description="The event description")


ActionSchema = NotifyUserAction | LogEventAction


class LLMResponse(BaseModel):
    response: str = Field(..., description="The response text to send to the user")
    actions: list[ActionSchema] = Field(
        default_factory=list, description="List of actions to execute"
    )
