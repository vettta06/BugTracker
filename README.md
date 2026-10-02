## DevBug

Приложение для управления багами. Позволяет создавать, изменять и удалять задачи, а также привязывать их к конкретным проектам и исполнителям.

## Локальный запуск

Требования: Python, PostgreSQL

```bash
# 1. Создание базы данных
psql -U postgres -c "CREATE DATABASE devbug;"

# 2. Установка зависимостей
cd backend
pip install -r requirements.txt

# 3. Создание .env
POSTGRES_DB=devbug
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/devbug

# 4. Применение миграций
alembic upgrade head

# 5. Заполнение тестовыми данными
python seed_db.py

# 6. Запуск бэкенда
uvicorn app.main:app --reload

# Документация api
http://localhost:8000/docs
```

## Запуск через Docker:

Требования: Docker, Docker Compose

```bash
# 1. Создание .env
POSTGRES_DB=devbug
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/devbug

# 2. Сборка и запуск контейнеров
docker compose up -d --build

# prod-запуск
docker compose -f docker-compose.yml up -d --build

# 3. Применение миграций внутри контейнера
docker compose exec backend alembic upgrade head

# 4. Заполнение тестовыми данными
docker compose exec backend python seed_db.py

http://localhost
```

Скрипт **seed_db.py** необходим для начальной инициализации базы данных. Он создает тестовых пользователей и проекты, так как текущая версия пользовательского интерфейса не содержит отдельных форм для их создания.

## Структура проекта

```
devbug/
├── backend/
│ ├── app/
│ │ ├── main.py # Точка входа FastAPI
│ │ ├── database.py # Настройка SQLAlchemy
│ │ ├── models.py # Модели данных
│ │ ├── schemas.py # Pydantic-схемы для валидации
│ │ └── routers/ # API-эндпоинты
│ │ ├── projects.py
│ │ ├── users.py
│ │ ├── bugs.py
│ │ └── comments.py
│ ├── alembic/ # Миграции базы данных
│ ├── alembic.ini
│ ├── seed_db.py # Скрипт заполнения БД
│ ├── Dockerfile
│ └── requirements.txt
├── frontend/
│ ├── index.html
│ ├── app.js
│ ├── nginx.conf
│ └── style.css
├── docker-compose.yml
├── .gitignore
├── 12facotors.md - файл с описанием соответствия приложения 12 факторам
└── .env
```

Стек: FastAPI, HTML + JS + CSS, Alembic, Docker
