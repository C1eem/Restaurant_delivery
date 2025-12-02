from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.crud import order_item as crud
from app.schemas.order_item import OrderItemCreate, OrderItemResponse, OrderItemUpdate
from app.dependencies import get_db

router = APIRouter(prefix="/order-items", tags=["order-items"])

@router.post("/", response_model=OrderItemResponse, status_code=status.HTTP_201_CREATED)
def create_order_item(order_item: OrderItemCreate, db: Session = Depends(get_db)):
    return crud.create_order_item(db, order_item)

@router.get("/", response_model=List[OrderItemResponse])
def read_order_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    order_items = crud.get_all_order_items(db, skip=skip, limit=limit)
    return order_items

@router.get("/{order_item_id}", response_model=OrderItemResponse)
def read_order_item(order_item_id: int, db: Session = Depends(get_db)):
    order_item = crud.get_order_item_by_id(db, order_item_id)
    if not order_item:
        raise HTTPException(status_code=404, detail="Элемент заказа не найден")
    return order_item

@router.get("/order/{order_id}", response_model=List[OrderItemResponse])
def read_items_for_order(order_id: int, db: Session = Depends(get_db)):
    items = crud.get_items_for_order(db, order_id)
    return items

@router.put("/{order_item_id}", response_model=OrderItemResponse)
def update_order_item(
    order_item_id: int,
    order_item_update: OrderItemUpdate,
    db: Session = Depends(get_db)
):
    order_item = crud.update_order_item(db, order_item_id, order_item_update)
    if not order_item:
        raise HTTPException(status_code=404, detail="Элемент заказа не найден")
    return order_item

@router.delete("/{order_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_item(order_item_id: int, db: Session = Depends(get_db)):
    success = crud.delete_order_item(db, order_item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Элемент заказа не найден")