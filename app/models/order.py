from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from app.models.base import Base
from datetime import datetime
import enum


class OrderStatus(enum.Enum):
    """
    Статусы заказов.
    Значения должны совпадать с перечислением orderstatus в PostgreSQL
    (см. Alembic-миссию 4204b4360ab5_1.py).
    """
    pending = "pending"
    cooking = "cooking"
    ready = "ready"
    delivering = "delivering"
    completed = "completed"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    delivery_address = Column(String, nullable=False)
    courier_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Курьер, назначенный на заказ
    created_at = Column(DateTime, default=datetime.utcnow())
    worker_id = Column(Integer, ForeignKey('workers.id'), nullable=True)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.pending)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Клиент, сделавший заказ

    def __repr__(self):
        return (f"<Order(id={self.id}, user_id={self.user_id}, courier_id={self.courier_id},"
                f"created_at={self.created_at}, total_amount={self.total_amount}, status='{self.status}')>")