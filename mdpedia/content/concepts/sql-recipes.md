---
title: "SQL: рецепты и типовые запросы"
skill: ["sql", "queries"]
level: intermediate
source: "library/sql/sql-recipes-and-queries.md"
embeddings:
  chunk_strategy: headings
  max_tokens: 2048
relations:
  parent: corpus/AGENT-INDEX.md
---

# SQL: рецепты и типовые запросы

## Источник (полный текст)

`library/sql/sql-recipes-and-queries.md`

## Ядро для ИИ (Embedding Target)

> Дословный фрагмент из `library/sql/sql-recipes-and-queries.md` (первые 120 строк, не более 24000 символов).

---
source:
  - "Anthony Molinaro — SQL Cookbook (O'Reilly, 2006); sql/books-md/SQL-sbornik_retseptov_O_39_Reilly.md"
  - "Астахова, Толстобров, Мельников — SQL в примерах и задачах (2002); sql/books-md/sql в примерах.md"
note: "Recipe-style справочник: Задача → Решение → Когда / ловушки. Примеры — ANSI SQL с пометками по СУБД."
---

# SQL: рецепты и типовые запросы

Синтез **SQL Cookbook** (Молинаро: joins, window, pivot, иерархии, CTE, reporting) и **SQL в примерах** (база SELECT, агрегаты, подзапросы, JOIN, NULL, строки/даты).

Формат рецепта: **Problem** → **Solution** → **When** → **Pitfalls** → sketch SQL.

---

## Соединения (JOIN)

### Inner / equi-join по FK

**Problem.** Собрать строки из двух таблиц по общему ключу (имя + атрибуты родителя).

**Solution.** Эквисоединение: `INNER JOIN … ON left.fk = right.pk` (эквивалент старому `FROM a, b WHERE a.fk = b.pk`).

**When.** Нужны только строки с совпадением с обеих сторон.

**Pitfalls.** Условие «только отдел 10» — в `WHERE`, а не в `ON`, если фильтр относится к одной таблице после inner join.

```sql
SELECT e.ename, d.loc
FROM emp e
INNER JOIN dept d ON e.deptno = d.deptno
WHERE e.deptno = 10;
```

*Астахова §2.19.1: STUDENT ↔ EXAM_MARKS по `STUDENT_ID`.*

---

### Multi-column join / INTERSECT

**Problem.** Найти «одинаковые» строки по нескольким столбцам (не только по PK).

**Solution.** `JOIN` с несколькими предикатами в `ON` или `INTERSECT` над проекциями, если столбцы второй стороны не нужны в выводе.

**When.** Сопоставление по бизнес-ключу (ename, job, sal), а не по surrogate key.

**Pitfalls.** Совпадение части столбцов при расхождении других даёт ложные совпадения — перечисляйте все значимые поля.

```sql
SELECT e.empno, e.ename, e.job, e.sal, e.deptno
FROM emp e
JOIN clerk_view v
  ON e.ename = v.ename AND e.job = v.job AND e.sal = v.sal;
```

*Cookbook: «Поиск одинаковых строк в двух таблицах».*

---

### Anti-join: значения / строки «слева без пары справа»

**Problem.** Отделы без сотрудников; ключи из A, отсутствующие в B; полные строки родителя без детей.

**Solution (предпочтительно).** `LEFT JOIN` + `WHERE right.key IS NULL` (anti-join).

**Solution (альтернатива).** `NOT EXISTS (SELECT 1 FROM b WHERE …)` — безопаснее при NULL, чем `NOT IN`.

**When.** Нужны столбцы «сиротской» таблицы; фильтр «нет соответствия».

**Pitfalls.** `NOT IN (subquery)` даёт UNKNOWN при NULL в подзапросе → пустой результат. `INNER JOIN` никогда не покажет отсутствующую сторону.

```sql
-- Anti-join
SELECT d.*
FROM dept d
LEFT JOIN emp e ON d.deptno = e.deptno
WHERE e.deptno IS NULL;

-- То же через NOT EXISTS
SELECT d.*
FROM dept d
WHERE NOT EXISTS (
  SELECT 1 FROM emp e WHERE e.deptno = d.deptno
);
```

*Cookbook: отсутствие в другой таблице; Astakhova §2.19.2 — LEFT OUTER vs UNION + NOT EXISTS.*

---

### LEFT / RIGHT / FULL outer

**Problem.** Сохранить все строки «главной» таблицы, подтянув необязательные данные.

**Solution.** `LEFT OUTER JOIN` (драйвер слева), `RIGHT` (драйвер справа), `FULL` (обе стороны без пары).

**When.** Студенты без оценок; справочник + факты с пропусками.

**Pitfalls.** Oracle legacy: `(+)` у дополняемой таблицы. Смешивание фильтров: предикаты на nullable сторону `JOIN` vs `WHERE` меняют outer-семантику.

```sql
SELECT s.surname, m.mark
FROM student s
LEFT OUTER JOIN exam_marks m ON s.student_id = m.student_id;
```

---

### Cartesian product (осознанно)

**Problem.** Понять, почему join «раздувает» строки, или сгенерировать все пары (редко).

**Solution.** `FROM a CROSS JOIN b` или `FROM a, b` без условия связи.

**When.** Декартово произведение как промежуточный шаг с последующим `WHERE` / `JOIN ON` (как в учебном разборе equi-join).

**Pitfalls.** Забытый предикат связи = экспоненциальный рост строк.

---


## Навигация

- [[corpus/AGENT-INDEX.md|Индекс агента]]
- [[library/INDEX.md|Библиотека (люди)]]
