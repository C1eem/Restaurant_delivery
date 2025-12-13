from typing import Optional

from sqlalchemy.orm import Session
from app.models.dish_ingredient import DishIngredient
from app.schemas.dish_ingredient import DishIngredientCreate, DishIngredientUpdate

def get_all_dish_ingredients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(DishIngredient).offset(skip).limit(limit).all()


def get_dish_ingredient_by_id(db: Session, dish_ingredient_id: int) -> Optional[DishIngredient]:
    return db.query(DishIngredient).filter(DishIngredient.id == dish_ingredient_id).first()


def get_ingredients_for_dish(db: Session, dish_id: int):
    return db.query(DishIngredient).filter(DishIngredient.dish_id == dish_id).all()


def get_dishes_for_ingredient(db: Session, ingredient_id: int):
    return db.query(DishIngredient).filter(DishIngredient.ingredient_id == ingredient_id).all()


def create_dish_ingredient(db: Session, dish_ingredient: DishIngredientCreate) -> DishIngredient:
    db_dish_ingredient = DishIngredient(
        dish_id=dish_ingredient.dish_id,
        ingredient_id=dish_ingredient.ingredient_id
    )
    db.add(db_dish_ingredient)
    db.commit()
    db.refresh(db_dish_ingredient)
    return db_dish_ingredient


def update_dish_ingredient(db: Session, dish_ingredient_id: int,
                           dish_ingredient_update: DishIngredientUpdate) -> Optional[DishIngredient]:
    db_dish_ingredient = get_dish_ingredient_by_id(db, dish_ingredient_id)
    if not db_dish_ingredient:
        return None

    update_data = dish_ingredient_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_dish_ingredient, key, value)

    db.commit()
    db.refresh(db_dish_ingredient)
    return db_dish_ingredient


def delete_dish_ingredient(db: Session, dish_ingredient_id: int) -> bool:
    db_dish_ingredient = get_dish_ingredient_by_id(db, dish_ingredient_id)
    if not db_dish_ingredient:
        return False

    db.delete(db_dish_ingredient)
    db.commit()
    return True