from typing import Optional

from sqlalchemy.orm import Session
from datetime import datetime
from app.models.order import Order, OrderStatus
from app.schemas.order import OrderCreate, OrderUpdate


def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
    return db.query(Order).filter(Order.id == order_id).first()


def get_all_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Order).offset(skip).limit(limit).all()


def get_orders_by_user(db: Session, user_id: int):
    return db.query(Order).filter(Order.user_id == user_id).all()


def get_orders_by_status(db: Session, status: OrderStatus):
    return db.query(Order).filter(Order.status == status).all()


def get_orders_by_courier(db: Session, courier_id: int):
    return db.query(Order).filter(Order.courier_id == courier_id).all()


def create_order(db: Session, order: OrderCreate) -> Order:
    db_order = Order(
        delivery_address=order.delivery_address,
        user_id=order.user_id,
        courier_id=order.courier_id,
        total_amount=order.total_amount,
        status=order.status,
        created_at=datetime.utcnow()
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def update_order(db: Session, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
    db_order = get_order_by_id(db, order_id)
    if not db_order:
        return None

    update_data = order_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_order, key, value)

    db.commit()
    db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int) -> bool:
    db_order = get_order_by_id(db, order_id)
    if not db_order:
        return False

    db.delete(db_order)
    db.commit()
    return True