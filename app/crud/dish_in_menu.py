from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.dish_in_menu import DishInMenu
from app.schemas.dish_in_menu import DishInMenuCreate, DishInMenuUpdate


def get_all_dishes_in_menu(db: Session, skip: int = 0, limit: int = 100) -> List[DishInMenu]:
    """
    Получить все записи о блюдах в меню
    """
    return db.query(DishInMenu).offset(skip).limit(limit).all()


def get_dish_in_menu_by_id(db: Session, dish_in_menu_id: int) -> Optional[DishInMenu]:
    """
    Получить запись о блюде в меню по ID
    """
    return db.query(DishInMenu).filter(DishInMenu.id == dish_in_menu_id).first()


def get_dishes_for_menu(db: Session, menu_id: int) -> List[DishInMenu]:
    """
    Получить все блюда для конкретного меню
    Примечание: у вас в модели пока нет прямого поля menu_id,
    но возможно оно появится позже. Оставил для примера структуры.
    """
    # Если у DishInMenu появится поле menu_id:
    # return db.query(DishInMenu).filter(DishInMenu.menu_id == menu_id).all()

    # Пока возвращаем все блюда в меню
    return get_all_dishes_in_menu(db)


def get_dish_in_menu_by_dish_id(db: Session, dish_id: int) -> Optional[DishInMenu]:
    """
    Получить запись о блюде в меню по ID блюда
    """
    return db.query(DishInMenu).filter(DishInMenu.dish_id == dish_id).first()


def get_dishes_in_menu_by_price_range(db: Session, min_price: float = 0, max_price: float = 10000) -> List[DishInMenu]:
    """
    Получить блюда в меню в указанном диапазоне цен
    """
    return db.query(DishInMenu) \
        .filter(DishInMenu.price >= min_price, DishInMenu.price <= max_price) \
        .all()


def create_dish_in_menu(db: Session, dish_in_menu: DishInMenuCreate) -> DishInMenu:
    """
    Создать новую запись о блюде в меню
    """
    db_dish_in_menu = DishInMenu(
        dish_id=dish_in_menu.dish_id,
        price=dish_in_menu.price
    )
    db.add(db_dish_in_menu)
    db.commit()
    db.refresh(db_dish_in_menu)
    return db_dish_in_menu


def update_dish_in_menu(db: Session, dish_in_menu_id: int,
                        dish_in_menu_update: DishInMenuUpdate) -> Optional[DishInMenu]:
    """
    Обновить запись о блюде в меню
    """
    db_dish_in_menu = get_dish_in_menu_by_id(db, dish_in_menu_id)
    if not db_dish_in_menu:
        return None

    update_data = dish_in_menu_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_dish_in_menu, key, value)

    db.commit()
    db.refresh(db_dish_in_menu)
    return db_dish_in_menu


def delete_dish_in_menu(db: Session, dish_in_menu_id: int) -> bool:
    """
    Удалить запись о блюде в меню
    """
    db_dish_in_menu = get_dish_in_menu_by_id(db, dish_in_menu_id)
    if not db_dish_in_menu:
        return False

    db.delete(db_dish_in_menu)
    db.commit()
    return True


def bulk_create_dishes_in_menu(db: Session, dishes_in_menu: List[DishInMenuCreate]) -> List[DishInMenu]:
    """
    Массовое создание записей о блюдах в меню
    """
    db_dishes = []
    for dish_data in dishes_in_menu:
        db_dish = DishInMenu(
            dish_id=dish_data.dish_id,
            price=dish_data.price
        )
        db.add(db_dish)
        db_dishes.append(db_dish)

    db.commit()
    # Обновляем объекты, чтобы получить их ID
    for db_dish in db_dishes:
        db.refresh(db_dish)

    return db_dishes


def get_dish_in_menu_by_dish_and_price(db: Session, dish_id: int, price: float) -> Optional[DishInMenu]:
    """
    Найти запись о блюде в меню по ID блюда и цене
    Полезно для проверки дубликатов
    """
    return db.query(DishInMenu) \
        .filter(DishInMenu.dish_id == dish_id, DishInMenu.price == price) \
        .first()


def update_dish_price(db: Session, dish_in_menu_id: int, new_price: float) -> Optional[DishInMenu]:
    """
    Обновить только цену блюда в меню
    """
    db_dish_in_menu = get_dish_in_menu_by_id(db, dish_in_menu_id)
    if not db_dish_in_menu:
        return None

    db_dish_in_menu.price = new_price
    db.commit()
    db.refresh(db_dish_in_menu)
    return db_dish_in_menu