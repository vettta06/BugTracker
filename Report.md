# Использованные абстракции

| Абстракция            | Имя в проекте           | Назначение                                                 |
| --------------------- | ----------------------- | ---------------------------------------------------------- |
| Namespace             | `devbug`                | Изоляция ресурсов приложения                               |
| ConfigMap             | `postgres-config`       | Несекретные параметры БД: имя БД, пользователь, хост, порт |
| ConfigMap             | `frontend-nginx-config` | Конфиг nginx для фронтенда                                 |
| Secret                | `postgres-secret`       | Пароль PostgreSQL                                          |
| PersistentVolumeClaim | `postgres-pvc`          | Хранение данных PostgreSQL                                 |
| Deployment            | `postgres`              | Под PostgreSQL                                             |
| Deployment            | `backend`               | Поды FastAPI-части                                         |
| Deployment            | `frontend`              | Под Frontend-части                                         |
| Service               | `db`                    | Внутренний доступ к базе данных                            |
| Service               | `backend`               | Внутренний доступ к backend                                |
| Service               | `frontend`              | Внешний доступ к приложению                                |
| Job                   | `backend-init`          | Миграции (initContainer) + seed (основной контейнер)       |
| Kustomization         | `k8s/`                  | Сборка всех манифестов                                     |

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
