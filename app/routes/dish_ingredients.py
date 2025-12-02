from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.crud import dish_ingredient as crud
from app.schemas.dish_ingredient import DishIngredientCreate, DishIngredientResponse, DishIngredientUpdate
from app.dependencies import get_db

router = APIRouter(prefix="/dish-ingredients", tags=["dish-ingredients"])

@router.post("/", response_model=DishIngredientResponse, status_code=status.HTTP_201_CREATED)
def create_dish_ingredient(dish_ingredient: DishIngredientCreate, db: Session = Depends(get_db)):
    return crud.create_dish_ingredient(db, dish_ingredient)

@router.get("/", response_model=List[DishIngredientResponse])
def read_dish_ingredients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    dish_ingredients = crud.get_all_dish_ingredients(db, skip=skip, limit=limit)
    return dish_ingredients

@router.get("/{dish_ingredient_id}", response_model=DishIngredientResponse)
def read_dish_ingredient(dish_ingredient_id: int, db: Session = Depends(get_db)):
    dish_ingredient = crud.get_dish_ingredient_by_id(db, dish_ingredient_id)
    if not dish_ingredient:
        raise HTTPException(status_code=404, detail="Связь блюдо-ингредиент не найдена")
    return dish_ingredient

@router.get("/dish/{dish_id}", response_model=List[DishIngredientResponse])
def read_ingredients_for_dish(dish_id: int, db: Session = Depends(get_db)):
    ingredients = crud.get_ingredients_for_dish(db, dish_id)
    return ingredients

@router.get("/ingredient/{ingredient_id}", response_model=List[DishIngredientResponse])
def read_dishes_for_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    dishes = crud.get_dishes_for_ingredient(db, ingredient_id)
    return dishes

@router.put("/{dish_ingredient_id}", response_model=DishIngredientResponse)
def update_dish_ingredient(
    dish_ingredient_id: int,
    dish_ingredient_update: DishIngredientUpdate,
    db: Session = Depends(get_db)
):
    dish_ingredient = crud.update_dish_ingredient(db, dish_ingredient_id, dish_ingredient_update)
    if not dish_ingredient:
        raise HTTPException(status_code=404, detail="Связь блюдо-ингредиент не найдена")
    return dish_ingredient

@router.delete("/{dish_ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dish_ingredient(dish_ingredient_id: int, db: Session = Depends(get_db)):
    success = crud.delete_dish_ingredient(db, dish_ingredient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Связь блюдо-ингредиент не найдена")