from typing import Optional, List

from fastapi import APIRouter, Depends, Request, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.dependencies import get_db
from app.crud import dish as dish_crud
from app.crud import user as user_crud
from app.crud import worker as worker_crud
from app.crud import order as order_crud
from app.crud import order_item as order_item_crud
from app.schemas.worker import WorkerRole
from app.schemas.user import UserCreate
from app.schemas.order import OrderUpdate, OrderCreate
from app.schemas.dish import DishUpdate
from app.schemas.order_item import OrderItemCreate

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(tags=["pages"])


class CartItemIn(BaseModel):
    dish_id: int
    quantity: int


class CheckoutData(BaseModel):
    items: List[CartItemIn]


def _get_current_worker(
    request: Request,
    db: Session,
) -> Optional["Worker"]:
    """
    Вспомогательная функция: получает текущего работника по cookie worker_id.
    """
    worker_id = request.cookies.get("worker_id")
    if not worker_id:
        return None
    try:
        wid = int(worker_id)
    except ValueError:
        return None
    return worker_crud.get_worker_by_id(db, wid)


def _get_current_user_id(request: Request) -> Optional[int]:
    """
    Получает id пользователя из cookie user_id.
    """
    raw = request.cookies.get("user_id")
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    registered: bool = False,
    db: Session = Depends(get_db),
):
    """
    Главная страница:
    - список блюд из БД
    - справа корзина (управляется на фронте через JS)
    - в шапке кнопка входа/регистрации
    """
    dishes = dish_crud.get_all_dishes(db)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "dishes": dishes,
            "registered": registered,
        },
    )


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """
    Простая страница/модальное окно логина.
    Само модальное окно подключается в base.html,
    а этот маршрут нужен на случай прямого перехода.
    """
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login/worker", response_class=HTMLResponse)
def worker_login(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Обработка логина работника (администратор, менеджер, курьер).
    Использует существующую логику проверки пароля в crud.worker.
    """
    worker = worker_crud.check_worker_password(db, login, password)
    if not worker:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Неверный логин или пароль",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # Перенаправляем в зависимости от роли
    if worker.role == WorkerRole.admin:
        response = RedirectResponse(
            url="/admin", status_code=status.HTTP_303_SEE_OTHER
        )
    if worker.role == WorkerRole.manager:
        response = RedirectResponse(
            url="/manager", status_code=status.HTTP_303_SEE_OTHER
        )
    if worker.role == WorkerRole.courier:
        response = RedirectResponse(
            url="/courier", status_code=status.HTTP_303_SEE_OTHER
        )
    else:
        # На всякий случай — дефолт
        response = RedirectResponse(
            url="/", status_code=status.HTTP_303_SEE_OTHER
        )

    # Сохраняем id работника в cookie для проверки прав
    response.set_cookie("worker_id", str(worker.id), httponly=True)
    return response


@router.post("/login/user", response_class=HTMLResponse)
def user_login(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Обработка логина обычного пользователя.
    """
    user = user_crud.check_user_password(db, login, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Неверный логин или пароль",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    response = RedirectResponse(
        url="/", status_code=status.HTTP_303_SEE_OTHER
    )
    # Сохраняем id пользователя в cookie (можно использовать при оформлении заказа)
    response.set_cookie("user_id", str(user.id), httponly=True)
    return response


@router.post("/register/user", response_class=HTMLResponse)
def user_register(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    phone_number: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Регистрация нового пользователя (клиента) через модальное окно.
    """
    # Проверяем уникальность логина и email
    if user_crud.get_user_by_login(db, login) or user_crud.get_user_by_email(db, email):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Пользователь с таким логином или email уже существует",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user_in = UserCreate(
        login=login,
        password=password,
        full_name=full_name,
        phone_number=phone_number,
        email=email,
    )
    user = user_crud.create_user(db, user_in)

    # После регистрации задаём cookie и перенаправляем на главное меню с уведомлением
    response = RedirectResponse(
        url="/?registered=true",
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.set_cookie("user_id", str(user.id), httponly=True)
    return response


@router.get("/user/{user_id}/orders", response_class=HTMLResponse)
def user_orders_page(
    user_id: int,
    request: Request,
    registered: bool = False,
    db: Session = Depends(get_db),
):
    """
    Страница заказов пользователя.
    """
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    orders = order_crud.get_orders_by_user(db, user_id)
    return templates.TemplateResponse(
        "user_orders.html",
        {
            "request": request,
            "user": user,
            "orders": orders,
            "registered": registered,
        },
    )


@router.get("/admin", response_class=HTMLResponse)
def admin_page(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Страница администратора:
    - управление меню (блюда)
    Доступна только для вошедшего работника с ролью admin.
    """
    current_worker = _get_current_worker(request, db)
    if not current_worker or current_worker.role != WorkerRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")
    dishes = dish_crud.get_all_dishes(db)
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "dishes": dishes,
        },
    )


@router.post("/admin/dish/{dish_id}/update", response_class=HTMLResponse)
def admin_update_dish(
    dish_id: int,
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    """
    Обновление блюда из интерфейса администратора.
    Доступно только для роли admin.
    """
    current_worker = _get_current_worker(request, db)
    if not current_worker or current_worker.role != WorkerRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")
    update = DishUpdate(
        name=name,
        price=price,
        description=description,
    )
    dish = dish_crud.update_dish(db, dish_id, update)
    if not dish:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")

    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/admin/dish/{dish_id}/delete", response_class=HTMLResponse)
def admin_delete_dish(
    dish_id: int,
    db: Session = Depends(get_db),
):
    """
    Удаление блюда из меню.
    Доступно только для роли admin.
    """
    current_worker = _get_current_worker(request, db)
    if not current_worker or current_worker.role != WorkerRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")
    success = dish_crud.delete_dish(db, dish_id)
    if not success:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")

    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/manager", response_class=HTMLResponse)
def manager_page(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Страница менеджера:
    - список заказов
    - список курьеров
    - возможность назначать заказы курьерам
    Доступна только для роли manager.
    """
    current_worker = _get_current_worker(request, db)
    if not current_worker or current_worker.role != WorkerRole.manager:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")
    orders = order_crud.get_all_orders(db)
    couriers = worker_crud.get_workers_by_role(db, WorkerRole.courier)
    return templates.TemplateResponse(
        "manager.html",
        {
            "request": request,
            "orders": orders,
            "couriers": couriers,
        },
    )


@router.post("/manager/assign", response_class=HTMLResponse)
def assign_courier_to_order(
    request: Request,
    order_id: int = Form(...),
    courier_id: int = Form(...),
    db: Session = Depends(get_db),
):
    """
    Менеджер назначает курьера на заказ.
    Обновляем поле worker_id у заказа.
    Доступно только для роли manager.
    """
    current_worker = _get_current_worker(request, db)
    if not current_worker or current_worker.role != WorkerRole.manager:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")
    update = OrderUpdate(worker_id=courier_id)
    order = order_crud.update_order(db, order_id, update)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    return RedirectResponse(url="/manager", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/courier", response_class=HTMLResponse)
def courier_page(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Страница курьера:
    - список назначенных ему заказов
    Доступна только для роли courier.
    """
    worker = _get_current_worker(request, db)
    if not worker or worker.role != WorkerRole.courier:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")

    assigned_orders = order_crud.get_orders_by_worker(db, worker.id)

    return templates.TemplateResponse(
        "courier.html",
        {
            "request": request,
            "courier": worker,
            "orders": assigned_orders,
        },
    )


@router.post("/checkout")
def checkout(
    data: CheckoutData,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Оформление заказа из корзины.
    Создаёт запись в orders и соответствующие строки в order_items.
    """
    user_id = _get_current_user_id(request)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Для оформления заказа нужно войти как пользователь",
        )

    if not data.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Корзина пуста")

    # Пересчитываем сумму заказа по данным из БД
    total = 0.0
    for item in data.items:
        dish = dish_crud.get_dish_by_id(db, item.dish_id)
        if not dish:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Блюдо с id={item.dish_id} не найдено",
            )
        total += dish.price * item.quantity

    # Создаём заказ
    order_in = OrderCreate(
        delivery_address="Адрес не указан",
        user_id=user_id,
        worker_id=None,
        total_amount=total,
    )
    order = order_crud.create_order(db, order_in)

    # Позиции заказа
    for item in data.items:
        order_item_in = OrderItemCreate(
            order_id=order.id,
            dish_id=item.dish_id,
            quantity=item.quantity,
        )
        order_item_crud.create_order_item(db, order_item_in)

    return {"order_id": order.id, "total_amount": total}



