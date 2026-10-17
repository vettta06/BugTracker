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

# Вариант 2 - по частям

kubectl apply -f k8s/namespace.yml

# ConfigMaps
kubectl apply -f k8s/postgres-configmap.yml
kubectl apply -f k8s/frontend-nginx-configmap.yml

kubectl apply -f k8s/postgres-secret.yml
kubectl apply -f k8s/postgres-pvc.yml
kubectl apply -f k8s/postgres-deployment.yml
kubectl apply -f k8s/postgres-service.yml

# Миграции и seed — после готовности БД
kubectl apply -f k8s/backend-init-job.yml
kubectl wait --for=condition=complete job/backend-init -n devbug --timeout=180s

# Backend и Frontend
kubectl apply -f k8s/backend-deployment.yml
kubectl apply -f k8s/backend-service.yml
kubectl apply -f k8s/frontend-deployment.yml
kubectl apply -f k8s/frontend-service.yml

# Observability: Victoria Logs + Vector + Grafana
kubectl apply -f k8s/victorialogs-pvc.yml
kubectl apply -f k8s/victorialogs-deployment.yml
kubectl apply -f k8s/victorialogs-service.yml
kubectl apply -f k8s/vector-rbac.yml
kubectl apply -f k8s/vector-configmap.yml
kubectl apply -f k8s/vector-daemonset.yml
kubectl apply -f k8s/grafana-secret.yml
kubectl apply -f k8s/grafana-pvc.yml
kubectl apply -f k8s/grafana-deployment.yml
kubectl apply -f k8s/grafana-service.yml

# 4. Проверить работу
kubectl get all -n devbug

# 5. Открыть приложение
minikube service frontend -n devbug

# 6. Открыть Grafana
minikube service grafana -n devbug

# 7. Открыть vmui (Victoria Logs UI)
kubectl port-forward -n devbug svc/victorialogs 9428:9428
```

Скрипт **seed_db.py** необходим для начальной инициализации базы данных. Он создает тестовых пользователей и проекты, так как текущая версия пользовательского интерфейса не содержит отдельных форм для их создания.

## Observability

Для сбора, хранения и визуализации логов используется стек:

- **Backend** пишет структурированные JSON-логи через `structlog`.
- **Vector** (DaemonSet) собирает логи из `/var/log/pods/` и отправляет в Victoria Logs.
- **Victoria Logs** хранит логи (retention 7 дней) и предоставляет UI `vmui` с LogsQL.
- **Grafana** визуализирует логи через официальный плагин `victoriametrics-logs-datasource`.

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
├── k8s/                              # Манифесты Kubernetes
│   ├── kustomization.yml             # Сборка всех манифестов
│   ├── namespace.yml                 # Namespace devbug
│   ├── postgres-configmap.yml        # ConfigMap с несекретными параметрами БД
│   ├── frontend-nginx-configmap.yml  # ConfigMap с nginx.conf
│   ├── postgres-secret.yml           # Secret с параметрами БД
│   ├── postgres-pvc.yml              # PVC для данных БД
│   ├── postgres-deployment.yml       # Deployment PostgreSQL
│   ├── postgres-service.yml          # ClusterIP-сервис для БД
│   ├── backend-init-job.yml          # Job: миграции + seed (initContainer'ы)
│   ├── backend-deployment.yml        # Deployment backend-части
│   ├── backend-service.yml           # ClusterIP-сервис для backend
│   ├── frontend-deployment.yml       # Deployment frontend-части
│   ├── frontend-service.yml          # NodePort-сервис для frontend
│   ├── victorialogs-pvc.yml          # PVC для данных Victoria Logs
│   ├── victorialogs-deployment.yml   # Deployment Victoria Logs
│   ├── victorialogs-service.yml      # ClusterIP-сервис для Victoria Logs
│   ├── vector-rbac.yml               # ServiceAccount, ClusterRole, ClusterRoleBinding для Vector
│   ├── vector-configmap.yml          # ConfigMap с vector.toml
│   ├── vector-daemonset.yml          # DaemonSet Vector для сбора логов
│   ├── grafana-secret.yml            # Secret с admin-паролем Grafana
│   ├── grafana-pvc.yml               # PVC для данных Grafana
│   ├── grafana-deployment.yml        # Deployment Grafana + плагин VictoriaLogs
│   └── grafana-service.yml           # NodePort-сервис для Grafana
├── docker-compose.yml
├── .gitignore
├── 12factors.md - файл с описанием соответствия приложения 12 факторам
├── Report.md - файл с описанием манифестов и работы k8s
└── .env
```

Стек: FastAPI, HTML + JS + CSS, Alembic, Docker, minikube, Victoria Logs, Vector, Grafana
