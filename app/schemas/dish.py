from pydantic import BaseModel
from typing import Optional


class DishCreate(BaseModel):
    name: str
    weight: float
    price: float
    calories: float
    description: Optional[str] = None


class DishUpdate(BaseModel):
    name: Optional[str] = None
    weight: Optional[float] = None
    price: Optional[float] = None
    calories: Optional[float] = None
    description: Optional[str] = None


class DishResponse(BaseModel):
    id: int
    name: str
    weight: float
    price: float
    calories: float
    description: Optional[str] = None

    class Config:
        from_attributes = True