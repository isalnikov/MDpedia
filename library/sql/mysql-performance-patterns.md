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

---

## 5. EXPLAIN (Appendix D + Ch 6)

### 5.1 Вызов и ограничения

| Вариант | Когда |
|---------|-------|
| `EXPLAIN SELECT` | Стандартный план |
| `EXPLAIN EXTENDED` + `SHOW WARNINGS` | «Reverse compile» оптимизатора (5.0+) |
| `EXPLAIN PARTITIONS` | Partition pruning (5.1+) |
| Rewrite UPDATE/DELETE → SELECT | Нет нативного EXPLAIN для write (до 5.6) |

**Когда EXPLAIN врёт / неполон:** оценки `rows`, subquery materialization, LIMIT в старых версиях, смешение `filesort` in-memory vs on-disk, триггеры/UDF, stored procedures.

### 5.2 `type` — от лучшего к худшему

| type | Смысл | Действие при проблеме |
|------|-------|------------------------|
| **system / const** | Одна строка, константа | — |
| **eq_ref** | Уникальный lookup (PK/unique) | — |
| **ref** | Non-unique index lookup | — |
| **range** | Диапазон по индексу | Отличать `BETWEEN` от `IN`/`OR` (Ch 5 sidebar) |
| **index** | Full index scan | OK если `Using index` (covering); иначе дорого |
| **ALL** | Full table scan | Индекс, переписать запрос, partitioning |

### 5.3 `Extra` — красные флаги

| Extra | Интерпретация |
|-------|----------------|
| **Using index** | Covering index (не путать с `type: index`) |
| **Using where** | Фильтр после чтения строк/индекса |
| **Using temporary** | Temp table (disk vs memory не видно) |
| **Using filesort** | Сортировка вне индекса |

### 5.4 Метрика «слишком много данных»

| Сигнал | Порог (эвристика Ch 6) |
|--------|-------------------------|
| Rows examined >> rows returned | Часто 10:1+ — искать лучший access type |
| Bad `type` | Добавить/исправить индекс под WHERE/JOIN |

---

## 6. Query Optimization (Ch 6)

### 6.1 Порядок оптимизации

1. **Optimize data access** — меньше строк, лучший access type (`EXPLAIN`).
2. **Restructure query** — join decomposition, chop up, fewer round-trips vs one complex query.
3. **Server / schema** — индексы, типы, кэширование.
4. **Hints** — только когда оптимизатор ошибается (редко).

### 6.2 Реструктуризация

| Pattern | Когда **use** | Когда **not** |
|---------|---------------|---------------|
| **Join decomposition** | Меньше дублирования examine при N:M | Латентность сети app↔DB дороже join |
| **Chopping up a query** | Промежуточные маленькие result sets | Транзакционная целостность одного ответа |
| **Many simple queries** | Кэш app; covering indexes | N+1 из ORM |
| **Complex single query** | Сильный оптимизатор + хорошие индексы | Correlated subqueries, LIMIT на огромном scan |

### 6.3 Типовые запросы

| Тип | Паттерн |
|-----|---------|
| **COUNT()** | Covering index / summary table; избегать `COUNT(*)` на огромных таблицах |
| **JOIN** | Индексы на join keys; порядок join (left-deep tree = порядок строк EXPLAIN) |
| **GROUP BY / DISTINCT** | Индекс по GROUP BY cols; временные таблицы |
| **LIMIT / OFFSET** | Большой OFFSET → keyset pagination |
| **UNION** | Временная таблица UNION RESULT; иногда `UNION ALL` |
| **Subqueries** | Часто → derived table / join; correlated — профилировать |

### 6.4 Query Cache (исторический, MySQL ≤ 5.7)

| Когда **был** полезен | Когда **выключать** |
|----------------------|---------------------|
| Тяжёлый SELECT, маленький result, много повторов | Много writes → invalidation; dominated by simple queries |
| Hit rate: смотреть **какие** запросы кэшируются, не только % | MySQL 8.0+ — **нет query cache** |

**Альтернатива:** Application-Level Cache (Ch 14), Redis/Memcached.

---

## 7. Replication (Ch 10)

### 7.1 Задачи репликации

| Задача | Подходит? |
|--------|-----------|
| **Scale reads** | Да — распределение SELECT |
| **Scale writes** | **Нет** — фундаментально; только sharding/partitioning |
| HA / failover | Да, с оговорками lag/consistency |
| Backup / reporting | Да — delayed replica |
| Zero-downtime DDL | Осторожно — binlog, online DDL |

### 7.2 Форматы (эпоха книги)

| Mode | Когда | Риск |
|------|-------|------|
| **Statement-based (SBR)** | Меньше binlog при простых запросах | Nondeterministic functions, UDF |
| **Row-based (RBR)** | Safer default для mixed workload | Больше binlog bandwidth |
| **Mixed** | Компромисс | Понимать переключение |

### 7.3 Топологии — когда что

| Topology | Use | Avoid |
|----------|-----|-------|
| **Master → replicas** | Read scaling, DR | Multi-master «для записи» без conflict strategy |
| **Master-Master active-active** | Чуть больше write throughput | Split-brain, conflicts, «who is truth» |
| **Ring** | — | Авторы не рекомендуют |
| **Custom (DRBD, Tungsten, etc.)** | OS-level / logical replication | Сложность ops |

### 7.4 Capacity & lag

| Правило | Суть |
|---------|------|
| **Plan to underutilize** | Replica под write+read ломается раньше master |
| **Replication lag** | Single-threaded apply на replica; long transactions на master |
| **Consistency check** | `pt-table-checksum`, сравнение после failover |

**DDIA:** leader–follower; async vs sync replication; replication lag; monotonic reads; consistent prefix.

---

## 8. Partitioning (Ch 7)

### 8.1 Ментальная модель

Партиционирование = **грубый индекс с низким overhead** (уравнение «какая партиция», не B-tree по строкам).

| Стратегия на **очень больших** таблицах | Когда |
|----------------------------------------|-------|
| **Scan, don’t index** | Регулярный sequential scan **части** таблицы; WHERE pruning ≤ few partitions |
| **Hot partition in memory** | «Горячий» срез + обычные индексы на маленькой партиции | Холодные данные на диске |

### 8.2 Типы

| Type | Use case |
|------|----------|
| **RANGE** | Time-series, архив по дате |
| **LIST** | Дискретные категории |
| **HASH** | Равномерное распределение |
| **KEY** | MySQL hash function |

### 8.3 Pitfalls

| Problem | Mitigation |
|---------|------------|
| **NULL defeats pruning** | Dummy partition `VALUES LESS THAN (0)`; 5.5+ `RANGE COLUMNS` |
| **PARTITION BY ≠ index key** | Индекс на `a`, partition by `b` → scan all partition trees |
| **Too many partitions** | Обычно сотни max для «scan strategy» |
| **Не масштабирует writes на один инстанс** | Sharding поверх или несколько writers (сложно) |

**DDIA:** секционирование по диапазону vs по хешу; skew / hot spots.

---

## 9. Caching — слои (Ch 7, 14, 9)

| Layer | Pattern | Когда **use** | Когда **not** |
|-------|---------|---------------|---------------|
| **InnoDB buffer pool** | Page cache rows+indexes | Всегда; size ≈ hot data | «Огромный pool + крошечные данные» |
| **MyISAM key cache** | Только индексы MyISAM | Legacy MyISAM | InnoDB workload |
| **OS page cache** | MyISAM .MYD | — | Двойной учёт с InnoDB |
| **MySQL Query Cache** | Идентичные SELECT | Legacy 5.x, узкий кейс | 8.0+, write-heavy |
| **Application cache** | Memcached/Redis, local static | Частично вычисленный HTML/JSON | Низкий hit rate, инвалидация hell |
| **Summary / cache tables** | Inside MySQL | Дорогой aggregate, периодический refresh | Strong real-time consistency |

**Application-Level Cache (Ch 14):**

| Policy | Tradeoff |
|--------|----------|
| **Local (request-scope)** | Дёшево; нет cross-request sharing |
| **Pregenerated content** | Стабильный read path |
| **Cache hierarchy** | L1 process → L2 Redis |

**DDIA:** кэши и согласованность; read-through vs write-through; stale reads после write.

---

## 10. InnoDB Tuning (Ch 1, 8)

### 10.1 Ключевые Knobs (эпоха книги + наследие)

| Setting / concept | Роль | Когда трогать |
|-------------------|------|---------------|
| **innodb_buffer_pool_size** | Главный consumer RAM; data+indexes+AHIndex+insert buffer | ~70–80% dedicated RAM (минус OS); не больше working set без выгоды |
| **innodb_buffer_pool_instances** | Contention на больших pool (5.5+) | Большой pool, многопоточность |
| **innodb_log_file_size** | Большие логи → реже checkpoint stall | IO-bound writes; tradeoff recovery time |
| **innodb_max_dirty_pages_pct** | «Furious flushing» vs lazy flush | Graceful shutdown; checkpoint stall |
| **Adaptive hash index** | Hot index pages in memory | Иногда отключать на odd workloads (версионно) |
| **Insert buffer** | Secondary index maintenance batching | Heavy secondary index writes |

### 10.2 Поведение

| Phenomenon | Mitigation |
|------------|------------|
| **Checkpoint stall / furious flushing** | Log size, IO capacity, dirty page tuning |
| **Long shutdown** | Снизить dirty pages перед stop |
| **Long warmup** | Percona preload / post-restart scans (`init_file`) |
| **Insert in PK order** | Sequential leaf pages | UUID/random PK — фрагментация |

**DDIA:** WAL; B-tree update-in-place; durability.

---

## 11. Profiling & Benchmarking (Ch 2–3)

### 11.1 Методология

| Шаг | Инструмент / идея |
|-----|-------------------|
| Define goal | Response time per query/task |
| Profile whole stack | App → MySQL → query |
| Find dominant cost | 80/20 в profile |
| Fix + measure again | Не оптимизировать CPU «вслепую» |

### 11.2 Инструменты

| Tool | Когда **use** |
|------|----------------|
| **slow query log** | Низкий overhead, high fidelity; `long_query_time`, микросекунды (Percona) |
| **pt-query-digest** | Агрегация slow log; EXPLAIN каждого pattern |
| **SHOW PROFILE** | Drill-down фазы одного запроса (community, 5.0 era) |
| **Performance Schema / USER_STATISTICS** | Workload stats (5.5+ trajectory) |
| **tcpdump + mk-query-digest** | Когда slow log нельзя |
| **sysbench / custom benchmark** | Capacity planning; полный stack (Ch 2) |
| **innotop / SHOW ENGINE INNODB STATUS** | Buffer pool, locks, deadlocks |

### 11.3 Диагностика

| Симптом | Вероятная причина | Куда смотреть |
|---------|-------------------|---------------|
| Медленный один запрос | Bad plan, bad index, examine too many rows | EXPLAIN, slow log, SHOW PROFILE |
| Весь сервер «тупит» | Locking, checkpoint, disk, replication lag | InnoDB status, disk, `SHOW PROCESSLIST` |
| Intermittent stalls | Furious flush, swap, connection storm | OS stats (Ch 9), intermittent capture (Ch 3) |

---

## 12. Scaling & HA (Ch 11 + cross-refs)

| Approach | Масштабирует reads | Масштабирует writes | Consistency |
|----------|-------------------|---------------------|-------------|
| **Bigger server (scale-up)** | Да | До потолка | Сильная |
| **Read replicas** | Да | Нет | Lag / eventual |
| **Partitioning (single node)** | Частично (pruning) | Через меньшие индексы/hot set | Одна запись |
| **Sharding (application)** | Да | Да | App-level |
| **Caching** | Да | Indirect | Stale risk |

**DDIA:** horizontal scale-out; single-leader; sharding vs single-node partitioning.

---

## 13. Hardware & OS (Ch 9) — кратко

| Тема | Правило книги |
|------|---------------|
| **RAID** | RAID 10 для OLTP; battery-backed cache важен |
| **SSD/flash** | Меняет IO-bound профиль; всё ещё sizing buffer pool |
| **Filesystem** | XFS/ext4 эпохи; doublewrite, direct IO — по версии |
| **64-bit** | Большой buffer pool, много connections |

Связь с **latency percentiles** — `ddia-patterns.md` (p99, не среднее).

---

## 14. Advanced features — когда / не когда (Ch 7)

| Feature | Use | Avoid |
|---------|-----|-------|
| **Partitioning** | TB-scale time-series, pruning | «Магическое ускорение» без prunable WHERE |
| **Views** | Упрощение API | Performance illusion на сложных view |
| **Triggers / SP in DB** | Локальная целостность | Скрытая логика, плохой EXPLAIN visibility |
| **Prepared statements** | Parse once, many executes | Один-off ad hoc |
| **Full-text search** | MyISAM/InnoDB FTS эпохи | Elasticsearch для сложного search |
| **Foreign keys** | InnoDB referential integrity | Cross-shard FK |

---

## Быстрые decision trees

### Медленный SELECT в production

1. **slow query log** / digest → частота + время.
2. **EXPLAIN** → `type`, `rows`, `Extra`.
3. Нет хорошего `type` → **индекс** (multicolumn order по запросам).
4. `Using index` возможен? → **Covering index**.
5. Examine millions, return few → переписать WHERE/JOIN, summary table, cache.
6. Таблица TB+ и time-range → **partitioning** + prunable predicate.

### Рост read нагрузки

1. **Replica** для read-only traffic.
2. **Application cache** для дорогих стабильных read.
3. **Summary tables** для отчётов.
4. Проверить **replication lag** и sticky reads (`ddia-patterns.md`).

### Рост write нагрузки

1. Репликация **не поможет** (Ch 10).
2. Оптимизировать индексы (меньше secondary), batch writes.
3. **Shard** или split домена.
4. Partitioning — pruning, не write scale.

### Новая OLTP-схема

1. **InnoDB**, нормализация по умолчанию.
2. **INT/BIGINT PK AUTO_INCREMENT** (или короткий natural key).
3. Индексы под **конкретные** запросы, не «на каждую колонку».
4. Денормализация только после профиля.

---

## Связь с паттернами репозитория

| Тема MySQL | См. также в `library/` |
|------------|-------------------------|
| Репликация, lag, consistency reads | `ddia-patterns.md` — гл. 5 (replication, monotonic reads) |
| Секционирование, hot spots | `ddia-patterns.md` — гл. 6 (partitioning) |
| B-tree, WAL, materialized views | `ddia-patterns.md` — гл. 3 |
| Кэш, stale data | `ddia-patterns.md` + `peaa-patterns.md` (Identity Map, cache) |
| Connection pooling, data access | `peaa-patterns.md` (Table Data Gateway, Query Object) |
| App-tier cache, messaging | `eip-patterns.md` |
| DataSource, JDBC, JPA tuning | `spring-boot-decisions.md` — § Data starters |

---

## Карта глав книги → этот документ

| Глава HPMySQL | § документа |
|-----------------|-------------|
| 1 Architecture & engines | §2 |
| 2 Benchmarking | §11 |
| 3 Profiling | §11 |
| 4 Schema & types | §3 |
| 5 Indexing | §4 |
| 6 Query optimization | §5–6 |
| 7 Partitioning, query cache, FTS | §6.4, §8, §14 |
| 8 Server settings | §9–10 |
| 9 OS & hardware | §13 |
| 10 Replication | §7 |
| 11 Scaling | §12 |
| 14 Application optimization | §9 |
| App. D EXPLAIN | §5 |

---

*Документ синтезирован из High Performance MySQL, 3rd ed. (2012); при миграции на MySQL 8.x сверяйте удалённые/изменённые фичи (query cache, EXPLAIN FORMAT=TREE, инструменты) с official docs.*