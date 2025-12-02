from pydantic import BaseModel
from typing import Optional


class IngredientCreate(BaseModel):
    name: str


class IngredientUpdate(BaseModel):
    name: Optional[str] = None


class IngredientResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True