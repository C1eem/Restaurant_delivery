from pydantic import BaseModel
from typing import Optional


class DishInMenuCreate(BaseModel):
    dish_id: int
    price: float


class DishInMenuUpdate(BaseModel):
    dish_id: Optional[int] = None
    price: Optional[float] = None


class DishInMenuResponse(BaseModel):
    id: int
    dish_id: int
    price: float

    class Config:
        from_attributes = True