from sqlalchemy import Column, Integer, ForeignKey
from app.models.base import Base

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    def __repr__(self):
        return (f"<OrderItem(id={self.id}, "
                f"order_id={self.order_id}, dish_id={self.dish_id}, quantity={self.quantity})>")