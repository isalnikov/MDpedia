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

### Join + агрегаты без двойного счёта

**Problem.** `SUM(sal)` после join с 1:N дублирует суммы.

**Solution.** (1) Агрегировать **до** join во вложенном запросе/CTE; (2) `SUM(DISTINCT …)` осторожно; (3) оконная `SUM() OVER (PARTITION BY …)` на детализированном наборе, затем `DISTINCT` по ключу.

**When.** EMP + EMP_BONUS (несколько бонусов на сотрудника).

**Pitfalls.** `DISTINCT` внутри `SUM` может скрыть легитимные разные значения с одинаковым sal.

```sql
SELECT d.deptno, d.total_sal, SUM(bonus_expr) AS total_bonus
FROM (
  SELECT deptno, SUM(sal) AS total_sal FROM emp GROUP BY deptno
) d
JOIN emp e ON e.deptno = d.deptno
JOIN emp_bonus eb ON eb.empno = e.empno
GROUP BY d.deptno, d.total_sal;
```

*Cookbook: «Объединения при агрегатных функциях».*

---

## Агрегаты и GROUP BY

### Скалярные агрегаты

**Problem.** Одно число по всей таблице: количество, сумма, среднее, min/max.

**Solution.** `COUNT(*)`, `COUNT(col)`, `SUM`, `AVG`, `MIN`, `MAX`; `COUNT(DISTINCT col)` для уникальных.

**When.** Отчёт «в целом» без разбивки.

**Pitfalls.** `COUNT(*)` считает строки; `COUNT(col)` игнорирует NULL. `AVG` делит только на известные (не NULL) значения.

```sql
SELECT COUNT(DISTINCT subj_id) FROM subject;
SELECT AVG(mark) FROM exam_marks;
```

*Astakhova §2.4–2.5.*

---

### Группировка и HAVING

**Problem.** Метрика по каждой группе; отсечь группы по условию на агрегат.

**Solution.** `GROUP BY` всех неагрегированных столбцов в SELECT; фильтр групп — `HAVING`, строк — `WHERE`.

**When.** MAX(mark) по студенту; предметы с `MAX(hour) >= 72`.

**Pitfalls.** Столбец в SELECT должен быть в `GROUP BY` или внутри агрегатной функции. `HAVING` без `GROUP BY` — один «глобальный» кластер (редко).

```sql
SELECT student_id, MAX(mark)
FROM exam_marks
GROUP BY student_id;

SELECT subj_name, MAX(hour)
FROM subject
GROUP BY subj_name
HAVING MAX(hour) >= 72;
```

---

### Подзапросы в HAVING / сравнение со средним

**Problem.** Оставить группы, где агрегат больше глобального или коррелированного порога.

**Solution.** Скалярный подзапрос в `HAVING` (гарантированно одна строка) или join с предварительно агрегированным набором.

```sql
SELECT subj_id, mark
FROM exam_marks
GROUP BY subj_id, mark
HAVING mark > (SELECT AVG(mark) FROM exam_marks WHERE student_id = 301);
```

*Astakhova §2.8, §2.10.*

---

### DISTINCT vs GROUP BY

**Problem.** Убрать дубликаты строк или подсчитать уникальные комбинации.

**Solution.** `SELECT DISTINCT …` для проекции; `GROUP BY` когда нужны агрегаты по группам. `UNION` (без ALL) убирает дубли между запросами; предпочитайте `UNION ALL`, если дубли допустимы.

**Pitfalls.** Лишний `DISTINCT`/`UNION` — лишняя сортировка/хеш на больших данных.

---

## Оконные функции

### Ранг и нумерация внутри партиции

**Problem.** «Топ-N в группе», удаление дублей по правилу, нумерация без схлопывания строк.

**Solution.** `ROW_NUMBER()`, `RANK()`, `DENSE_RANK() OVER (PARTITION BY … ORDER BY …)`.

**When.** Нужна **детализация строк** + вычисление по «окну» группы; замена коррелированных подзапросов для «последней/первой» записи.

**Pitfalls.** Без `PARTITION BY` окно — весь результат. `ROW_NUMBER` всегда уникален; `RANK` пропускает места после ties.

```sql
SELECT ename, deptno, sal,
       ROW_NUMBER() OVER (PARTITION BY deptno ORDER BY sal DESC) AS rn
FROM emp;
```

*Cookbook: приложение A и глава про reporting / window.*

---

### Скользящие и накопительные суммы

**Problem.** Running total, moving average, сумма в окне дат.

**Solution.** `SUM(…) OVER (ORDER BY … ROWS/RANGE BETWEEN …)`; кастомные рамки для «последние 90 дней найма».

**When.** Отчёты без self-join по дате; KPI «как было на конец периода».

```sql
SELECT hiredate, sal,
       SUM(sal) OVER (ORDER BY hiredate
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_sal
FROM emp;
```

---

### Агрегат по партиции без GROUP BY

**Problem.** Показать каждую строку сотрудника и **одновременно** `total_sal` отдела без подзапроса.

**Solution.** `SUM(sal) OVER (PARTITION BY deptno)` на том же join, где иначе задвоился бы `SUM` после GROUP BY.

**Pitfalls.** После оконных агрегатов часто нужен внешний `SELECT DISTINCT deptno, total_sal, …` или фильтр по `ROW_NUMBER()`.

```sql
SELECT DISTINCT deptno,
       SUM(sal) OVER (PARTITION BY deptno) AS total_sal
FROM emp;
```

*Cookbook: join + `SUM() OVER (PARTITION BY deptno)`.*

---

## Pivot / Unpivot

### Строки → столбцы (reporting)

**Problem.** Crosstab: счётчики/суммы по известному набору категорий в заголовках колонок.

**Solution (портативно).** `SUM(CASE WHEN dim = v THEN measure ELSE 0 END)` + `GROUP BY` ключ отчёта.

**Solution (SQL Server).** `PIVOT (agg FOR col IN ([v1],[v2],…))` над derived table `driver`.

**Solution (Oracle).** `PIVOT` / `MODEL`; **PostgreSQL** — `crosstab` (contrib) или `FILTER (WHERE …)`.

**When.** Фиксированный маленький набор pivot-значений; ETL в витрину.

**Pitfalls.** Новые значения `dim` не появятся как колонки без изменения запроса. `PIVOT` требует агрегат; драйвер должен быть агрегируемым набором.

```sql
-- CASE (везде)
SELECT SUM(CASE deptno WHEN 10 THEN 1 ELSE 0 END) AS dept_10,
       SUM(CASE deptno WHEN 20 THEN 1 ELSE 0 END) AS dept_20
FROM emp;

-- SQL Server PIVOT (идея)
-- SELECT [10] AS dept_10, [20] AS dept_20
-- FROM (SELECT deptno, empno FROM emp) driver
-- PIVOT (COUNT(empno) FOR deptno IN ([10],[20])) p;
```

*Cookbook гл. 14: PIVOT / UNPIVOT.*

### Столбцы → строки

**Problem.** Нормализовать wide-таблицу.

**Solution.** `UNPIVOT` (SQL Server), `UNION ALL` по столбцам, или `LATERAL` + `VALUES` в PostgreSQL.

---

## Иерархические запросы

### Дерево parent–child (вниз от корня)

**Problem.** Все потомки узла; уровень вложенности; путь от корня.

**Solution by DB:**
- **Oracle:** `START WITH … CONNECT BY PRIOR child_pk = parent_pk`, `LEVEL`, `SYS_CONNECT_BY_PATH`
- **Стандарт / PG / SQL Server / DB2:** `WITH RECURSIVE cte AS (anchor UNION ALL recursive) SELECT …`
- **Фиксированная глубина:** цепочка self-joins (2–3 уровня)

**When.** Оргструктура (`mgr`/`empno`), BOM, категории.

**Pitfalls.** Циклы в данных — зацикливание рекурсии; нужен `CYCLE` (SQL:1999) или ограничение глубины. `CONNECT BY` — Oracle-specific.

```sql
-- Рекурсия вверх: MILLER → CLARK → KING (идея Cookbook)
WITH RECURSIVE up AS (
  SELECT empno, ename, mgr, 0 AS depth FROM emp WHERE ename = 'MILLER'
  UNION ALL
  SELECT e.empno, e.ename, e.mgr, up.depth + 1
  FROM emp e JOIN up ON e.empno = up.mgr
)
SELECT * FROM up;
```

---

### Генерация последовательностей (календарь, символы)

**Problem.** Нет таблицы дат; нужен ряд чисел/дней.

**Solution.** `GENERATE_SERIES` (PostgreSQL); рекурсивный `WITH` или `CONNECT BY LEVEL` (Oracle); рекурсия по строке (разбор IP, split delimited list).

*Cookbook: даты, split, listing.*

---

## Строки и даты

### Конкатенация и подстроки

**Problem.** Склеить ФИО; вырезать префикс; padding; регистр.

**Solution.** `||` / `CONCAT()` / `+` (SQL Server); `SUBSTR`/`SUBSTRING`; `LPAD`/`RPAD`; `UPPER`/`LOWER`; `LENGTH`/`LEN`.

**When.** Форматирование вывода, а не хранение (логику лучше в приложении при сложном i18n).

```sql
SELECT UPPER(surname) || ';' || UPPER(name) FROM student;
SELECT SUBSTR(name, 1, 1) || '. ' || surname FROM student;
```

*Astakhova §2.3.3–2.3.5.*

---

### LIKE, NULL-safe сравнения

**Problem.** Поиск по шаблону; трёхзначная логика с NULL.

**Solution.** `LIKE 'И%'`; для отсутствия значения — `IS NULL` / `IS NOT NULL`, не `= NULL`. `UNKNOWN` при `AND`/`OR` с NULL — фильтруйте явно.

*Astakhova §2.2, §2.6.*

---

### Даты: литералы и преобразования

**Problem.** Вывод даты в формате; парсинг строки; арифметика дат.

**Solution (Oracle-стиль в пособии).** `TO_CHAR(date, fmt)`, `TO_DATE(str, fmt)`; интервалы «+ N days» по правилам СУБД. **ISO:** литералы `DATE 'YYYY-MM-DD'`, типы `TIMESTAMP`, функции `EXTRACT`, `DATE_TRUNC` (PG).

**Pitfalls.** Сложение двух полных дат (дата+дата) — непредсказуемо. Сравнивайте timezone-aware типы осознанно.

```sql
SELECT TO_CHAR(birthday, 'DD-MM-YYYY') FROM student;
-- Портативно:
SELECT CAST(birthday AS DATE) FROM student;
```

*Astakhova §1.5.3, §2.3.7.*

---

## Подзапрос vs JOIN vs CTE

| Ситуация | Предпочтение | Почему |
|----------|--------------|--------|
| Добавить столбцы из связанной таблицы | **JOIN** | Один проход, оптимизатор видит связь, читаемый план |
| Фильтр «есть/нет связанных строк» | **EXISTS** / **NOT EXISTS** | Семантика без дублирования; NOT EXISTS безопасен с NULL |
| Фильтр по списку из другой таблицы | **IN (subquery)** или **JOIN** | IN удобен для малого набора; при NULL в списке — EXISTS |
| Скаляр: одно значение на строку (bonus, avg dept) | **Коррелированный подзапрос** или **оконная функция** | Оконные — быстрее на больших данных; подзапрос — если СУБД без window |
| Агрегат до соединения | **CTE / подзапрос в FROM** | Избежать двойного счёта при 1:N |
| Многошаговый pipeline, читаемость | **WITH (CTE)** | Именованные шаги; рекурсия; материализация (зависит от СУБД) |
| «Строки из A без B» с полями A | **LEFT JOIN … WHERE b.key IS NULL** | Эквивалент NOT EXISTS; часто лучше план |
| Только проверка ключей A ⊄ B | **NOT EXISTS** | Не размножает строки |
| Объединить два отчёта | **UNION ALL** + внешний **ORDER BY** | ALL дешевле; сортировка после union |
| Топ-N на группу (до SQL:2003 стиль) | **Подзапрос в WHERE** | Сегодня: **ROW_NUMBER()** |

### Скалярный подзапрос в SELECT

**When.** Одна дополнительная метрика на строку, не меняя join-граф основного запроса.

**Pitfalls.** Подзапрос должен вернуть **ровно одну строку**; иначе runtime error. Несколько строк — join или lateral/outer apply.

*Cookbook: «скалярный vs составной подзапрос»; Astakhova: скаляр только при единственном значении.*

### CTE (`WITH`)

**When.** (1) Повторное использование поднабора; (2) **рекурсия**; (3) документирование этапов ETL-запроса.

**Pitfalls.** В старых версиях — barrier к оптимизации (материализация). Не заменяйте CTE «для красоты» там, где достаточно подзапроса в `FROM`.

*Cookbook: рекурсивный WITH для иерархий, split, календарей.*

---

## Коррелированные подзапросы и EXISTS

### IN / = (скаляр)

```sql
SELECT * FROM exam_marks
WHERE student_id = (SELECT student_id FROM student WHERE surname = 'Петров' LIMIT 1);

SELECT * FROM exam_marks
WHERE student_id IN (SELECT student_id FROM student WHERE city = 'Воронеж');
```

*Astakhova §2.8.*

### EXISTS (полу-join)

```sql
SELECT s.*
FROM student s
WHERE EXISTS (
  SELECT 1 FROM exam_marks m
  WHERE m.student_id = s.student_id AND m.mark < 3
);
```

**Pitfalls.** `COUNT(*) > 0` вместо EXISTS — шумнее; EXISTS останавливается на первом совпадении.

*Astakhova §2.11, §2.14.*

---

## UNION, ORDER BY, представления

- **UNION ALL** — склейка наборов одинаковой формы; **ORDER BY** только снаружи всего union.
- **VIEW** — именованный SELECT; агрегирующие и join-представления для повторного использования (Astakhova гл. 5).

---

## Быстрый указатель по источникам

| Тема | SQL Cookbook | SQL в примерах |
|------|----------------|----------------|
| JOIN, anti-join, OR в JOIN | гл. 3 | §2.18–2.19 |
| Агрегаты, NULL в COUNT/AVG | гл. 4–5, reporting | §2.4–2.6 |
| Подзапросы, EXISTS, ANY/ALL | гл. 1, 3, 14 | §2.8–2.14 |
| Оконные функции | гл. 7–8, прил. A | — |
| PIVOT / crosstab | гл. 14 | — |
| Иерархии, WITH RECURSIVE | гл. 13 | — |
| Строки, TO_CHAR/DATE | гл. 6, 11 | §2.3 |
| CTE vs подзапрос | повсеместно | представления §5 |

---

## Grep-сводка по исходникам (2025-11)

Подсчёт вхождений (`rg -i`), ориентир для навигации по `sql/books-md/`:

| Паттерн | Cookbook (~32k строк) | SQL в примерах (~3.4k строк) |
|---------|----------------------|------------------------------|
| `join` | **85** | **20** |
| `group by` | **323** | **23** |
| `over` / `оконн` / `window` | **248** | **0** |
| `pivot` / `unpivot` | **35** | **0** |
| `connect by` / `рекурсив` / `иерарх` | **231** | **0** |
| `with ` (CTE) | **133** | **0** |
| `подзапрос` / `exists` | **214** | **91** |
| `union` | **247** | **23** |
| `distinct` | **68** | **16** |

**Вывод.** Cookbook — основной корпус по **joins на практике**, **window**, **иерархиям**, **CTE**, **PIVOT** и сложному reporting. Пособие Астаховой — фундамент **SELECT**, **агрегатов**, **NULL**, **подзапросов**, **JOIN/outer**, **строк/дат**; оконных функций в тексте нет.

Примеры grep-команд:

```bash
rg -n -i 'anti.?join|not exists' sql/books-md/SQL-sbornik_retseptov_O_39_Reilly.md
rg -n 'LEFT OUTER JOIN' "sql/books-md/sql в примерах.md"
rg -n -i 'partition by' sql/books-md/SQL-sbornik_retseptov_O_39_Reilly.md
```