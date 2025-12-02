from sqlalchemy import Column, Integer, ForeignKey
from app.models.base import Base

class DishIngredient(Base):
    __tablename__ = "dish_ingredients"

    id = Column(Integer, primary_key=True)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)

    def __repr__(self):
        return (f"<DishIngredient(id={self.id}, dish_id={self.dish_id})"
                f"ingredient_id={self.ingredient_id}>")
