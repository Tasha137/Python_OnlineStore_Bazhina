# Python_OnlineStore_Bazhina
Проект: Сайт интернет-магазина
Имя Фамилия — Наталья Бажина
логин на GitHub — Tasha137
e-mail — tasha137@mail.ru

# Онлайн-магазин

Веб-приложение интернет-магазина на Django с корзиной, оформлением заказов, авторизацией пользователей и административной панелью.

## Возможности

- Просмотр каталога товаров.
- Добавление товаров в корзину.
- Оформление заказа.
- Регистрация и вход пользователей.
- Личный кабинет пользователя.
- Административная панель для управления товарами и заказами.

## Технологии

- Python 3
- Django
- PostgreSQL
- HTML, CSS
- Docker
- Docker Compose

## Запуск через Docker

### 1. Клонировать проект
```bash
git clone <URL_репозитория>
cd <папка_проекта>
```

### 2. Проверить файлы Docker
Убедитесь, что в проекте есть:
- `Dockerfile`
- `docker-compose.yml`
- `requirements.txt`

### 3. Собрать и запустить контейнеры
```bash
docker compose up --build
```

Если используется старая версия Docker, можно:
```bash
docker-compose up --build
```

### 4. Выполнить миграции
В отдельном терминале:
```bash
docker compose exec web python manage.py migrate
```

### 5. Создать суперпользователя
```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Открыть проект
- Сайт: `http://localhost:8000/`
- Админка: `http://localhost:8000/admin/`

## Полезные команды

Остановить контейнеры:
```bash
docker compose down
```

Посмотреть логи:
```bash
docker compose logs -f
```