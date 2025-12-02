from passlib.context import CryptContext

# Используем sha256_crypt, чтобы не зависеть от внешнего модуля bcrypt
# и избежать проблем с бэкендом на Windows.
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеширует пароль."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль."""
    return pwd_context.verify(plain_password, hashed_password)