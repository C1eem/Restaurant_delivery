"""
Скрипт для создания тестовых пользователей (админов, менеджеров, курьеров).
Запуск: python create_test_users.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.crud import user as user_crud
from app.models.user import UserRole
from app.schemas.user import UserCreate

# Тестовые пользователи для создания
TEST_USERS = [
    # Администраторы
    {
        "login": "admin",
        "password": "admin123",
        "full_name": "Главный Администратор",
        "phone_number": "+79991234567",
        "email": "admin@restaurant.ru",
        "role": UserRole.admin,
        "delivery_address": None
    },
    {
        "login": "admin2",
        "password": "admin123",
        "full_name": "Администратор 2",
        "phone_number": "+79991234568",
        "email": "admin2@restaurant.ru",
        "role": UserRole.admin,
        "delivery_address": None
    },
    # Менеджеры
    {
        "login": "manager",
        "password": "manager123",
        "full_name": "Менеджер Иванов",
        "phone_number": "+79991234569",
        "email": "manager@restaurant.ru",
        "role": UserRole.manager,
        "delivery_address": None
    },
    {
        "login": "manager1",
        "password": "manager123",
        "full_name": "Менеджер Петров",
        "phone_number": "+79991234570",
        "email": "manager1@restaurant.ru",
        "role": UserRole.manager,
        "delivery_address": None
    },
    {
        "login": "manager2",
        "password": "manager123",
        "full_name": "Менеджер Сидоров",
        "phone_number": "+79991234571",
        "email": "manager2@restaurant.ru",
        "role": UserRole.manager,
        "delivery_address": None
    },
    # Курьеры
    {
        "login": "courier",
        "password": "courier123",
        "full_name": "Курьер Смирнов",
        "phone_number": "+79991234572",
        "email": "courier@restaurant.ru",
        "role": UserRole.courier,
        "delivery_address": "г. Москва, ул. Курьерская, д. 1"
    },
    {
        "login": "courier1",
        "password": "courier123",
        "full_name": "Курьер Козлов",
        "phone_number": "+79991234573",
        "email": "courier1@restaurant.ru",
        "role": UserRole.courier,
        "delivery_address": "г. Москва, ул. Доставки, д. 2"
    },
    {
        "login": "courier2",
        "password": "courier123",
        "full_name": "Курьер Волков",
        "phone_number": "+79991234574",
        "email": "courier2@restaurant.ru",
        "role": UserRole.courier,
        "delivery_address": "г. Москва, ул. Транспортная, д. 3"
    },
    {
        "login": "courier3",
        "password": "courier123",
        "full_name": "Курьер Лебедев",
        "phone_number": "+79991234575",
        "email": "courier3@restaurant.ru",
        "role": UserRole.courier,
        "delivery_address": "г. Москва, ул. Скоростная, д. 4"
    },
]


def create_test_users():
    """Создает тестовых пользователей."""
    db = SessionLocal()
    created_count = 0
    skipped_count = 0
    
    try:
        print("=" * 70)
        print("СОЗДАНИЕ ТЕСТОВЫХ ПОЛЬЗОВАТЕЛЕЙ")
        print("=" * 70)
        
        for user_data in TEST_USERS:
            # Проверяем, существует ли пользователь
            existing = user_crud.get_user_by_login(db, user_data["login"])
            if existing:
                print(f"⚠ Пользователь '{user_data['login']}' уже существует, пропускаем")
                skipped_count += 1
                continue
            
            # Проверяем email
            existing_email = user_crud.get_user_by_email(db, user_data["email"])
            if existing_email:
                print(f"⚠ Email '{user_data['email']}' уже используется, пропускаем")
                skipped_count += 1
                continue
            
            # Проверяем телефон
            existing_phone = user_crud.get_user_by_email(db, user_data["phone_number"])
            if existing_phone:
                print(f"⚠ Телефон '{user_data['phone_number']}' уже используется, пропускаем")
                skipped_count += 1
                continue
            
            # Создаем пользователя
            user_create = UserCreate(
                login=user_data["login"],
                password=user_data["password"],
                full_name=user_data["full_name"],
                phone_number=user_data["phone_number"],
                email=user_data["email"],
                delivery_address=user_data["delivery_address"]
            )
            
            user = user_crud.create_user(db, user_create)
            
            # Обновляем роль
            user_crud.update_user_role(db, user_data["login"], user_data["role"])
            
            role_name = {
                UserRole.admin: "Администратор",
                UserRole.manager: "Менеджер",
                UserRole.courier: "Курьер",
                UserRole.client: "Клиент"
            }.get(user_data["role"], "Неизвестно")
            
            print(f"✓ Создан {role_name}: {user_data['login']} ({user_data['full_name']})")
            created_count += 1
        
        print("\n" + "=" * 70)
        print(f"✓ Создано пользователей: {created_count}")
        print(f"⚠ Пропущено: {skipped_count}")
        print("=" * 70)
        
        # Выводим список для входа
        print("\n" + "=" * 70)
        print("ЛОГИНЫ И ПАРОЛИ ДЛЯ ВХОДА")
        print("=" * 70)
        
        print("\n📌 АДМИНИСТРАТОРЫ:")
        print("   Логин: admin      | Пароль: admin123")
        print("   Логин: admin2     | Пароль: admin123")
        
        print("\n👔 МЕНЕДЖЕРЫ:")
        print("   Логин: manager    | Пароль: manager123")
        print("   Логин: manager1   | Пароль: manager123")
        print("   Логин: manager2   | Пароль: manager123")
        
        print("\n🚴 КУРЬЕРЫ:")
        print("   Логин: courier    | Пароль: courier123")
        print("   Логин: courier1   | Пароль: courier123")
        print("   Логин: courier2   | Пароль: courier123")
        print("   Логин: courier3   | Пароль: courier123")
        
        print("\n" + "=" * 70)
        print("💡 Используйте эти данные для входа в систему")
        print("=" * 70)
        
    except Exception as e:
        print(f"✗ Ошибка при создании пользователей: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_users()

