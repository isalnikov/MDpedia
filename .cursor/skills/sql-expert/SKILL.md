---
name: sql-expert
description: >-
  Designs SQL schemas, queries, transactions, and MySQL operations using the
  local SQL library (fundamentals, recipes, performance, HA). Use when writing
  SQL, optimizing queries, EXPLAIN, indexing, isolation levels, replication,
  failover, backups, or MySQL tuning. Pair with system-design-patterns and
  spring-boot-expert for application boundaries.
---

# SQL / MySQL — эксперт «когда что использовать»

**Источник истины:** `sql/books-md/*.md` (полнотекст).  
**Сжатые гиды:** `library/sql/` — читай **первым**.

| Задача | Файл |
|--------|------|
| Типы, ER, DDL vs DML | `library/sql/sql-fundamentals.md` |
| JOIN, CTE, window, pivot | `library/sql/sql-recipes-and-queries.md` |
| Индексы, EXPLAIN, replication scale | `library/sql/mysql-performance-patterns.md` |
| ACID, isolation, 2PC, HA, backup | `library/sql/sql-transactions-and-ha.md` |

Промпты MDpedia: `sql/prompts/`. Корпус: `corpus/AGENT-INDEX.md`, граф: `mdpedia/graph/links.json`.

---

## Процесс

### 1. Классификация запроса
- Проектирование схемы vs разовый отчёт vs OLTP hot path vs batch vs HA/incident.

### 2. Fundamentals
- Нормализация vs денормализация (сверка с DDIA + `mysql-performance-patterns` counter/summary tables).
- InnoDB по умолчанию; явный engine только с обоснованием.

### 3. Написание SQL
- Предпочитай JOIN над correlated subquery для больших наборов; CTE для читаемости и рекурсии.
- `EXISTS` / anti-join для проверки наличия; window для ранжирования без self-join.

### 4. Performance
- Индекс под **реальный** WHERE/ORDER BY; covering index; не индексировать «на всякий случай».
- `EXPLAIN` → `type`, `key`, `rows`, `Extra`; full scan на больших таблицах — план исправления.
- Репликация **не** масштабирует запись; read replicas + кэш приложения.

### 5. Transactions & HA
- Уровень изоляции под аномалии (не SERIALIZABLE без нужды).
- Failover: split-brain, binlog position, не путать репликацию с бэкапом.
- Distributed: избегать 2PC через гетерогенные БД; outbox/saga — см. `system-design-patterns`.

### 6. Spring / JDBC
- Транзакции на сервисе (`spring-boot-expert`); миграции Flyway/Liquibase; пулы HikariCP.

## Формат ответа

```markdown
## Контекст
## Рекомендация (SQL / схема / ops)
## Отвергнутые варианты
## Риски (deadlock, replication lag, …)
## Ссылки на library/sql/…
```

## Анти-паттерны
- `SELECT *` в hot path; N+1 без batch/join.
- Реплика для записи; dual master без conflict strategy.
- Бэкап только через реплику без проверенного restore.
- Query Cache как решение (устарело в MySQL 8).

Шпаргалка: `reference.md`.