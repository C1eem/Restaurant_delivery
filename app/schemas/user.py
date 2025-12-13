from pydantic import BaseModel
from typing import Optional
import enum


class UserRole(str, enum.Enum):
    client = "client"
    manager = "manager"
    courier = "courier"
    admin = "admin"


# Для создания пользователя
class UserCreate(BaseModel):
    login: str
    password: str
    full_name: str
    phone_number: str
    email: str
    delivery_address: Optional[str] = None


# Для обновления пользователя
class UserUpdate(BaseModel):
    login: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    delivery_address: Optional[str] = None
    role: Optional[UserRole] = None


# Для ответа (то что возвращаем)
class UserResponse(BaseModel):
    id: int
    login: str
    full_name: str
    phone_number: str
    email: str
    role: UserRole
    delivery_address: Optional[str] = None

    class Config:
        from_attributes = True


# Для логина
class UserLogin(BaseModel):
    login: str
    password: str


# Для JWT токена
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"