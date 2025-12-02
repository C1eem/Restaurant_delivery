from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Импортируем все роуты
from app.routes import (
    users,
    workers,
    dishes,
    ingredients,
    dish_ingredients,
    orders,
    order_items,
    pages,
)

# Создаем приложение FastAPI
app = FastAPI(
    title="Restaurant API",
    description="API для управления рестораном",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажи конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статика (CSS, JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключаем все роуты
app.include_router(pages.router)        # HTML-страницы
app.include_router(users.router)        # API пользователей
app.include_router(workers.router)      # API работников
app.include_router(dishes.router)       # API блюд
app.include_router(ingredients.router)  # API ингредиентов
app.include_router(dish_ingredients.router)
app.include_router(orders.router)
app.include_router(order_items.router)
