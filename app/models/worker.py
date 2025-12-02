from app.models.base import Base
from sqlalchemy import Column, Integer, String, Enum
import enum

class WorkerRole(enum.Enum):
    admin = "администратор"
    client = "клиент"
    courier = "курьер"
    manager = "менеджер"

class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True)
    login = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(Enum(WorkerRole), nullable=False)

    def __repr__(self):
        return (f"<Worker(id={self.id}, login='{self.login}', "
                f"email='{self.email}', name='{self.full_name}')>")