import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

from app.db.session import Base, engine, get_db
from app.models.dish import Dish
from app.models.dish_ingredient import DishIngredient
from app.models.ingredient import Ingredient
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.user import User
# from app.models.worker import Worker, WorkerRole
from app.core.security import hash_password


# Проверяем существование базы данных
def check_and_create_database():
    # Получаем параметры из переменных окружения
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "food_delivery_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "1234")

    # Формируем строку подключения
    database_url = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


    # Проверяем существование базы данных
    conn = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}"
    engine = create_engine(conn)

    with engine.connect() as test_conn:
        try:
            test_conn.execute(text("SELECT 1"))
        except Exception as e:
            print(f"База данных не найдена. Создаем новую базу данных...")
            test_conn.execute(text(f'CREATE DATABASE "{DB_NAME}"'))
            print("База данных успешно создана.")
        finally:
            test_conn.close()


# Создание таблиц
def create_tables():
    print("Создание таблиц...")
    #Base.metadata.create_all(bind=engine)
    print("Таблицы созданы.")


# Заполнение тестовыми данными
def populate_test_data():
    print("Заполнение тестовыми данными...")
    db = next(get_db())

    try:
        print("Очистка существующих данных...")
        db.query(OrderItem).delete()
        db.query(Order).delete()
        db.query(DishIngredient).delete()
        db.query(Dish).delete()
        db.query(Ingredient).delete()
        db.query(User).delete()
        db.flush()

        # Создание ингредиентов
        ingredients = [
            Ingredient(name="Мука"),
            Ingredient(name="Яйца"),
            Ingredient(name="Соль"),
            Ingredient(name="Сахар"),
            Ingredient(name="Масло"),
        ]
        db.add_all(ingredients)
        db.flush()  # Получаем ID для ингредиентов, но не коммитим всю транзакцию

        # Создание блюд
        dishes = [
            Dish(
                name="Пирог",
                weight=500,
                price=10.99,
                calories=300,
                description="Вкусный пирог",
            ),
            Dish(
                name="Печенье",
                weight=200,
                price=5.99,
                calories=150,
                description="Хрустящее печенье",
            ),
        ]
        db.add_all(dishes)
        db.flush()  # Получаем ID для блюд, но не коммитим всю транзакцию

        # Создание связей между блюдами и ингредиентами
        dish_ingredients = [
            DishIngredient(dish_id=dishes[0].id, ingredient_id=ingredients[0].id),
            DishIngredient(dish_id=dishes[0].id, ingredient_id=ingredients[1].id),
            DishIngredient(dish_id=dishes[0].id, ingredient_id=ingredients[2].id),
            DishIngredient(dish_id=dishes[1].id, ingredient_id=ingredients[3].id),
            DishIngredient(dish_id=dishes[1].id, ingredient_id=ingredients[4].id),
        ]
        db.add_all(dish_ingredients)

        # Создание пользователей
        users = [
            User(
                login="admin",
                password_hash=hash_password("admin123"),
                full_name="Администратор",
                phone_number="1234567890",
                email="admin@example.com",
            ),
            User(
                login="client",
                password_hash=hash_password("client123"),
                full_name="Клиент",
                phone_number="0987654321",
                email="client@example.com",
            ),
        ]
        db.add_all(users)
        db.flush()  # Получаем ID для пользователей



        # Создание заказов
        orders = [
            Order(
                delivery_address="ул. Центральная, д. 1",
                worker_id=users[1].id,
                total_amount=20.98,
                user_id=users[0].id,
            ),
            Order(
                delivery_address="ул. Лесная, д. 2",
                worker_id=None,
                total_amount=10.99,
                user_id=users[1].id,
            ),
        ]
        db.add_all(orders)
        db.flush()  # Получаем ID для заказов

        # Создание элементов заказов
        order_items = [
            OrderItem(order_id=orders[0].id, dish_id=dishes[0].id, quantity=2),
            OrderItem(order_id=orders[0].id, dish_id=dishes[1].id, quantity=1),
            OrderItem(order_id=orders[1].id, dish_id=dishes[0].id, quantity=3),
        ]
        db.add_all(order_items)

        db.commit()
        print("Тестовые данные успешно добавлены.")

    except Exception as e:
        db.rollback()
        print(f"Ошибка при заполнении данными: {e}")
        raise


def reset_sequences():
    """Сбрасывает все последовательности к начальным значениям"""
    print("Сброс последовательностей...")
    db = next(get_db())

    try:
        # Список всех таблиц и их последовательностей
        sequences = [
            "dish_ingredients_id_seq",
            "dishes_id_seq",
            "ingredients_id_seq",
            "orders_id_seq",
            "order_items_id_seq",
            "users_id_seq",
            "workers_id_seq"
        ]

        for sequence in sequences:
            db.execute(text(f"ALTER SEQUENCE {sequence} RESTART WITH 1"))

        db.commit()
        print("Последовательности сброшены.")
    except Exception as e:
        db.rollback()
        print(f"Ошибка при сбросе последовательностей: {e}")


if __name__ == "__main__":
    check_and_create_database()
    create_tables()
    reset_sequences()
    populate_test_data()
    print("База данных инициализирована успешно.")