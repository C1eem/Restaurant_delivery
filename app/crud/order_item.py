from typing import Optional

from sqlalchemy.orm import Session
from app.models.order_item import OrderItem
from app.schemas.order_item import OrderItemCreate, OrderItemUpdate

def get_all_order_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(OrderItem).offset(skip).limit(limit).all()


def get_order_item_by_id(db: Session, order_item_id: int) -> Optional[OrderItem]:
    return db.query(OrderItem).filter(OrderItem.id == order_item_id).first()


def get_items_for_order(db: Session, order_id: int):
    return db.query(OrderItem).filter(OrderItem.order_id == order_id).all()


def create_order_item(db: Session, order_item: OrderItemCreate) -> OrderItem:
    db_order_item = OrderItem(
        order_id=order_item.order_id,
        dish_id=order_item.dish_id,
        quantity=order_item.quantity
    )
    db.add(db_order_item)
    db.commit()
    db.refresh(db_order_item)
    return db_order_item


def update_order_item(db: Session, order_item_id: int, order_item_update: OrderItemUpdate) -> Optional[OrderItem]:
    db_order_item = get_order_item_by_id(db, order_item_id)
    if not db_order_item:
        return None

    update_data = order_item_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_order_item, key, value)

    db.commit()
    db.refresh(db_order_item)
    return db_order_item


def delete_order_item(db: Session, order_item_id: int) -> bool:
    db_order_item = get_order_item_by_id(db, order_item_id)
    if not db_order_item:
        return False

    db.delete(db_order_item)
    db.commit()
    return True