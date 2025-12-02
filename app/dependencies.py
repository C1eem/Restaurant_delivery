from typing import Generator
from sqlalchemy.orm import Session
from .db.session import SessionLocal

# Зависимость для получения сессии БД
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()