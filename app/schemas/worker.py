from pydantic import BaseModel
from typing import Optional
import enum


class WorkerRole(str, enum.Enum):
    admin = "администратор"
    client = "клиент"
    courier = "курьер"
    manager = "менеджер"


class WorkerCreate(BaseModel):
    login: str
    password: str
    full_name: str
    phone_number: str
    email: str
    role: WorkerRole


class WorkerUpdate(BaseModel):
    login: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    role: Optional[WorkerRole] = None


class WorkerResponse(BaseModel):
    id: int
    login: str
    full_name: str
    phone_number: str
    email: str
    role: WorkerRole

    class Config:
        from_attributes = True


class WorkerLogin(BaseModel):
    login: str
    password: str