---
name: sql-optimize-mysql
version: "1.0"
inputs: [explain_output, slow_query, mysql_version]
outputs: [action_plan, index_changes, config_hints]
tags: [mysql, performance, explain]
---

# PROMPT: оптимизация MySQL

Источник: `library/sql/mysql-performance-patterns.md`. Проверка HA: `library/sql/sql-transactions-and-ha.md` если задействована реплика.

## Версия MySQL

{{mysql_version}}

## Запрос

```sql
{{slow_query}}
```

## EXPLAIN / профиль

```
{{explain_output}}
```

## Инструкция

1. Ответ time = f(CPU/IO/lock/wait) — не угадывать без метрик (HPM Ch 3).
2. EXPLAIN: type, key, rows, Extra → конкретные шаги (индекс, переписать JOIN, covering).
3. Реплика/кэш только если сценарий read-heavy; запись не масштабировать репликами.
4. Query Cache не предлагать для MySQL 8+.