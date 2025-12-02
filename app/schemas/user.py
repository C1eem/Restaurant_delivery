from pydantic import BaseModel
from typing import Optional


# Для создания пользователя
class UserCreate(BaseModel):
    login: str
    password: str
    full_name: str
    phone_number: str
    email: str


# Для обновления пользователя
class UserUpdate(BaseModel):
    login: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None


# Для ответа (то что возвращаем)
class UserResponse(BaseModel):
    id: int
    login: str
    full_name: str
    phone_number: str
    email: str

    class Config:
        from_attributes = True


# Для логина
class UserLogin(BaseModel):
    login: str
    password: str