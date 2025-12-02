from typing import Optional

from sqlalchemy.orm import Session
from app.models.dish import Dish
from app.schemas.dish import DishCreate, DishUpdate


def get_dish_by_id(db: Session, dish_id: int) -> Optional[Dish]:
    return db.query(Dish).filter(Dish.id == dish_id).first()


def get_dish_by_name(db: Session, name: str) -> Optional[Dish]:
    return db.query(Dish).filter(Dish.name == name).first()


def get_all_dishes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Dish).offset(skip).limit(limit).all()


def create_dish(db: Session, dish: DishCreate) -> Dish:
    db_dish = Dish(
        name=dish.name,
        weight=dish.weight,
        price=dish.price,
        calories=dish.calories,
        description=dish.description
    )
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return db_dish


def update_dish(db: Session, dish_id: int, dish_update: DishUpdate) -> Optional[Dish]:
    db_dish = get_dish_by_id(db, dish_id)
    if not db_dish:
        return None

    update_data = dish_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_dish, key, value)

    db.commit()
    db.refresh(db_dish)
    return db_dish


def delete_dish(db: Session, dish_id: int) -> bool:
    db_dish = get_dish_by_id(db, dish_id)
    if not db_dish:
        return False

    db.delete(db_dish)
    db.commit()
    return True