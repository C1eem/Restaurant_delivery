from typing import Optional, List

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


# Получить пользователя по ID
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


# Получить пользователя по логину
def get_user_by_login(db: Session, login: str) -> Optional[User]:
    return db.query(User).filter(User.login == login).first()


# Получить пользователя по email
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


# Получить пользователя по телефону
def get_user_by_phone(db: Session, phone_number: str) -> Optional[User]:
    return db.query(User).filter(User.phone_number == phone_number).first()


# Получить всех пользователей
def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


# Получить пользователей по роли
def get_users_by_role(db: Session, role: UserRole) -> List[User]:
    return db.query(User).filter(User.role == role).all()


# Создать пользователя
def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = hash_password(user.password)
    db_user = User(
        login=user.login,
        password_hash=hashed_password,
        full_name=user.full_name,
        phone_number=user.phone_number,
        email=user.email,
        delivery_address=user.delivery_address,
        role=UserRole.client  # По умолчанию client
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Обновить пользователя
def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    update_data = user_update.dict(exclude_unset=True)

    if "password" in update_data:
        update_data["password_hash"] = pwd_context.hash(update_data["password"])
        del update_data["password"]

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


# Обновить роль пользователя
def update_user_role(db: Session, login: str, role: UserRole) -> Optional[User]:
    db_user = get_user_by_login(db, login)
    if not db_user:
        return None
    db_user.role = role
    db.commit()
    db.refresh(db_user)
    return db_user


# Удалить пользователя
def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True


# Проверить логин и пароль
def check_user_password(db: Session, login: str, password: str) -> Optional[User]:
    user = get_user_by_login(db, login)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user