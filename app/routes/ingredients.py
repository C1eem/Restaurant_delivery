from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.crud import ingredient as crud
from app.schemas.ingredient import IngredientCreate, IngredientResponse, IngredientUpdate
from app.dependencies import get_db

router = APIRouter(prefix="/ingredients", tags=["ingredients"])

@router.post("/", response_model=IngredientResponse, status_code=status.HTTP_201_CREATED)
def create_ingredient(ingredient: IngredientCreate, db: Session = Depends(get_db)):
    return crud.create_ingredient(db, ingredient)

@router.get("/", response_model=List[IngredientResponse])
def read_ingredients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    ingredients = crud.get_all_ingredients(db, skip=skip, limit=limit)
    return ingredients

@router.get("/{ingredient_id}", response_model=IngredientResponse)
def read_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    ingredient = crud.get_ingredient_by_id(db, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ингредиент не найден")
    return ingredient

@router.get("/name/{name}", response_model=IngredientResponse)
def read_ingredient_by_name(name: str, db: Session = Depends(get_db)):
    ingredient = crud.get_ingredient_by_name(db, name)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ингредиент не найден")
    return ingredient

@router.put("/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient(
    ingredient_id: int,
    ingredient_update: IngredientUpdate,
    db: Session = Depends(get_db)
):
    ingredient = crud.update_ingredient(db, ingredient_id, ingredient_update)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ингредиент не найден")
    return ingredient

@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    success = crud.delete_ingredient(db, ingredient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ингредиент не найден")