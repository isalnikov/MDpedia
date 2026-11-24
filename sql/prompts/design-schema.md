---
name: sql-design-schema
version: "1.0"
inputs: [domain_description, access_patterns, volume]
outputs: [ddl_sketch, index_plan, normalization_notes]
tags: [sql, ddl, schema]
---

# PROMPT: проектирование схемы SQL

Перед ответом прочитай `library/sql/sql-fundamentals.md` и релевантные разделы `library/sql/mysql-performance-patterns.md` (Ch 4 schema).

## Задача

{{domain_description}}

## Паттерны доступа

{{access_patterns}}

## Объём / рост

{{volume}}

## Инструкция агенту

1. Нормализация vs summary/counter tables — обосновать по книгам (см. гиды).
2. Типы колонок, PK, InnoDB.
3. Индексы под перечисленные запросы — не «на будущее».
4. Ссылка на `library/sql/INDEX.md` и `system-design-patterns` при границах сервиса.