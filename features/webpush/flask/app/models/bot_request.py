
from pydantic import BaseModel, Field, field_validator


class BotNotificationRequest(BaseModel):
    """Model for bot notification request."""

    bot_id: str
    title: str
    content: str
    timestamp_ms: int = Field(..., alias="timestamp")

    @field_validator("timestamp_ms", mode="before")
    @classmethod
    def convert_timestamp(cls, v):
        """Convert timestamp to milliseconds if needed."""
        if isinstance(v, (int, float)):
            return int(v)
        raise ValueError("timestamp must be an integer or float")

    model_config = {"populate_by_name": True}


class BotAuthResponse(BaseModel):
    """Response for bot authentication."""

    success: bool
    message: str


class NotificationResponse(BaseModel):
    """Response for notification send."""

    success: bool
    message: str
    notification_id: str | None = None
