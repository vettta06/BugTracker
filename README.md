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
POSTGRES_PASSWORD=<password>
DATABASE_URL=postgresql://postgres:<password>@localhost:5432/devbug

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
POSTGRES_PASSWORD=<password>
DATABASE_URL=postgresql://postgres:<password>@db:5432/devbug

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

## Запуск в Kubernetes:

Требования: Docker, minikube, kubectl

```bash
# 1. Запуск кластера
minikube start --driver=docker --container-runtime=docker

# 2. Сборка образов внутри minikube
eval $(minikube docker-env)
docker build -t devbug-backend:latest ./backend
docker build -t devbug-frontend:latest ./frontend

# 3. Применение манифестов

# Вариант 1 -  одной командой
kubectl apply -k k8s/

# отедельно запустить job
kubectl apply -f k8s/backend-migration-job.yml
kubectl apply -f k8s/backend-seed-job.yml

# Вариант 2 - по частям

kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/postgres-secret.yml
kubectl apply -f k8s/postgres-pvc.yml
kubectl apply -f k8s/postgres-deployment.yml
kubectl apply -f k8s/postgres-service.yml

# Миграции и seed — после готовности БД
kubectl apply -f k8s/backend-migration-job.yml
kubectl wait --for=condition=complete job/backend-migration -n devbug --timeout=120s
kubectl apply -f k8s/backend-seed-job.yml
kubectl wait --for=condition=complete job/backend-seed -n devbug --timeout=120s

# Backend и Frontend
kubectl apply -f k8s/backend-deployment.yml
kubectl apply -f k8s/backend-service.yml
kubectl apply -f k8s/frontend-deployment.yml
kubectl apply -f k8s/frontend-service.yml

# 4. Проверить работу
kubectl get all -n devbug

# 5. Открыть приложение
minikube service frontend -n devbug
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
│ ├── style.css
│ └── Dockerfile
├── k8s/                         # Манифесты Kubernetes
│   ├── kustomization.yml        # Сборка всех манифестов
│   ├── namespace.yml            # Namespace devbug
│   ├── postgres-secret.yml      # Secret с параметрами БД
│   ├── postgres-pvc.yml         # PersistentVolumeClaim для данных БД
│   ├── postgres-deployment.yml  # Deployment PostgreSQL
│   ├── postgres-service.yml     # ClusterIP-сервис для БД
│   ├── backend-migration-job.yml # Job для миграций Alembic
│   ├── backend-seed-job.yml     # Job для seed_db.py
│   ├── backend-deployment.yml   # Deployment backend-части
│   ├── backend-service.yml      # ClusterIP-сервис для backend
│   ├── frontend-deployment.yml  # Deployment frontend-части
│   └── frontend-service.yml     # NodePort-сервис для frontend
├── docker-compose.yml
├── .gitignore
├── 12factors.md - файл с описанием соответствия приложения 12 факторам
├── Report.md - файл с описанием манифестов и работы k8s
└── .env
```

Стек: FastAPI, HTML + JS + CSS, Alembic, Docker, minikube
