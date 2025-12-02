from typing import Optional

from sqlalchemy.orm import Session
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate, IngredientUpdate


def get_ingredient_by_id(db: Session, ingredient_id: int) -> Optional[Ingredient]:
    return db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()


def get_ingredient_by_name(db: Session, name: str) -> Optional[Ingredient]:
    return db.query(Ingredient).filter(Ingredient.name == name).first()


def get_all_ingredients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Ingredient).offset(skip).limit(limit).all()


def create_ingredient(db: Session, ingredient: IngredientCreate) -> Ingredient:
    db_ingredient = Ingredient(name=ingredient.name)
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient


def update_ingredient(db: Session, ingredient_id: int, ingredient_update: IngredientUpdate) -> Optional[Ingredient]:
    db_ingredient = get_ingredient_by_id(db, ingredient_id)
    if not db_ingredient:
        return None

    update_data = ingredient_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_ingredient, key, value)

    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient


def delete_ingredient(db: Session, ingredient_id: int) -> bool:
    db_ingredient = get_ingredient_by_id(db, ingredient_id)
    if not db_ingredient:
        return False

    db.delete(db_ingredient)
    db.commit()
    return True