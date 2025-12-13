"""
Скрипт для получения списка пользователей по ролям.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.crud import user as user_crud
from app.models.user import UserRole

def get_users_list():
    """Получает список пользователей по ролям."""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("СПИСОК ПОЛЬЗОВАТЕЛЕЙ ДЛЯ ВХОДА")
        print("=" * 60)
        
        # Администраторы
        admins = user_crud.get_users_by_role(db, UserRole.admin)
        print("\n📌 АДМИНИСТРАТОРЫ:")
        if admins:
            for admin in admins:
                print(f"   Логин: {admin.login:<20} | ФИО: {admin.full_name}")
        else:
            print("   (нет администраторов)")
        
        # Менеджеры
        managers = user_crud.get_users_by_role(db, UserRole.manager)
        print("\n👔 МЕНЕДЖЕРЫ:")
        if managers:
            for manager in managers:
                print(f"   Логин: {manager.login:<20} | ФИО: {manager.full_name}")
        else:
            print("   (нет менеджеров)")
        
        # Курьеры
        couriers = user_crud.get_users_by_role(db, UserRole.courier)
        print("\n🚴 КУРЬЕРЫ:")
        if couriers:
            for courier in couriers:
                print(f"   Логин: {courier.login:<20} | ФИО: {courier.full_name}")
        else:
            print("   (нет курьеров)")
        
        # Клиенты
        clients = user_crud.get_users_by_role(db, UserRole.client)
        print("\n👤 КЛИЕНТЫ (первые 5):")
        if clients:
            for client in clients[:5]:
                print(f"   Логин: {client.login:<20} | ФИО: {client.full_name}")
            if len(clients) > 5:
                print(f"   ... и ещё {len(clients) - 5} клиентов")
        else:
            print("   (нет клиентов)")
        
        print("\n" + "=" * 60)
        print("💡 Для входа используйте логин и пароль пользователя")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    get_users_list()

