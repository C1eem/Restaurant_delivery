from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.models.base import Base

class DishInMenu(Base):
    __tablename__ = "dishes_in_menu"

    id = Column(Integer, primary_key=True)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)
    price = Column(Float, nullable=False)

    def __repr__(self):
        return (f"<Dish(id={self.id}, dish_id='{self.dish_id}', "
                f"price={self.price})>")
