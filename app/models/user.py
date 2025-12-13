from sqlalchemy import Column, Integer, String, Enum
from app.models.base import Base
import enum


class UserRole(enum.Enum):
    client = "client"
    manager = "manager"
    courier = "courier"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.client)
    delivery_address = Column(String, nullable=True)

    def __repr__(self):
        return (f"<User(id={self.id}, login='{self.login}', "
                f"email='{self.email}', name='{self.full_name}', role='{self.role}')>")