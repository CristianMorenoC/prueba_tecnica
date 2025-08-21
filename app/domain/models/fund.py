from pydantic import BaseModel


class Fund(BaseModel):
    fund_id: str
    name: str
    min_amount: float
    category: str
