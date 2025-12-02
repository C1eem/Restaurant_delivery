from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.crud import dish as crud
from app.schemas.dish import DishCreate, DishResponse, DishUpdate
from app.dependencies import get_db

router = APIRouter(prefix="/dishes", tags=["dishes"])

@router.post("/", response_model=DishResponse, status_code=status.HTTP_201_CREATED)
def create_dish(dish: DishCreate, db: Session = Depends(get_db)):
    # Проверяем уникальность названия
    if crud.get_dish_by_name(db, dish.name):
        raise HTTPException(status_code=400, detail="Блюдо с таким названием уже существует")
    return crud.create_dish(db, dish)

@router.get("/", response_model=List[DishResponse])
def read_dishes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    dishes = crud.get_all_dishes(db, skip=skip, limit=limit)
    return dishes

@router.get("/{dish_id}", response_model=DishResponse)
def read_dish(dish_id: int, db: Session = Depends(get_db)):
    dish = crud.get_dish_by_id(db, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")
    return dish

@router.get("/name/{name}", response_model=DishResponse)
def read_dish_by_name(name: str, db: Session = Depends(get_db)):
    dish = crud.get_dish_by_name(db, name)
    if not dish:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")
    return dish

@router.put("/{dish_id}", response_model=DishResponse)
def update_dish(
    dish_id: int,
    dish_update: DishUpdate,
    db: Session = Depends(get_db)
):
    dish = crud.update_dish(db, dish_id, dish_update)
    if not dish:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")
    return dish

@router.delete("/{dish_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dish(dish_id: int, db: Session = Depends(get_db)):
    success = crud.delete_dish(db, dish_id)
    if not success:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")