from datetime import datetime

from pydantic import BaseModel

from models.notifications import NotificationType


class NotificationOut(BaseModel):
    id: int
    type: NotificationType
    title: str
    message: str
    related_id: int | None = None
    related_type: str | None = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
