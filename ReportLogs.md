## Логирование

Перед выполнением практической работы в проект было доабвлено логирование при помощи structlog. настройки логирования находятся в backend/app/logger.py.
В логах не прописываются секретные данные, имена пользователей, содержание багов и комментариев. Используются только ID объектов.

## Настройка Victoria Logs

Для развёртывания Victoria Logs были использованы манифесты
`Deployment` + `Service` + `PVC`

| Файл                              | Назначение                                                                                         |
| --------------------------------- | -------------------------------------------------------------------------------------------------- |
| `k8s/victorialogs-pvc.yml`        | PVC на 2 GB для хранения логов на диске                                                            |
| `k8s/victorialogs-deployment.yml` | Deployment с одной репликой Victoria Logs. Монтирует PVC в `/victoria-logs-data`, retention 7 дней |
| `k8s/victorialogs-service.yml`    | ClusterIP-сервис на порту 9428                                                                     |

Lоставка логов настроена через DaemonSet. Выбор обусловлен тем, что:

- Vector читает логи локально с каждой ноды;
- При добавлении новой ноды vector автоматически запустится на ней;
- Используется один агент на ноду

| Файл                       | Назначение                                                                                                                               |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `k8s/vector-rbac.yml`      | ServiceAccount + ClusterRole + ClusterRoleBinding. Даёт Vector права читать `pods`, `namespaces`, `nodes` из Kubernetes API              |
| `k8s/vector-configmap.yml` | ConfigMap с `vector.toml`. Описывает source (`kubernetes_logs`), transform (парсинг JSON), sink (Elasticsearch Bulk API в Victoria Logs) |
| `k8s/vector-daemonset.yml` | DaemonSet Vector                                                                                                                         |

В `vector.toml` указаны заголовки `VL-Msg-Field=event`, `VL-Time-Field=timestamp`, `VL-Stream-Fields=service` для маппинга логов на `_msg`, `_time`, `_stream` в Victoria Logs.

## Выполнение запросов

### 1. Получение сырых записей за последние 30 минут

![alt text](image.png)

### 2. Фильтр по полю request_finished

![alt text](image-1.png)

### 3. Запрос с группировкой по уровню

![alt text](image-2.png)

### 4. Агрегирующий запрос

![alt text](image-3.png)
