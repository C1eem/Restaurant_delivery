import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

from app.db.session import Base, engine, get_db
from app.models.dish import Dish
from app.models.dish_in_menu import DishInMenu
from app.models.dish_ingredient import DishIngredient
from app.models.ingredient import Ingredient
from app.models.order import Order, OrderStatus  # Импортируем OrderStatus
from app.models.order_item import OrderItem
from app.models.user import User
from app.core.security import hash_password


# Проверяем существование базы данных
def check_and_create_database():
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "food_delivery_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "1234")

    database_url = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
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


def create_tables():
    print("Создание таблиц...")
    # Base.metadata.create_all(bind=engine)
    print("Таблицы созданы.")


def populate_test_data():
    print("Заполнение тестовыми данными...")
    db = next(get_db())

    try:
        print("Очистка существующих данных...")
        # Важно соблюдать порядок удаления из-за foreign keys
        db.query(OrderItem).delete()
        db.query(Order).delete()
        db.query(DishIngredient).delete()
        db.query(DishInMenu).delete()
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
            Ingredient(name="Сыр"),
            Ingredient(name="Помидоры"),
            Ingredient(name="Тесто"),
            Ingredient(name="Мясной фарш"),
            Ingredient(name="Соус"),
            Ingredient(name="Курица"),
            Ingredient(name="Салат"),
            Ingredient(name="Сухарики"),
            Ingredient(name="Соус Цезарь"),
        ]
        db.add_all(ingredients)
        db.flush()

        # Создание блюд (БЕЗ ЦЕНЫ)
        dishes = [
            Dish(
                name="Пирог",
                weight=500,
                calories=300,
                description="Вкусный пирог с ягодами",
            ),
            Dish(
                name="Печенье",
                weight=200,
                calories=150,
                description="Хрустящее печенье с шоколадом",
            ),
            Dish(
                name="Пицца Маргарита",
                weight=800,
                calories=850,
                description="Классическая пицца с сыром и томатами",
            ),
            Dish(
                name="Бургер",
                weight=450,
                calories=600,
                description="Сочный бургер с говядиной",
            ),
            Dish(
                name="Салат Цезарь",
                weight=350,
                calories=400,
                description="Классический салат с курицей",
            ),
            Dish(
                name="Паста Карбонара",
                weight=400,
                calories=550,
                description="Итальянская паста с беконом и сыром",
            ),
            Dish(
                name="Суп Том Ям",
                weight=350,
                calories=250,
                description="Острый тайский суп с креветками",
            ),
        ]
        db.add_all(dishes)
        db.flush()

        # Создание записей в меню (отдельная таблица с ценами)
        dishes_in_menu = [
            # Пирог - разные цены
            DishInMenu(dish_id=dishes[0].id, price=10.99),  # Маленький
            DishInMenu(dish_id=dishes[0].id, price=15.99),  # Большой

            # Печенье
            DishInMenu(dish_id=dishes[1].id, price=5.99),  # Порция 200г

            # Пицца Маргарита
            DishInMenu(dish_id=dishes[2].id, price=15.50),  # Стандартная
            DishInMenu(dish_id=dishes[2].id, price=12.99),  # По акции

            # Бургер
            DishInMenu(dish_id=dishes[3].id, price=12.75),  # Классический

            # Салат Цезарь
            DishInMenu(dish_id=dishes[4].id, price=8.25),  # Стандартный
            DishInMenu(dish_id=dishes[4].id, price=10.50),  # С креветками

            # Паста Карбонара
            DishInMenu(dish_id=dishes[5].id, price=11.99),

            # Суп Том Ям
            DishInMenu(dish_id=dishes[6].id, price=9.75),
        ]
        db.add_all(dishes_in_menu)
        db.flush()

        # Создание связей между блюдами и ингредиентами
        dish_ingredients = [
            # Пирог
            DishIngredient(dish_id=dishes[0].id, ingredient_id=ingredients[0].id),  # Мука
            DishIngredient(dish_id=dishes[0].id, ingredient_id=ingredients[1].id),  # Яйца
            DishIngredient(dish_id=dishes[0].id, ingredient_id=ingredients[2].id),  # Соль
            DishIngredient(dish_id=dishes[0].id, ingredient_id=ingredients[3].id),  # Сахар

            # Печенье
            DishIngredient(dish_id=dishes[1].id, ingredient_id=ingredients[0].id),  # Мука
            DishIngredient(dish_id=dishes[1].id, ingredient_id=ingredients[3].id),  # Сахар
            DishIngredient(dish_id=dishes[1].id, ingredient_id=ingredients[4].id),  # Масло

            # Пицца Маргарита
            DishIngredient(dish_id=dishes[2].id, ingredient_id=ingredients[5].id),  # Сыр
            DishIngredient(dish_id=dishes[2].id, ingredient_id=ingredients[6].id),  # Помидоры
            DishIngredient(dish_id=dishes[2].id, ingredient_id=ingredients[7].id),  # Тесто
            DishIngredient(dish_id=dishes[2].id, ingredient_id=ingredients[9].id),  # Соус

            # Бургер
            DishIngredient(dish_id=dishes[3].id, ingredient_id=ingredients[8].id),  # Мясной фарш
            DishIngredient(dish_id=dishes[3].id, ingredient_id=ingredients[5].id),  # Сыр

            # Салат Цезарь
            DishIngredient(dish_id=dishes[4].id, ingredient_id=ingredients[10].id),  # Курица
            DishIngredient(dish_id=dishes[4].id, ingredient_id=ingredients[11].id),  # Салат
            DishIngredient(dish_id=dishes[4].id, ingredient_id=ingredients[12].id),  # Сухарики
            DishIngredient(dish_id=dishes[4].id, ingredient_id=ingredients[13].id),  # Соус Цезарь

            # Паста Карбонара
            DishIngredient(dish_id=dishes[5].id, ingredient_id=ingredients[1].id),  # Яйца
            DishIngredient(dish_id=dishes[5].id, ingredient_id=ingredients[5].id),  # Сыр

            # Суп Том Ям
            DishIngredient(dish_id=dishes[6].id, ingredient_id=ingredients[6].id),  # Помидоры
        ]
        db.add_all(dish_ingredients)

        # Создание пользователей
        users = [
            User(
                login="admin",
                password_hash=hash_password("admin123"),
                full_name="Администратор Системы",
                phone_number="1234567890",
                email="admin@example.com",
            ),
            User(
                login="client1",
                password_hash=hash_password("client123"),
                full_name="Иван Иванов",
                phone_number="0987654321",
                email="ivanov@example.com",
            ),
            User(
                login="courier1",
                password_hash=hash_password("courier123"),
                full_name="Петр Петров (Курьер)",
                phone_number="1112223334",
                email="courier@example.com",
            ),
            User(
                login="manager1",
                password_hash=hash_password("manager123"),
                full_name="Анна Сидорова (Менеджер)",
                phone_number="5556667778",
                email="manager@example.com",
            ),
            User(
                login="client2",
                password_hash=hash_password("client456"),
                full_name="Мария Смирнова",
                phone_number="9998887776",
                email="smirnova@example.com",
            ),
            User(
                login="chef1",
                password_hash=hash_password("chef123"),
                full_name="Олег Шеф-повар",
                phone_number="3334445556",
                email="chef@example.com",
            ),
        ]
        db.add_all(users)
        db.flush()

        # Создание заказов с правильными статусами из OrderStatus
        orders = [
            # Новый заказ - ожидает обработки
            Order(
                delivery_address="ул. Центральная, д. 1, кв. 5",
                worker_id=None,  # Еще не назначен курьер
                total_amount=43.47,  # (2 * 10.99) + 5.99 + 15.50
                user_id=users[1].id,  # client1
                status=OrderStatus.pending,
            ),

            # Заказ в процессе приготовления
            Order(
                delivery_address="ул. Лесная, д. 2, кв. 10",
                worker_id=None,  # Пока нет курьера
                total_amount=32.97,  # 3 * 10.99
                user_id=users[4].id,  # client2
                status=OrderStatus.cooking,
            ),

            # Заказ готов к выдаче
            Order(
                delivery_address="пр. Мира, д. 15, офис 305",
                worker_id=users[2].id,  # Назначен курьер courier1
                total_amount=28.25,  # 12.75 + 15.50
                user_id=users[3].id,  # manager1
                status=OrderStatus.ready,
            ),

            # Заказ в процессе доставки
            Order(
                delivery_address="ул. Садовая, д. 25, кв. 12",
                worker_id=users[2].id,  # Курьер в пути
                total_amount=24.74,  # 5.99 + 9.75 + 9.00
                user_id=users[1].id,  # client1
                status=OrderStatus.delivering,
            ),

            # Завершенный заказ
            Order(
                delivery_address="ул. Пушкина, д. 10, кв. 3",
                worker_id=users[2].id,  # Курьер доставил
                total_amount=35.48,  # 15.99 + 11.99 + 7.50
                user_id=users[4].id,  # client2
                status=OrderStatus.completed,
            ),

            # Отмененный заказ
            Order(
                delivery_address="ул. Гагарина, д. 5, кв. 7",
                worker_id=None,
                total_amount=18.50,  # 8.25 + 10.25
                user_id=users[1].id,  # client1
                status=OrderStatus.cancelled,
            ),
        ]
        db.add_all(orders)
        db.flush()

        # Создание элементов заказов
        # Каждый OrderItem ссылается на dish_in_menu_id (не dish_id!)
        order_items = [
            # Заказ 1 (pending): 2 маленьких пирога, печенье, пицца стандартная
            OrderItem(order_id=orders[0].id, dish_in_menu_id=dishes_in_menu[0].id, quantity=2),  # Пирог мал.
            OrderItem(order_id=orders[0].id, dish_in_menu_id=dishes_in_menu[2].id, quantity=1),  # Печенье
            OrderItem(order_id=orders[0].id, dish_in_menu_id=dishes_in_menu[3].id, quantity=1),  # Пицца стан.

            # Заказ 2 (cooking): 3 больших пирога
            OrderItem(order_id=orders[1].id, dish_in_menu_id=dishes_in_menu[1].id, quantity=3),  # Пирог бол.

            # Заказ 3 (ready): бургер и пицца по акции
            OrderItem(order_id=orders[2].id, dish_in_menu_id=dishes_in_menu[5].id, quantity=1),  # Бургер
            OrderItem(order_id=orders[2].id, dish_in_menu_id=dishes_in_menu[4].id, quantity=1),  # Пицца акция

            # Заказ 4 (delivering): печенье, суп, салат стандартный
            OrderItem(order_id=orders[3].id, dish_in_menu_id=dishes_in_menu[2].id, quantity=1),  # Печенье
            OrderItem(order_id=orders[3].id, dish_in_menu_id=dishes_in_menu[9].id, quantity=1),  # Суп
            OrderItem(order_id=orders[3].id, dish_in_menu_id=dishes_in_menu[6].id, quantity=1),  # Салат стан.

            # Заказ 5 (completed): большой пирог, паста, салат с креветками
            OrderItem(order_id=orders[4].id, dish_in_menu_id=dishes_in_menu[1].id, quantity=1),  # Пирог бол.
            OrderItem(order_id=orders[4].id, dish_in_menu_id=dishes_in_menu[8].id, quantity=1),  # Паста
            OrderItem(order_id=orders[4].id, dish_in_menu_id=dishes_in_menu[7].id, quantity=1),  # Салат кревет.

            # Заказ 6 (cancelled): салат стандартный и что-то еще
            OrderItem(order_id=orders[5].id, dish_in_menu_id=dishes_in_menu[6].id, quantity=1),  # Салат стан.
            OrderItem(order_id=orders[5].id, dish_in_menu_id=dishes_in_menu[2].id, quantity=2),  # Печенье x2
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
        # Только реально существующие последовательности
        sequences = [
            "dish_ingredients_id_seq",
            "dishes_id_seq",
            "dishes_in_menu_id_seq",
            "ingredients_id_seq",
            "orders_id_seq",
            "order_items_id_seq",
            "users_id_seq",
            # workers_id_seq больше нет
        ]

        for sequence in sequences:
            try:
                db.execute(text(f"ALTER SEQUENCE {sequence} RESTART WITH 1"))
                print(f"Сброшена последовательность: {sequence}")
            except Exception as e:
                print(f"Предупреждение: не удалось сбросить {sequence}: {e}")

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