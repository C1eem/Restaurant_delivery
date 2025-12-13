from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

# Используем sha256_crypt, чтобы не зависеть от внешнего модуля bcrypt
# и избежать проблем с бэкендом на Windows.
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# JWT настройки
# Берём ключ из переменных окружения, если он не задан или пустой – используем безопасный дефолт.
SECRET_KEY = os.getenv("SECRET_KEY") or "dev-secret-key-change-in-development"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней


def hash_password(password: str) -> str:
    """Хеширует пароль."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создает JWT токен."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Декодирует JWT токен."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None