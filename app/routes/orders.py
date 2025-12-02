from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.crud import order as crud
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate, OrderStatus
from app.dependencies import get_db

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db, order)

@router.get("/", response_model=List[OrderResponse])
def read_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    orders = crud.get_all_orders(db, skip=skip, limit=limit)
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
def read_order(order_id: int, db: Session = Depends(get_db)):
    order = crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return order

@router.get("/user/{user_id}", response_model=List[OrderResponse])
def read_user_orders(user_id: int, db: Session = Depends(get_db)):
    orders = crud.get_orders_by_user(db, user_id)
    return orders

@router.get("/status/{status}", response_model=List[OrderResponse])
def read_orders_by_status(status: OrderStatus, db: Session = Depends(get_db)):
    orders = crud.get_orders_by_status(db, status)
    return orders

@router.get("/worker/{worker_id}", response_model=List[OrderResponse])
def read_orders_by_worker(worker_id: int, db: Session = Depends(get_db)):
    orders = crud.get_orders_by_worker(db, worker_id)
    return orders

@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db)
):
    order = crud.update_order(db, order_id, order_update)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    success = crud.delete_order(db, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Заказ не найден")