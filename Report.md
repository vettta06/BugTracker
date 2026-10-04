# Использованные абстракции

| Абстракция            | Имя в проекте       | Назначение                      |
| --------------------- | ------------------- | ------------------------------- |
| Namespace             | `devbug`            | Изоляция ресурсов приложения    |
| Secret                | `postgres-secret`   | Хранение учётных данных БД      |
| PersistentVolumeClaim | `postgres-pvc`      | Хранение данных PostgreSQL      |
| Deployment            | `postgres`          | Под PostgreSQL                  |
| Deployment            | `backend`           | Поды FastAPI-части              |
| Deployment            | `frontend`          | Под Frontend-части              |
| Service               | `db`                | Внутренний доступ к базе данных |
| Service               | `backend`           | Внутренний доступ к backend     |
| Service               | `frontend`          | Внешний доступ к приложению     |
| Job                   | `backend-migration` | Применение миграций Alembic     |
| Job                   | `backend-seed`      | Заполнение бд тестовыми данными |
| Kustomization         | `k8s/`              | Сборка всех манифестов          |

# Взаимодействие между сервисами

| Источник           | Получатель              | Способ общения | Порт      |
| ------------------ | ----------------------- | -------------- | --------- |
| Браузер            | Service `frontend`      | NodePort       | 80 → 8080 |
| Service `frontend` | Pod `frontend`          | ClusterIP      | 8080      |
| Nginx (frontend)   | Service `backend`       | `proxy_pass`   | 8000      |
| Service `backend`  | Pod `backend` (uvicorn) | ClusterIP      | 8000      |
| Backend            | Service `db`            | `DATABASE_URL` | 5432      |
| Service `db`       | Pod `postgres`          | ClusterIP      | 5432      |
| Pod `postgres`     | PVC `postgres-pvc`      | `volumeMount`  | —         |
