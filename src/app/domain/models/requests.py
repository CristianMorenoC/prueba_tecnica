from pydantic import BaseModel


class SubscribeRequest(BaseModel):
    amount: int
