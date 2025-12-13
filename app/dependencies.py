from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .db.session import SessionLocal
from .crud import user as user_crud
from .models.user import User
from .core.security import decode_access_token

security = HTTPBearer()

# Зависимость для получения сессии БД
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Зависимость для получения текущего пользователя из JWT токена
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
        )
    user = user_crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )
    return user


# Зависимость для получения текущего пользователя из cookie (для обратной совместимости)
def get_current_user_from_cookie(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = decode_access_token(token)
    if payload is None:
        return None
    user_id: int = payload.get("sub")
    if user_id is None:
        return None
    return user_crud.get_user_by_id(db, user_id)