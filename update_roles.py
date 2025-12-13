"""
Скрипт для обновления ролей пользователей.
Запуск: python update_roles.py
"""
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.crud import user as user_crud
from app.models.user import UserRole

# Массивы логинов для каждой роли
ADMIN_LOGINS = [
    "admin",
    "admin2",
    "administrator",
    # Добавьте сюда логины администраторов
]

MANAGER_LOGINS = [
    "manager",
    "manager1",
    "manager2",
    # Добавьте сюда логины менеджеров
]

COURIER_LOGINS = [
    "courier",
    "courier1",
    "courier2",
    "courier3",
    # Добавьте сюда логины курьеров
]


def update_roles():
    """Обновляет роли пользователей согласно массивам логинов."""
    db = SessionLocal()
    try:
        updated_count = 0
        
        # Обновляем администраторов
        for login in ADMIN_LOGINS:
            user = user_crud.get_user_by_login(db, login)
            if user:
                user_crud.update_user_role(db, login, UserRole.admin)
                print(f"✓ Обновлена роль пользователя '{login}' на 'администратор'")
                updated_count += 1
            else:
                print(f"⚠ Пользователь с логином '{login}' не найден")
        
        # Обновляем менеджеров
        for login in MANAGER_LOGINS:
            user = user_crud.get_user_by_login(db, login)
            if user:
                user_crud.update_user_role(db, login, UserRole.manager)
                print(f"✓ Обновлена роль пользователя '{login}' на 'менеджер'")
                updated_count += 1
            else:
                print(f"⚠ Пользователь с логином '{login}' не найден")
        
        # Обновляем курьеров
        for login in COURIER_LOGINS:
            user = user_crud.get_user_by_login(db, login)
            if user:
                user_crud.update_user_role(db, login, UserRole.courier)
                print(f"✓ Обновлена роль пользователя '{login}' на 'курьер'")
                updated_count += 1
            else:
                print(f"⚠ Пользователь с логином '{login}' не найден")
        
        print(f"\n✓ Всего обновлено ролей: {updated_count}")
        
    except Exception as e:
        print(f"✗ Ошибка при обновлении ролей: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Обновление ролей пользователей...")
    print("=" * 50)
    update_roles()
    print("=" * 50)
    print("Готово!")

