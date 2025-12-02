from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.crud import user as crud
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserLogin
from app.dependencies import get_db

router = APIRouter(prefix="/users", tags=["users"])


# Создать пользователя
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Проверяем уникальность логина
    if crud.get_user_by_login(db, user.login):
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким логином уже существует"
        )

    # Проверяем уникальность email
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует"
        )

    # Создаем пользователя
    return crud.create_user(db, user)


# Получить всех пользователей
@router.get("/", response_model=List[UserResponse])
def read_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    users = crud.get_all_users(db, skip=skip, limit=limit)
    return users


# Получить пользователя по ID
@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


# Обновить пользователя
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
        user_id: int,
        user_update: UserUpdate,
        db: Session = Depends(get_db)
):
    user = crud.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


# Удалить пользователя
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Пользователь не найден")


# Аутентификация пользователя
@router.post("/login/")
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    user = crud.check_user_password(db, credentials.login, credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль"
        )
    return {"message": "Успешный вход", "user_id": user.id}