from pydantic import BaseModel
from typing import Optional


class DishIngredientCreate(BaseModel):
    dish_id: int
    ingredient_id: int


class DishIngredientUpdate(BaseModel):
    dish_id: Optional[int] = None
    ingredient_id: Optional[int] = None


class DishIngredientResponse(BaseModel):
    id: int
    dish_id: int
    ingredient_id: int

    class Config:
        from_attributes = True