from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.models.base import Base

class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    weight = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    calories = Column(Float, nullable=False)
    description = Column(String)

    def __repr__(self):
        return (f"<Dish(id={self.id}, name='{self.name}', "
                f"price={self.price})>")
