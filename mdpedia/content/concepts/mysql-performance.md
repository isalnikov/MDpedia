---
title: "High Performance MySQL — паттерны и решения"
skill: ["mysql", "performance"]
level: advanced
source: "library/sql/mysql-performance-patterns.md"
embeddings:
  chunk_strategy: headings
  max_tokens: 2048
relations:
  parent: corpus/AGENT-INDEX.md
---

# High Performance MySQL — паттерны и решения

## Источник (полный текст)

`library/sql/mysql-performance-patterns.md`

## Ядро для ИИ (Embedding Target)

> Дословный фрагмент из `library/sql/mysql-performance-patterns.md` (первые 120 строк, не более 24000 символов).

---
source: sql/books-md/High.Performance.MySQL.3rd.Edition.md
version: "3rd Edition (2012)"
mysql_era: "5.0–5.6 (book); принципы применимы к 8.x с оговорками"
document: High Performance MySQL (Schwartz, Zaitsev, Tkachenko)
purpose: экспертный гид «когда что выбирать» для производительности MySQL
language: ru
technical_terms: en
---

# High Performance MySQL — паттерны и решения

Сжатый operational guide по *High Performance MySQL*, 3rd ed. (O’Reilly, 2012). Главы 1–11, 14; приложение D (EXPLAIN). Ссылки на разделы — по **Table of Contents** книги.

**Базовый принцип:** оптимизация = снижение **response time** (время на задачу/запрос), а не «минимизация CPU» или «максимизация QPS». Нельзя надёжно оптимизировать то, что не измеряете (глава 3).

**Оговорка по версии:** книга описывает Query Cache, MyISAM как рабочий default, Percona Server 5.x. В MySQL 8.0 Query Cache удалён; default — **InnoDB**. Механика InnoDB, индексов, EXPLAIN и репликации остаётся актуальной; сверяйте устаревшие фичи с docs вашей версии.

---

## 1. Метаданные

| Поле | Значение |
|------|----------|
| Источник | `sql/books-md/High.Performance.MySQL.3rd.Edition.md` |
| Издание | 3rd ed., 2012 |
| Фокус глав | Ch 1 архитектура, 2 benchmark, 3 profiling, 4 schema, 5 indexes, 6 queries, 7 advanced (partitioning, query cache), 8 server settings, 9–10 HW + replication, 11 scaling, 14 app cache |
| EXPLAIN | Appendix D (стр. 719 в печатном TOC) |

---

## 2. Storage Engine — матрица выбора (Ch 1)

| Сценарий | Engine | Когда **да** | Когда **нет** |
|----------|--------|--------------|---------------|
| Default / не уверены | **InnoDB** | Транзакции, crash recovery, online backup, clustered index | — |
| Order processing, финансы | **InnoDB** | ACID, FK constraints | — |
| Append-only лог, телеметрия | **MyISAM** / **Archive** | Очень быстрые bulk INSERT, read-mostly отчёты с **replica** | Нужна durability без сюрпризов при crash |
| Read-mostly каталог | **InnoDB** (авторы) | Данные в памяти, clustered index; MyISAM «падает» под нагрузкой | Геопоиск только в MyISAM (fulltext/spatial ограничения эпохи) |
| Чистый in-memory scratch | **MEMORY** | Временные lookup-таблицы | «Общий» кэш; размер, перезапуск теряют данные |
| Периодические агрегаты | **Archive** / summary tables | Сжатие, архив | OLTP на тех же таблицах |

**DDIA:** `ddia-patterns.md` — B-tree (OLTP), WAL, durability vs производительность.

### 2.1 Logging + тяжёлые отчёты

| Паттерн | Описание | Когда |
|---------|----------|-------|
| **Read replica for reports** | INSERT на master, SELECT на replica | Отчёты конкурируют с real-time write |
| **Sharding-by-time table names** | `web_logs_2012_01` | Запрос к «закрытым» месяцам без блокировки текущего лога |

---

## 3. Schema Design & Data Types (Ch 4)

### 3.1 Типы данных

| Принцип | Когда применять | Когда не |
|---------|-----------------|----------|
| **Smaller is better** | VARCHAR вместо CHAR; INT вместо BIGINT; нормальный precision для DECIMAL | Микро-оптимизация важнее корректности домена |
| **Avoid NULL** (с осторожностью) | NOT NULL + default для известных инвариантов | Искусственные «магические» −1 / `0000-00-00` вместо NULL |
| **ENUM vs VARCHAR** | Фиксированный малый домен | SET/ENUM для взаимоисключающих флагов — пересмотреть модель |
| **Synthetic identifiers** | `AUTO_INCREMENT` / monotonic PK для InnoDB | UUID/random как **clustered PK** — фрагментация, random I/O |

### 3.2 Normalization vs Denormalization

| Подход | Когда **use** | Когда **avoid** |
|--------|---------------|-----------------|
| **Normalized schema** | Write-heavy; мало дубликатов; DISTINCT/GROUP BY для списков | Read-heavy с join’ами на больших объёмах |
| **Denormalized schema** | Read-mostly; full scan одной таблицы быстрее random I/O join | Частые обновления → risk inconsistency |
| **Hybrid** | **Cache tables**, **summary tables**, **counter tables** (Ch 4) | Дублирование «на всякий случай» без профиля |

**DDIA:** нормализация vs денормализация; вторичные индексы; materialized views.

### 3.3 Паттерны схемы

| Pattern | Назначение | Риск |
|---------|------------|------|
| **Summary table** | Предварительная агрегация | Синхронизация с master data |
| **Counter table** | Высокочастотные UPDATE счётчиков | Hot row; батчинг/разбиение |
| **Materialized view** (эмуляция) | Дорогой отчёт из сырых данных | Staleness |
| **Cache table** | Денормализация под конкретный read path | Инвалидация |

---

## 4. Indexing (Ch 5)

### 4.1 Базовая матрица

| Pattern | Когда **use** | Когда **not** |
|---------|---------------|---------------|
| **B-Tree index** | Фильтрация, sort, join по префиксу | Hash/spatial/fulltext — другая семантика |
| **Multicolumn index** | WHERE + ORDER BY / несколько фильтров | Колонки «для галочки» — порядок решает |
| **Column order (left-prefix)** | Equality cols слева, range — последняя equality | Ожидать index use при пропуске левых колонок |
| **Prefix index** | Длинные VARCHAR/BLOB/TEXT | Низкая selectivity; нельзя покрыть ORDER BY |
| **Covering index** | `Using index` — только листья индекса | SELECT * ломает covering |
| **Clustered index (InnoDB PK)** | PK = порядок физического хранения | Random PK inserts |
| **Secondary index** | Поиск по неключевым полям | Каждый secondary = cost на write + lookup PK |
| **Index for sorting** | `type: index` + нет `Using filesort` | Filesort при несовпадении order индекса |
| **Redundant / duplicate indexes** | Аудит схемы | Два индекса `(a,b)` и `(a)` |
| **Unused indexes** | Мониторинг `STATISTICS` / pt-idx-usage | Дроп без доказательства неиспользования |

### 4.2 Стратегии

| Техника | Условие |
|---------|---------|
| **Index isolation** | Колонка в WHERE без функции/типа, ломающего sargability |
| **Avoid multiple range conditions** | Два RANGE на одном multicolumn — часто один range работает |
| **Loose index scan** | MIN/MAX по префиксу индекса (Ch 6) |
| **Indexes and locking** | Индекс сужает locked rows; server-side `Using where` после InnoDB |

**DDIA:** вторичные индексы; B-tree; skew.

### 4.3 Clustered PK — decision

| PK strategy | Когда | Pitfall |
|-------------|-------|---------|
| **AUTO_INCREMENT** | Monotonic insert, sequential leaf pages | Hot spot upper PK при extreme concurrency |
| **Natural key** | Короткий, стабильный, уникальный | Длинные строки раздувают secondary indexes |
| **UUID** | Распределённая генерация ID | Random inserts → splits, fragmentation → `OPTIMIZE TABLE` |


## Навигация

- [[corpus/AGENT-INDEX.md|Индекс агента]]
- [[library/INDEX.md|Библиотека (люди)]]
