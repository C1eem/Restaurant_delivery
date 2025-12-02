from pydantic import BaseModel
from typing import Optional


class OrderItemCreate(BaseModel):
    order_id: int
    dish_id: int
    quantity: int = 1


class OrderItemUpdate(BaseModel):
    dish_id: Optional[int] = None
    quantity: Optional[int] = None


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    dish_id: int
    quantity: int

    class Config:
        from_attributes = True