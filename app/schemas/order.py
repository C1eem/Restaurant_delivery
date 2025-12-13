from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import enum


class OrderStatus(str, enum.Enum):
    # Значения синхронизированы с БД (enum orderstatus)
    pending = "pending"
    cooking = "cooking"
    ready = "ready"
    delivering = "delivering"
    completed = "completed"
    cancelled = "cancelled"


class OrderCreate(BaseModel):
    delivery_address: str
    user_id: int
    courier_id: Optional[int] = None
    total_amount: float
    status: OrderStatus = OrderStatus.pending


class OrderUpdate(BaseModel):
    delivery_address: Optional[str] = None
    courier_id: Optional[int] = None
    total_amount: Optional[float] = None
    status: Optional[OrderStatus] = None


class OrderResponse(BaseModel):
    id: int
    delivery_address: str
    user_id: int
    courier_id: Optional[int] = None
    created_at: datetime
    total_amount: float
    status: OrderStatus

    class Config:
        from_attributes = True