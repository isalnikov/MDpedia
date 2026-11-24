---
name: sql-review-query
version: "1.0"
inputs: [sql_text, dialect, tables]
outputs: [rewritten_sql, recipe_ref, pitfalls]
tags: [sql, select, join, cte]
---

# PROMPT: ревью и переписывание SQL

Источник рецептов: `library/sql/sql-recipes-and-queries.md`.

## SQL

```sql
{{sql_text}}
```

## Диалект

{{dialect}}

## Таблицы / контекст

{{tables}}

## Инструкция

1. Классифицировать: join / aggregate / window / hierarchy / pivot.
2. Найти соответствующий рецепт в Cookbook / SQL в примерах (указать секцию гида).
3. Предложить subquery vs JOIN vs CTE по таблице из гида.
4. Отметить NULL, дубли при JOIN+aggregate, DISTINCT-подводные камни.