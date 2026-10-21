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

# 3. Установка мониторинга
helm repo add vm https://victoriametrics.github.io/helm-charts/

helm repo update

kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

helm install vm-single vm/victoria-metrics-single -n monitoring

helm install vmagent vm/victoria-metrics-agent -n monitoring --set remoteWrite[0].url=http://vm-single-victoria-metrics-single-server.monitoring.svc.cluster.local:8428/api/v1/write

# 4. Развёртывание приложения
kubectl apply -k k8s/

# 5. Проверка работы
kubectl get all -n devbug

# 6. Открыть приложение
minikube service frontend -n devbug

# 7. Открыть Grafana
minikube service grafana -n devbug

# 8. Открыть VictoriaLogs
kubectl port-forward -n devbug svc/victorialogs 9428:9428
```

Скрипт **seed_db.py** необходим для начальной инициализации базы данных. Он создает тестовых пользователей и проекты, так как текущая версия пользовательского интерфейса не содержит отдельных форм для их создания.

## Observability

Для мониторинга приложения используются VictoriaMetrics Single и vmagent, развёрнутые в Kubernetes через Helm. Для сбора логов используются VictoriaLogs и Vector, а для визуализации — Grafana.

### Бизнес-метрики

Приложение предоставляет следующие бизнес-метрики:

- `devbug_bugs_created_total` — количество созданных багов.
- `devbug_bugs_status_changed_total` — количество изменений статусов багов.
- `devbug_bugs_assigned_total` — количество назначений исполнителей.
- `devbug_projects_created_total` — количество созданных проектов.

FastAPI также предоставляет метрики HTTP-запросов через эндпоинт `/metrics`. Метрики PostgreSQL собираются с помощью `postgres_exporter`.

### Проверка состояния

Проверить состояние приложения:

```bash
kubectl get pods -n devbug
```

Проверить состояние компонентов мониторинга:

```bash
kubectl get pods -n monitoring
```

### Просмотр метрик

Для доступа к VictoriaMetrics выполните:

```bash
kubectl port-forward -n monitoring svc/vm-single-victoria-metrics-single-server 8428:8428
```

Откройте интерфейс VMUI:

```bash
http://localhost:8428/vmui/
```

В поле запроса укажите имя метрики, например:

```bash
devbug_bugs_assigned_total
```

Чтобы получить список имён всех доступных метрик, выполните в отдельном терминале:

```bash
curl -s 'http://localhost:8428/api/v1/label/__name__/values'
```

### Проверка сбора метрик

Для доступа к странице целей сбора vmagent выполните в отдельном терминале:

```bash
kubectl port-forward -n monitoring deployment/vmagent-victoria-metrics-agent 8429:8429
```

Откройте страницу:

```bash
http://localhost:8429/targets
```

В разделе `kubernetes-pods` отображаются обнаруженные цели сбора.

### Просмотр логов

Для доступа к VictoriaLogs выполните:

```bash
kubectl port-forward -n devbug svc/victorialogs 9428:9428
```

После этого откройте:

```bash
http://localhost:9428/
```

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
├── k8s/ # Манифесты Kubernetes
│ ├── kustomization.yml # Сборка всех манифестов
│ ├── namespace.yml # Namespace devbug
│ ├── postgres-configmap.yml # ConfigMap с несекретными параметрами БД
│ ├── frontend-nginx-configmap.yml # ConfigMap с nginx.conf
│ ├── postgres-secret.yml # Secret с параметрами БД
│ ├── postgres-pvc.yml # PVC для данных БД
│ ├── postgres-deployment.yml # Deployment PostgreSQL
│ ├── postgres-service.yml # ClusterIP-сервис для БД
│ ├── backend-init-job.yml # Job: миграции + seed (initContainer'ы)
│ ├── backend-deployment.yml # Deployment backend-части
│ ├── backend-service.yml # ClusterIP-сервис для backend
│ ├── frontend-deployment.yml # Deployment frontend-части
│ ├── frontend-service.yml # NodePort-сервис для frontend
│ ├── victorialogs-pvc.yml # PVC для данных Victoria Logs
│ ├── victorialogs-deployment.yml # Deployment Victoria Logs
│ ├── victorialogs-service.yml # ClusterIP-сервис для Victoria Logs
│ ├── vector-rbac.yml # ServiceAccount, ClusterRole, ClusterRoleBinding для Vector
│ ├── vector-configmap.yml # ConfigMap с vector.toml
│ ├── vector-daemonset.yml # DaemonSet Vector для сбора логов
│ ├── grafana-secret.yml # Secret с admin-паролем Grafana
│ ├── grafana-pvc.yml # PVC для данных Grafana
│ ├── grafana-deployment.yml # Deployment Grafana + плагин VictoriaLogs
│ └── grafana-service.yml # NodePort-сервис для Grafana
├── docker-compose.yml
├── .gitignore
├── 12factors.md - файл с описанием соответствия приложения 12 факторам
├── Report.md - файл с описанием манифестов и работы k8s
└── .env

```

**Стек:** FastAPI, HTML, CSS, JavaScript, PostgreSQL, SQLAlchemy, Alembic, Docker, Kubernetes, Minikube, VictoriaMetrics, vmagent, postgres_exporter, VictoriaLogs, Vector, Grafana.
