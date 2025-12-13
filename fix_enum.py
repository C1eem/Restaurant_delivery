"""
Скрипт для исправления enum userrole в базе данных.
Обновляет значения с русских на английские.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from sqlalchemy import text

def fix_enum():
    """Обновляет enum userrole в базе данных."""
    db = SessionLocal()
    try:
        print("Обновление enum userrole...")
        
        # Удаляем старый enum (CASCADE удалит все зависимости)
        db.execute(text("DROP TYPE IF EXISTS userrole CASCADE"))
        db.commit()
        print("✓ Старый enum удален")
        
        # Создаем новый enum с английскими значениями
        db.execute(text("CREATE TYPE userrole AS ENUM ('client', 'manager', 'courier', 'admin')"))
        db.commit()
        print("✓ Новый enum создан")
        
        # Добавляем колонку role если её нет
        db.execute(text("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (SELECT FROM information_schema.columns 
                              WHERE table_name = 'users' AND column_name = 'role') THEN
                    ALTER TABLE users ADD COLUMN role userrole NOT NULL DEFAULT 'client';
                END IF;
            END $$;
        """))
        db.commit()
        print("✓ Колонка role проверена")
        
        # Обновляем существующие значения (если есть старые русские значения)
        db.execute(text("""
            UPDATE users 
            SET role = CASE 
                WHEN role::text = 'клиент' THEN 'client'::userrole
                WHEN role::text = 'менеджер' THEN 'manager'::userrole
                WHEN role::text = 'курьер' THEN 'courier'::userrole
                WHEN role::text = 'администратор' THEN 'admin'::userrole
                ELSE role
            END
            WHERE role::text IN ('клиент', 'менеджер', 'курьер', 'администратор');
        """))
        db.commit()
        print("✓ Значения обновлены")
        
        print("\n✓ Enum успешно обновлен!")
        
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_enum()

