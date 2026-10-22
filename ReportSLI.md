## 1. Выбранные метрики (SLI)

Были выбраны 3 основных SLI и 1 supporting SLI. Бизнес-метрики (`devbug_*`) в качестве SLI **не используются**.

### 1.1. Таблица SLI

| #                  | SLI               | Тип   | Метрика-источник                       | Лейблы                                                     | SLO (30d) | SLA     |
| ------------------ | ----------------- | ----- | -------------------------------------- | ---------------------------------------------------------- | --------- | ------- |
| SLI-1              | HTTP availability | RBSLO | `http_requests_total`                  | `namespace="devbug"`, `pod=~"backend-.*"`, `status!~"5.."` | ≥ 99.5%   | ≥ 99.0% |
| SLI-2              | HTTP latency      | RBSLO | `http_request_duration_seconds_bucket` | `le="0.5"`, `namespace="devbug"`, `pod=~"backend-.*"`      | ≥ 99.0%   | ≥ 98.0% |
| SLI-3              | Backend uptime    | TBSLO | `up`                                   | `namespace="devbug"`, `pod=~"backend-.*"`                  | ≥ 99.9%   | ≥ 99.5% |
| SLI-4 (supporting) | DB availability   | TBSLO | `pg_up`                                | `namespace="devbug"`                                       | ≥ 99.9%   | ≥ 99.5% |

### 1.2. Обоснование выбора

**SLI-1 (HTTP availability, RBSLO).**
`http_requests_total` от `prometheus-fastapi-instrumentator` - счётчик всех HTTP-запросов
с лейблом `status`. Доля запросов **без 5xx** - показатель того, что пользователь
получил корректный ответ, а не ошибку сервера. Считаем «успешным» любой ответ **не 5xx**.

**SLI-2 (HTTP latency, RBSLO).**
`http_request_duration_seconds_bucket` - гистограмма латентности. Считаем **долю запросов
быстрее 500ms**.

**SLI-3 (Backend uptime, TBSLO).**
`up` - флаг от vmagent: `1`, если scrape `/metrics` успешен, `0` - если под недоступен.
Пишется независимо от трафика, поэтому ловит случай, когда под лежит и запросов нет.

**SLI-4 (DB availability, supporting).**
`pg_up` от `postgres_exporter`: увидим, если БД не работает. Supporting SLI -
не входит в основной SLA, но выводится на дашборд.

**Почему бизнес-метрики - не SLI.**
`devbug_bugs_created_total`, `devbug_bugs_status_changed_total`,
`devbug_bugs_assigned_total`, `devbug_projects_created_total` - это **количество
успешных бизнес-операций**. У них **нет парного счётчика ошибок** (например,
`devbug_bug_create_errors_total`), поэтому нельзя посчитать «долю успешных».
Они остаются на дашборде как дополнительные индикаторы, но SLO на них не строится.

---

## 2. SLI: формулировки и формулы расчёта

Окно расчёта: **30 дней rolling** (последние 30 дней, не сбрасывается 1-го числа).
Для демонстрации используются короткие окна.

### SLI-1. HTTP availability (RBSLO)

**Формулировка:** доля HTTP-запросов к backend, завершившихся без 5xx,
от общего числа запросов.

**Формула (5m):**

```promql
sum(rate(http_requests_total{namespace="devbug", pod=~"backend-.*", status!~"5.."}[5m]))
/
sum(rate(http_requests_total{namespace="devbug", pod=~"backend-.*"}[5m]))
```

**Формула (30d, для SLO-дашборда):**

```promql
sum(rate(http_requests_total{namespace="devbug", pod=~"backend-.*", status!~"5.."}[30d]))
/
sum(rate(http_requests_total{namespace="devbug", pod=~"backend-.*"}[30d]))
```

Результат - число 0..1.

### SLI-2. HTTP latency (RBSLO)

**Формулировка:** доля HTTP-запросов к backend, завершившихся быстрее 500ms,
от общего числа запросов.

**Формула (5m):**

```promql
sum(rate(http_request_duration_seconds_bucket{namespace="devbug", pod=~"backend-.*", le="0.5"}[5m]))
/
sum(rate(http_request_duration_seconds_count{namespace="devbug", pod=~"backend-.*"}[5m]))
```

### SLI-3. Backend uptime (TBSLO)

**Формулировка:** доля минут, в течение которых все поды backend были доступны
(`up == 1`), от общего числа минут.

**Формула (1m):**

```promql
avg_over_time(up{namespace="devbug", pod=~"backend-.*"}[1m])
```

**Формула (30d):**

```promql
avg_over_time(up{namespace="devbug", pod=~"backend-.*"}[30d])
```

### SLI-4. DB availability (TBSLO, supporting)

**Формулировка:** доля минут, в течение которых PostgreSQL был доступен (`pg_up == 1`).

**Формула (1m):**

```promql
avg_over_time(pg_up{namespace="devbug"}[1m])
```

---

## 3. SLO: формулировки и error budget

| SLO   | Формулировка                                      | Target (30d) | Error budget                           |
| ----- | ------------------------------------------------- | ------------ | -------------------------------------- |
| SLO-1 | 99.5% HTTP-запросов к backend завершаются без 5xx | 99.5%        | 0.5% × 30d - 3ч 36м «плохого» времени  |
| SLO-2 | 99% HTTP-запросов к backend быстрее 500ms         | 99.0%        | 1% запросов могут быть медленнее 500ms |
| SLO-3 | 99.9% минут все поды backend доступны (`up==1`)   | 99.9%        | 0.1% × 30d - 43м недоступности         |

**Почему такие значения:**

- **99.5% availability** - стандарт для внутренних сервисов. Даёт ~3.5 часа бюджета в месяц
- **99% latency < 500ms** - 500ms незаметны пользователю; 1% «медленных» запросов покрывает холодный старт, GC-паузы.
- **99.9% uptime** - строже availability, потому что лежащее приложение - это полный отказ, а не деградация.

**Error budget remaining**

```promql
1 - ((1 - <SLI_30d>) / (1 - <SLO_target>))
```

- `1.0` - бюджет целый (SLI = SLO или лучше);
- `0.0` - бюджет исчерпан (SLI = SLO ровно на границе);
- `< 0` - SLO нарушен (SLI хуже target).

---

## 4. SLA: формулировки

| SLA   | Обещание                        | Буфер относительно SLO |
| ----- | ------------------------------- | ---------------------- |
| SLA-1 | Доступность API ≥ 99.0% в месяц | −0.5% от SLO-1 (99.5%) |
| SLA-2 | 98% запросов быстрее 500ms      | −1.0% от SLO-2 (99%)   |
| SLA-3 | Uptime ≥ 99.5% в месяц          | −0.4% от SLO-3 (99.9%) |

**Общий SLA:**

> DevBug обязуется обеспечивать доступность API не ниже 99.0% в месяц, 98% запросов
> быстрее 500ms и uptime не ниже 99.5% в месяц.

---

## 5. Реализация пробера

Реализация: recording rules в VictoriaMetrics (`k8s/slo-recording-rules.yml`).

Список правил:

- `sli:http_availability:ratio_rate5m`
- `sli:http_latency_fast:ratio_rate5m`
- `sli:backend_uptime:ratio_rate1m`
- `slo:http_availability:ratio_30d`
- `slo:http_availability:error_budget_remaining`

---

## 6. Визуализация (Grafana)

Datasource VictoriaMetrics (provisioning) + SLO dashboard
(`k8s/grafana-datasource-configmap.yml`, `k8s/grafana-dashboard-slo-configmap.yml`).

Панели:

1. SLI-1 availability (5m) + threshold SLO.
2. SLI-2 latency fast ratio (5m) + threshold SLO.
3. SLI-3 uptime (1m) + threshold SLO.
4. Error budget remaining (30d).
5. SLO compliance (30d).
6. Supporting: `pg_up`, `devbug_*`.

---
