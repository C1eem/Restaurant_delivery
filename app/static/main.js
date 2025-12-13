// Логика для модальных окон логина и деталей блюда, а также корзины

document.addEventListener("DOMContentLoaded", () => {
    setupLoginModal();
    setupDishDetailsModal();
    setupCart();
});

function setupLoginModal() {
    const loginButton = document.getElementById("loginButton");
    const loginModal = document.getElementById("loginModal");
    const closeLoginModal = document.getElementById("closeLoginModal");

    if (!loginButton || !loginModal || !closeLoginModal) {
        return;
    }

    loginButton.addEventListener("click", () => {
        loginModal.classList.remove("hidden");
    });

    closeLoginModal.addEventListener("click", () => {
        loginModal.classList.add("hidden");
    });

    loginModal.addEventListener("click", (e) => {
        if (e.target === loginModal) {
            loginModal.classList.add("hidden");
        }
    });

    // Переключение вкладок
    const tabButtons = document.querySelectorAll(".tab-button");
    const tabs = document.querySelectorAll(".tab");

    tabButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            const tab = btn.dataset.tab;
            tabButtons.forEach((b) => b.classList.remove("active"));
            tabs.forEach((t) => t.classList.remove("active"));

            btn.classList.add("active");
            const activeTab = document.getElementById(tab + "Tab");
            if (activeTab) activeTab.classList.add("active");
        });
    });

    // Валидация формы регистрации
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", (e) => {
            const requiredFields = registerForm.querySelectorAll("[required]");
            let isValid = true;
            
            requiredFields.forEach((field) => {
                if (!field.value || field.value.trim() === "") {
                    isValid = false;
                    field.style.borderColor = "red";
                } else {
                    field.style.borderColor = "";
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert("Пожалуйста, заполните все обязательные поля!");
            }
        });
    }
}

function setupDishDetailsModal() {
    const dishModal = document.getElementById("dishModal");
    const closeDishModal = document.getElementById("closeDishModal");
    const dishModalTitle = document.getElementById("dishModalTitle");
    const dishModalDescription = document.getElementById("dishModalDescription");
    const dishModalPrice = document.getElementById("dishModalPrice");
    const dishModalWeight = document.getElementById("dishModalWeight");
    const dishModalCalories = document.getElementById("dishModalCalories");
    const dishModalAddToCart = document.getElementById("dishModalAddToCart");

    if (!dishModal || !closeDishModal) return;

    let currentDishData = null;

    document.querySelectorAll(".view-details").forEach((btn) => {
        btn.addEventListener("click", () => {
            const card = btn.closest(".card");
            if (!card) return;
            currentDishData = extractDishData(card);

            dishModalTitle.textContent = currentDishData.name;
            dishModalDescription.textContent =
                currentDishData.description || "Описание не указано.";
            dishModalPrice.textContent = currentDishData.price.toFixed(2);
            dishModalWeight.textContent = currentDishData.weight;
            dishModalCalories.textContent = currentDishData.calories;

            dishModal.classList.remove("hidden");
        });
    });

    closeDishModal.addEventListener("click", () => {
        dishModal.classList.add("hidden");
    });

    dishModal.addEventListener("click", (e) => {
        if (e.target === dishModal) {
            dishModal.classList.add("hidden");
        }
    });

    if (dishModalAddToCart) {
        dishModalAddToCart.addEventListener("click", () => {
            if (currentDishData) {
                addToCart(currentDishData);
                dishModal.classList.add("hidden");
            }
        });
    }
}

let cart = [];

function setupCart() {
    const checkoutButton = document.getElementById("checkoutButton");

    document.querySelectorAll(".add-to-cart").forEach((btn) => {
        btn.addEventListener("click", () => {
            const card = btn.closest(".card");
            if (!card) return;
            const data = extractDishData(card);
            addToCart(data);
        });
    });

    if (checkoutButton) {
        checkoutButton.addEventListener("click", async () => {
            if (!cart.length) return;

            // Проверяем адрес доставки
            let deliveryAddress = null;
            const userAddress = document.getElementById("userDeliveryAddress");
            if (userAddress && userAddress.value) {
                deliveryAddress = userAddress.value;
            } else {
                // Запрашиваем адрес у пользователя
                deliveryAddress = prompt("Укажите адрес доставки:");
                if (!deliveryAddress || deliveryAddress.trim() === "") {
                    alert("Адрес доставки обязателен для оформления заказа!");
                    return;
                }
            }

            const payload = {
                items: cart.map((item) => ({
                    dish_id: item.id,
                    quantity: item.quantity,
                })),
                delivery_address: deliveryAddress,
            };

            try {
                const res = await fetch("/checkout", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(payload),
                });

                if (res.status === 401) {
                    alert("Чтобы оформить заказ, войдите в систему.");
                    return;
                }

                if (res.status === 400) {
                    const errorData = await res.json();
                    alert(errorData.detail || "Не удалось оформить заказ. Проверьте данные.");
                    return;
                }

                if (!res.ok) {
                    alert("Не удалось оформить заказ. Попробуйте ещё раз.");
                    return;
                }

                const data = await res.json();
                alert(`Заказ №${data.order_id} оформлен на сумму ${data.total_amount.toFixed(2)} ₽`);

                // Очищаем корзину
                cart = [];
                updateCartUI();
            } catch (e) {
                console.error(e);
                alert("Произошла ошибка при оформлении заказа.");
            }
        });
    }

    updateCartUI();
}

function extractDishData(card) {
    return {
        id: parseInt(card.dataset.dishId, 10),
        name: card.dataset.dishName,
        price: parseFloat(card.dataset.dishPrice),
        weight: parseFloat(card.dataset.dishWeight),
        calories: parseFloat(card.dataset.dishCalories),
        description: card.dataset.dishDescription || "",
    };
}

function addToCart(dish) {
    const existing = cart.find((item) => item.id === dish.id);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({ ...dish, quantity: 1 });
    }
    updateCartUI();
}

function updateCartUI() {
    const cartItems = document.getElementById("cartItems");
    const cartTotal = document.getElementById("cartTotal");
    const checkoutButton = document.getElementById("checkoutButton");

    if (!cartItems || !cartTotal || !checkoutButton) return;

    cartItems.innerHTML = "";

    if (cart.length === 0) {
        const p = document.createElement("p");
        p.className = "muted";
        p.textContent = "Корзина пуста. Добавьте блюда из меню.";
        cartItems.appendChild(p);
        cartTotal.textContent = "0.00";
        checkoutButton.disabled = true;
        return;
    }

    let total = 0;

    cart.forEach((item) => {
        total += item.price * item.quantity;
        const row = document.createElement("div");
        row.className = "cart-item";
        row.innerHTML = `
            <div>
                <div>${item.name}</div>
                <div class="muted small">${item.price.toFixed(2)} ₽ × ${item.quantity}</div>
            </div>
            <div>
                <button class="btn btn-small btn-secondary cart-minus" data-id="${item.id}">−</button>
                <button class="btn btn-small btn-secondary cart-plus" data-id="${item.id}">+</button>
            </div>
        `;
        cartItems.appendChild(row);
    });

    // Уменьшить количество
    cartItems.querySelectorAll("button.cart-minus").forEach((btn) => {
        btn.addEventListener("click", () => {
            const id = parseInt(btn.dataset.id, 10);
            const idx = cart.findIndex((i) => i.id === id);
            if (idx !== -1) {
                if (cart[idx].quantity > 1) {
                    cart[idx].quantity -= 1;
                } else {
                    cart.splice(idx, 1);
                }
                updateCartUI();
            }
        });
    });

    // Увеличить количество
    cartItems.querySelectorAll("button.cart-plus").forEach((btn) => {
        btn.addEventListener("click", () => {
            const id = parseInt(btn.dataset.id, 10);
            const item = cart.find((i) => i.id === id);
            if (item) {
                item.quantity += 1;
                updateCartUI();
            }
        });
    });

    cartTotal.textContent = total.toFixed(2);
    checkoutButton.disabled = false;
}


