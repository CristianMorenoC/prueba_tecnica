from pydantic import BaseModel
from domain.models.subscription import NotificationChannel


class SubscribeRequest(BaseModel):
    amount: int
    notification_channel: NotificationChannel
