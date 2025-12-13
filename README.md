# Restaurant_delivery

<h3>database (данные у разных пользователей могут отличаться)</h3>
- host: localhost
- port: 5432
- name: food_delivery_db
- login: postgres
- password: 1234

## Гайд по alembic
- ```bash
    alembic revision --autogenerate # создать новую версию бд, которую хотим загрузить в реальную бд
  ```
- ```bash
    alembic upgrade head # загрузить новую версию в рельную бд
  ```
  
### Если надо удалить бд и подключить все с нуля через alembic
- Удаляешь бд (например через pgAdmin)
- Удаляешь все содержимое папки alembic/versions
- ```bash
    alembic downgrade base
    alembic revision --autogenerate -m "Comment"
    alembic upgrade head
    ```

## Гайд по коммитам на гит
- ```bash
    git add . # сохранить все изменения для дальнейшего
  ```
- ```bash
    git commit -m "КОММЕНТАРИЙ" # создать коммит (комментарий ОБЯЗАТЕЛЕН)
  ```