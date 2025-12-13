from typing import Optional, List

from fastapi import APIRouter, Depends, Request, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta
import traceback

from app.dependencies import get_db, get_current_user_from_cookie
from app.crud import dish as dish_crud
from app.crud import user as user_crud
from app.crud import order as order_crud
from app.crud import order_item as order_item_crud
from app.crud import ingredient as ingredient_crud
from app.models.dish import Dish
from app.models.dish_in_menu import DishInMenu
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.order import OrderUpdate, OrderCreate
from app.schemas.dish import DishUpdate, DishCreate
from app.schemas.order_item import OrderItemCreate
from app.core.security import create_access_token, verify_password
from app.models.order import OrderStatus

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(tags=["pages"])


class CartItemIn(BaseModel):
    dish_id: int
    quantity: int


class CheckoutData(BaseModel):
    items: List[CartItemIn]
    delivery_address: Optional[str] = None


def _get_current_user(
    request: Request,
    db: Session,
) -> Optional[User]:
    """Получает текущего пользователя из JWT токена в cookie."""
    from app.dependencies import get_current_user_from_cookie
    # Создаем временную зависимость для получения пользователя
    token = request.cookies.get("access_token")
    if not token:
        return None
    from app.core.security import decode_access_token
    payload = decode_access_token(token)
    if payload is None:
        return None
    user_id: int = payload.get("sub")
    if user_id is None:
        return None
    return user_crud.get_user_by_id(db, user_id)


def _get_current_user_id(request: Request) -> Optional[int]:
    """Получает id пользователя из JWT токена."""
    user = get_current_user_from_cookie(request, None)
    if user:
        return user.id
    return None


@router.get("/", response_class=HTMLResponse)
def index(
        request: Request,
        registered: bool = False,
        db: Session = Depends(get_db),
):
    """Главная страница с меню."""
    try:
        from sqlalchemy import func

        # Подзапрос для получения последней/актуальной записи в меню для каждого блюда
        subquery = (
            db.query(
                DishInMenu.dish_id,
                func.max(DishInMenu.id).label('latest_menu_id')
            )
            .group_by(DishInMenu.dish_id)
            .subquery()
        )

        # Получаем блюда с их текущими ценами из меню
        dishes_with_prices = (
            db.query(Dish, DishInMenu.price)
            .join(DishInMenu, Dish.id == DishInMenu.dish_id)
            .join(subquery,
                  (DishInMenu.dish_id == subquery.c.dish_id) &
                  (DishInMenu.id == subquery.c.latest_menu_id))
            .all()
        )

        # Преобразуем в список словарей для шаблона
        dishes = []
        for dish_obj, price in dishes_with_prices:
            dish_dict = {
                'id': dish_obj.id,
                'name': dish_obj.name,
                'weight': dish_obj.weight,
                'calories': dish_obj.calories,
                'description': dish_obj.description,
                'price': price  # Добавляем цену из dishes_in_menu
            }
            dishes.append(dish_dict)

        current_user = _get_current_user(request, db)
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "dishes": dishes,
                "registered": registered,
                "current_user": current_user,
            },
        )
    except Exception as e:
        import traceback
        print(f"Ошибка на главной странице: {e}")
        print(traceback.format_exc())
        # Возвращаем страницу даже при ошибке
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "dishes": [],
                "registered": False,
                "current_user": None,
            },
        )


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Страница логина."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Единый вход для всех пользователей."""
    try:
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

        # Создаем JWT токен
        access_token = create_access_token(data={"sub": user.id})
        
        # Перенаправляем в зависимости от роли
        if user.role == UserRole.admin:
            url = "/account/admin"
        elif user.role == UserRole.manager:
            url = "/account/manager"
        elif user.role == UserRole.courier:
            url = "/account/courier"
        else:
            url = "/"
        
        response = RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie("access_token", access_token, httponly=True, max_age=60*60*24*7)  # 7 дней
        return response
    except Exception as e:
        import traceback
        print(f"Ошибка при входе: {e}")
        print(traceback.format_exc())
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Произошла ошибка при входе. Попробуйте позже.",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/register", response_class=HTMLResponse)
def register(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    phone_number: str = Form(...),
    email: str = Form(...),
    delivery_address: str = Form(None),
    db: Session = Depends(get_db),
):
    """Регистрация нового пользователя (по умолчанию клиент)."""
    try:
        # Валидация обязательных полей
        if not login or not password or not full_name or not phone_number or not email:
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Все обязательные поля должны быть заполнены",
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        # Проверяем уникальность логина и email
        existing_user = user_crud.get_user_by_login(db, login)
        if existing_user:
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Пользователь с таким логином уже существует",
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        existing_email = user_crud.get_user_by_email(db, email)
        if existing_email:
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Пользователь с таким email уже существует",
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        # Проверяем уникальность телефона
        existing_phone = user_crud.get_user_by_phone(db, phone_number)
        if existing_phone:
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Пользователь с таким номером телефона уже существует",
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user_in = UserCreate(
            login=login,
            password=password,
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            delivery_address=delivery_address if delivery_address else None,
        )
        user = user_crud.create_user(db, user_in)

        # Создаем JWT токен
        access_token = create_access_token(data={"sub": user.id})
        
        response = RedirectResponse(
            url="/?registered=true",
            status_code=status.HTTP_303_SEE_OTHER,
        )
        response.set_cookie("access_token", access_token, httponly=True, max_age=60*60*24*7)
        return response
    except Exception as e:
        # Логируем ошибку для отладки
        print(f"Ошибка при регистрации: {e}")
        print(traceback.format_exc())
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": f"Ошибка при регистрации: {str(e)}",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/logout", response_class=HTMLResponse)
def logout():
    """Выход из системы."""
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response


@router.get("/account/admin", response_class=HTMLResponse)
def admin_account(
    request: Request,
    db: Session = Depends(get_db),
):
    """Личный кабинет администратора."""
    try:
        current_user = _get_current_user(request, db)
        if not current_user:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        if current_user.role != UserRole.admin:
            return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        
        dishes = dish_crud.get_all_dishes(db)
        users = user_crud.get_all_users(db)
        orders = order_crud.get_all_orders(db)
        try:
            ingredients = ingredient_crud.get_all_ingredients(db)
        except:
            ingredients = []
        
        return templates.TemplateResponse(
            "account_admin.html",
            {
                "request": request,
                "current_user": current_user,
                "dishes": dishes,
                "users": users,
                "orders": orders,
                "ingredients": ingredients,
            },
        )
    except Exception as e:
        import traceback
        print(f"Ошибка в личном кабинете администратора: {e}")
        print(traceback.format_exc())
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/account/manager", response_class=HTMLResponse)
def manager_account(
    request: Request,
    db: Session = Depends(get_db),
):
    """Личный кабинет менеджера."""
    try:
        current_user = _get_current_user(request, db)
        if not current_user:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        if current_user.role != UserRole.manager:
            return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        
        orders = order_crud.get_all_orders(db)
        couriers = user_crud.get_users_by_role(db, UserRole.courier)
        
        return templates.TemplateResponse(
            "account_manager.html",
            {
                "request": request,
                "current_user": current_user,
                "orders": orders,
                "couriers": couriers,
            },
        )
    except Exception as e:
        import traceback
        print(f"Ошибка в личном кабинете менеджера: {e}")
        print(traceback.format_exc())
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/account/courier", response_class=HTMLResponse)
def courier_account(
    request: Request,
    db: Session = Depends(get_db),
):
    """Личный кабинет курьера."""
    try:
        current_user = _get_current_user(request, db)
        if not current_user:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        if current_user.role != UserRole.courier:
            return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        
        assigned_orders = order_crud.get_orders_by_courier(db, current_user.id)
        
        return templates.TemplateResponse(
            "account_courier.html",
            {
                "request": request,
                "current_user": current_user,
                "orders": assigned_orders,
            },
        )
    except Exception as e:
        import traceback
        print(f"Ошибка в личном кабинете курьера: {e}")
        print(traceback.format_exc())
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/account/client", response_class=HTMLResponse)
def client_account(
    request: Request,
    db: Session = Depends(get_db),
):
    """Личный кабинет клиента."""
    try:
        current_user = _get_current_user(request, db)
        if not current_user:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
        orders = order_crud.get_orders_by_user(db, current_user.id)
        
        return templates.TemplateResponse(
            "account_client.html",
            {
                "request": request,
                "current_user": current_user,
                "orders": orders,
            },
        )
    except Exception as e:
        import traceback
        print(f"Ошибка в личном кабинете клиента: {e}")
        print(traceback.format_exc())
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/account/{role}", response_class=HTMLResponse)
def account_by_role(
    role: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Перенаправление в личный кабинет по роли."""
    try:
        current_user = _get_current_user(request, db)
        if not current_user:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
        role_map = {
            "client": "/account/client",
            "manager": "/account/manager",
            "courier": "/account/courier",
            "admin": "/account/admin",
            # Обратная совместимость со старыми значениями
            "клиент": "/account/client",
            "менеджер": "/account/manager",
            "курьер": "/account/courier",
            "администратор": "/account/admin",
        }
        
        redirect_url = role_map.get(role, "/")
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        import traceback
        print(f"Ошибка при перенаправлении: {e}")
        print(traceback.format_exc())
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/manager/assign", response_class=HTMLResponse)
def assign_courier_to_order(
    request: Request,
    order_id: int = Form(...),
    courier_id: int = Form(...),
    db: Session = Depends(get_db),
):
    """Менеджер назначает курьера на заказ."""
    try:
        current_user = _get_current_user(request, db)
        if not current_user or current_user.role != UserRole.manager:
            return RedirectResponse(url="/account/manager", status_code=status.HTTP_303_SEE_OTHER)

        # Не даём назначать курьера на отменённые или завершённые заказы
        order = order_crud.get_order_by_id(db, order_id)
        if not order:
            return RedirectResponse(url="/account/manager?error=order_not_found", status_code=status.HTTP_303_SEE_OTHER)
        if order.status in (OrderStatus.cancelled, OrderStatus.completed):
            return RedirectResponse(url="/account/manager?error=order_closed", status_code=status.HTTP_303_SEE_OTHER)

        update = OrderUpdate(courier_id=courier_id)
        order = order_crud.update_order(db, order_id, update)
        if not order:
            return RedirectResponse(url="/account/manager?error=order_not_found", status_code=status.HTTP_303_SEE_OTHER)

        return RedirectResponse(url="/account/manager?success=assigned", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        import traceback
        print(f"Ошибка при назначении курьера: {e}")
        print(traceback.format_exc())
        return RedirectResponse(url="/account/manager?error=assignment_failed", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/manager/cancel/{order_id}", response_class=HTMLResponse)
def cancel_order(
    order_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Менеджер отменяет доставку."""
    try:
        current_user = _get_current_user(request, db)
        if not current_user or current_user.role != UserRole.manager:
            return RedirectResponse(url="/account/manager", status_code=status.HTTP_303_SEE_OTHER)
        
        update = OrderUpdate(status=OrderStatus.cancelled)
        order = order_crud.update_order(db, order_id, update)
        if not order:
            return RedirectResponse(url="/account/manager?error=order_not_found", status_code=status.HTTP_303_SEE_OTHER)
        
        return RedirectResponse(url="/account/manager?success=cancelled", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        import traceback
        print(f"Ошибка при отмене заказа: {e}")
        print(traceback.format_exc())
        return RedirectResponse(url="/account/manager?error=cancel_failed", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/courier/update-status/{order_id}", response_class=HTMLResponse)
def update_order_status(
    order_id: int,
    request: Request,
    new_status: str = Form(...),
    db: Session = Depends(get_db),
):
    """Курьер изменяет статус заказа."""
    try:
        current_user = _get_current_user(request, db)
        if not current_user or current_user.role != UserRole.courier:
            return RedirectResponse(url="/account/courier", status_code=status.HTTP_303_SEE_OTHER)
        
        try:
            status_enum = OrderStatus[new_status]
        except KeyError:
            return RedirectResponse(url="/account/courier?error=invalid_status", status_code=status.HTTP_303_SEE_OTHER)
        
        update = OrderUpdate(status=status_enum)
        order = order_crud.update_order(db, order_id, update)
        if not order:
            return RedirectResponse(url="/account/courier?error=order_not_found", status_code=status.HTTP_303_SEE_OTHER)
        
        return RedirectResponse(url="/account/courier?success=status_updated", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        import traceback
        print(f"Ошибка при обновлении статуса: {e}")
        print(traceback.format_exc())
        return RedirectResponse(url="/account/courier?error=update_failed", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/account/profile/update", response_class=JSONResponse)
def update_profile(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    delivery_address: str = Form(None),
    password: str = Form(None),
    db: Session = Depends(get_db),
):
    """Обновление профиля пользователя через AJAX."""
    try:
        current_user = _get_current_user(request, db)
        if not current_user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": "Требуется авторизация"}
            )
        
        user_update = UserUpdate(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            delivery_address=delivery_address if delivery_address else None,
            password=password if password else None,
        )
        
        updated_user = user_crud.update_user(db, current_user.id, user_update)
        if not updated_user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "message": "Пользователь не найден"}
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": True, "message": "Профиль успешно обновлен"}
        )
    except Exception as e:
        import traceback
        print(f"Ошибка при обновлении профиля: {e}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": f"Ошибка: {str(e)}"}
        )


@router.post("/checkout")
def checkout(
    data: CheckoutData,
    request: Request,
    db: Session = Depends(get_db),
):
    """Оформление заказа из корзины."""
    try:
        current_user = _get_current_user(request, db)
        if not current_user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Для оформления заказа нужно войти"}
            )

        if not data.items:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Корзина пуста"}
            )

        # Проверяем адрес доставки
        delivery_address = data.delivery_address
        if not delivery_address:
            # Используем адрес из профиля, если он есть
            if current_user.delivery_address:
                delivery_address = current_user.delivery_address
            else:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Необходимо указать адрес доставки"}
                )

        # Пересчитываем сумму заказа по данным из БД
        total = 0.0
        for item in data.items:
            dish = dish_crud.get_dish_by_id(db, item.dish_id)
            if not dish:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": f"Блюдо с id={item.dish_id} не найдено"}
                )
            total += dish.price * item.quantity

        # Создаём заказ
        order_in = OrderCreate(
            delivery_address=delivery_address,
            user_id=current_user.id,
            courier_id=None,
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
    except Exception as e:
        import traceback
        print(f"Ошибка при оформлении заказа: {e}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Произошла ошибка при оформлении заказа"}
        )
