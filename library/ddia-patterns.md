# DDIA — архитектурные концепции и паттерны

Источник: *Martin Kleppmann, Designing Data-Intensive Applications* (рус. пер. O’Reilly, 2018), файл `books-md/Kleppman_Martin_-_Vysokonagruzhennye_prilozhenia_Bestsellery_O_Reilly_-_2018.md`.

Легенда ссылок:
- **PEAA** — *Patterns of Enterprise Application Architecture* (Fowler)
- **EIP** — *Enterprise Integration Patterns* (Hohpe & Woolf)

Каждая запись: **проблема → компромиссы → сбои → когда применять → связанные PEAA/EIP**.

---

## Часть I. Основы информационных систем

### Глава 1. Надёжность, масштабируемость, сопровождение

#### Триада качеств данных (Reliability, Scalability, Maintainability)

| | |
|---|---|
| **Проблема** | Нагрузка и сбои ломают систему раньше, чем «функциональность»; операционные затраты растут нелинейно. |
| **Компромиссы** | Надёжность стоит избыточности; масштабирование — сложности координации; сопровождение — дисциплины в API и автоматизации. |
| **Сбои** | Каскадные отказы при отсутствии изоляции; «масштабировали CPU», а узкое место — диск/сеть/БД. |
| **Когда** | Базовая рамка для любого архитектурного решения в гл. 2–12. |
| **PEAA/EIP** | — |

#### Горизонтальное масштабирование (scale-out) vs вертикальное (scale-up)

| | |
|---|---|
| **Проблема** | Один узел не вмещает данные или RPS. |
| **Компромиссы** | Scale-out требует репликации, секционирования, распределённого согласования; scale-up упирается в потолок железа. |
| **Сбои** | Неравномерная нагрузка (hot spots); сложность отладки распределённой системы. |
| **Когда** | Рост данных/трафика; предсказуемый рост нагрузки. |
| **PEAA/EIP** | — |

#### Описание и нагрузка (latency percentiles, throughput)

| | |
|---|---|
| **Проблема** | Среднее время ответа скрывает деградацию для части пользователей. |
| **Компромиссы** | Оптимизация p99 удорожает инфраструктуру; SLI/SLO нужно измерять. |
| **Сбои** | Очереди, GC-паузы, «шумные соседи» в multi-tenant. |
| **Когда** | Проектирование SLA, ёмкостное планирование. |
| **PEAA/EIP** | — |

#### Операционная готовность (simplicity, evolvability)

| | |
|---|---|
| **Проблема** | Сложные системы не чинятся под стрессом. |
| **Компромиссы** | Простой дизайн может отложить «блестящие» оптимизации. |
| **Сбои** | Накопление костылей, рассинхрон документации и продакшена. |
| **Когда** | Долгоживущие продукты, многокомандная разработка. |
| **PEAA/EIP** | PEAA: **Separation of Concerns** (на уровне модулей). |

---

### Глава 2. Модели данных и языки запросов

#### Реляционная модель vs документная vs графовая

| | |
|---|---|
| **Проблема** | Impedance mismatch между доменом, приложением и хранилищем; разные паттерны чтения/записи. |
| **Компромиссы** | Нормализация — целостность и гибкие запросы; денормализация/вложенные документы — меньше join’ов; граф — связность, дороже на масштабе. |
| **Сбои** | Документы без схемы: несогласованные поля; граф без индексов — экспоненциальные обходы. |
| **Когда** | Связи «многие-ко-многим» и транзакции → SQL; агрегаты с локальной связностью → document; обход связей — graph. |
| **PEAA/EIP** | PEAA: **Domain Model** vs **Transaction Script**; **Table Module**. |

#### Материализация связей в приложении vs в БД

| | |
|---|---|
| **Проблема** | В NoSQL часто нет join — кто эмулирует связи? |
| **Компромиссы** | Логика в коде гибче, но дублируется; FK в БД — проще инварианты. |
| **Сбои** | N+1, несогласованные кэши. |
| **Когда** | Микросервисы с границами агрегатов (DDD). |
| **PEAA/EIP** | PEAA: **Identity Map**, **Unit of Work**. |

---

### Глава 3. Подсистемы хранения и извлечения

#### Журнализированное хранение (log-structured) / LSM-дерево

| | |
|---|---|
| **Проблема** | Случайная запись на HDD/SSD дорогая при update-in-place. |
| **Компромиссы** | Последовательная запись + compaction; выше write throughput, фоновое уплотнение, read amplification. |
| **Сбои** | Всплески compaction («write stall»); дубли ключей до merge. |
| **Когда** | Write-heavy, ключ–значение, Cassandra, RocksDB, Kafka. |
| **PEAA/EIP** | EIP: неизменяемый **Message Store** (аналогия журнала). |

#### B-дерево (update-in-place)

| | |
|---|---|
| **Проблема** | Нужны эффективные range-запросы и предсказуемое чтение. |
| **Компромиссы** | Оптимизировано под OLTP и индексы; WAL для durability; page split. |
| **Сбои** | Повреждение страниц без WAL; блокировки при concurrent access. |
| **Когда** | Классические RDBMS, индексные структуры. |
| **PEAA/EIP** | — |

#### WAL / журнал упреждающей записи

| | |
|---|---|
| **Проблема** | Как восстановить согласованное состояние после сбоя? |
| **Компромиссы** | Дополнительный I/O на запись; replay при recovery. |
| **Сбои** | Потеря/повреждение WAL → потеря данных или длительное восстановление. |
| **Когда** | Любая durable storage engine; база для **replication log**. |
| **PEAA/EIP** | EIP: **Guaranteed Delivery** (журнал как основа). |

#### Столбцовое хранение и сжатие (column store, RLE)

| | |
|---|---|
| **Проблема** | Аналитика сканирует мало столбцов из огромных таблиц. |
| **Компромиссы** | Отлично для OLAP; слабее для point-updates строки. |
| **Сбои** | Вставки в «широкие» таблицы; мелкие обновления ломают сжатие. |
| **Когда** | DWH, агрегаты, отчёты. |
| **PEAA/EIP** | — |

#### Материализованные представления и OLAP-кубы

| | |
|---|---|
| **Проблема** | Тяжёлые агрегирующие запросы блокируют OLTP или слишком медленны. |
| **Компромиссы** | Быстрое чтение, дорогая/сложная запись и инвалидация. |
| **Сбои** | Устаревший куб; гонки при инкрементальном обновлении. |
| **Когда** | Повторяющиеся отчёты, дашборды (связь с **derived data** в ч. III). |
| **PEAA/EIP** | PEAA: кэширование на уровне **Domain Model** (производное состояние). |

#### Вторичные индексы

| | |
|---|---|
| **Проблема** | Поиск не по первичному ключу. |
| **Компромиссы** | Каждый индекс — стоимость записи; в распределённой БД — cross-partition updates. |
| **Сбои** | Рассинхрон индекса и таблицы при асинхронном обновлении. |
| **Когда** | Любые ad hoc query patterns; в потоковой архитектуре — отдельный **derived index**. |
| **PEAA/EIP** | — |

---

### Глава 4. Кодирование и эволюция

#### Форматы сериализации (language-specific, JSON/XML, binary: Protobuf/Avro/Thrift)

| | |
|---|---|
| **Проблема** | Данные переживают процессы, языки и версии сервисов. |
| **Компромиссы** | JSON — человекочитаем, слабая схема; binary — компактность и скорость; встроенная Java serialization — хрупкость. |
| **Сбои** | Поля с одинаковыми именами, потеря точности чисел, несовместимость версий. |
| **Когда** | API, очереди, снимки, CDC-потоки. |
| **PEAA/EIP** | EIP: **Canonical Data Model**, **Content Enricher** (на границе). |

#### Схема в коде vs схема в хранилище (schema-on-read vs schema-on-write)

| | |
|---|---|
| **Проблема** | Когда валидировать структуру? |
| **Компромиссы** | schema-on-write — целостность на входе; schema-on-read — гибкость загрузки. |
| **Сбои** | «Мусор» в data lake при отсутствии контрактов. |
| **Когда** | DWH/ETL vs гибкие документные БД. |
| **PEAA/EIP** | — |

#### Обратная и прямая совместимость (forward/backward compatibility)

| | |
|---|---|
| **Проблема** | Rolling deploy: старые и новые читатели/писатели одновременно. |
| **Компромиссы** | Avro/Protobuf с ID схемы; запрет на удаление обязательных полей без плана. |
| **Сбои** | Удалённое поле, прочитанное старым кодом; default values mask bugs. |
| **Когда** | Микросервисы, Kafka topics, мобильные клиенты с отставанием версий. |
| **PEAA/EIP** | EIP: **Version Marker** (идея). |

#### Потоки данных: база данных, сервисы, асинхронные сообщения

| | |
|---|---|
| **Проблема** | Где граница транзакции при RPC + messaging? |
| **Компромиссы** | Синхронные вызовы — простая модель, coupling; сообщения — latency и семантика доставки. |
| **Сбои** | Потеря ответа при успешной записи; двойная обработка. |
| **Когда** | Интеграция сервисов (мост к ч. II–III). |
| **PEAA/EIP** | EIP: **Request-Reply**, **Message Channel**, **Datatype Channel**. |

---

## Часть II. Распределённые данные

### Глава 5. Репликация

#### Репликация с одним ведущим (single-leader / leader–follower)

| | |
|---|---|
| **Проблема** | Отказ узла и масштабирование чтения без расщепления записи. |
| **Компромиссы** | Простой total order записей; ведущий — bottleneck и SPOF (нужен failover). |
| **Сбои** | Потеря ведущего без quorum failover; split-brain при двух лидерах. |
| **Когда** | PostgreSQL, MySQL replica, Kafka (per partition). |
| **PEAA/EIP** | EIP: **Master-Slave** канал (идея единственного писателя). |

#### Синхронная vs асинхронная репликация

| | |
|---|---|
| **Проблема** | Durability vs latency при записи. |
| **Компромиссы** | Sync — надёжнее, медленнее; async — риск потери последних записей при failover. |
| **Сбои** | Переключение на отстающую реплику → потеря данных. |
| **Когда** | Финансы — ближе к sync; аналитика — async. |
| **PEAA/EIP** | — |

#### Журнал репликации (WAL shipping, statement-based, row-based, trigger-based)

| | |
|---|---|
| **Проблема** | Как доставить изменения последователям детерминированно. |
| **Компромиссы** | WAL — точно, но привязка к движку; logical decoding — гибче; triggers — накладные расходы. |
| **Сбои** | Недетерминированные UDF ломают statement replication. |
| **Когда** | Основа CDC; основа **event stream** из БД. |
| **PEAA/EIP** | EIP: **Message Store**, **Publish-Subscribe Channel**. |

#### Задержка репликации и гарантии чтения

| **Концепт** | **Проблема** | **Идея** |
|---|---|---|
| **Read your writes** | Пользователь не видит свою запись | Маршрутизация к лидеру или версионирование |
| **Monotonic reads** | «Прыжки во времени» между репликами | Sticky session к одной реплике |
| **Consistent prefix reads** | Причинный порядок нарушен | Поток с гарантией порядка по ключу/партиции |
| **Компромиссы** | Сильнее гарантии → меньше freedom в load balancing |
| **Сбои** | Смешение реплик при round-robin |
| **PEAA/EIP** | PEAA: **Unit of Work** (сессия пользователя); EIP: **Message Sequence** |

#### Multi-leader (multi-master) репликация

| | |
|---|---|
| **Проблема** | Запись в нескольких ДЦ, офлайн-клиенты, уменьшение latency записи. |
| **Компромиссы** | Конфликты записи неизбежны; топология (all-to-all, star). |
| **Сбои** | LWW теряет обновления; конфликты без CRDT/merge UI. |
| **Когда** | CouchDB, Cassandra multi-DC (осторожно), офлайн-first. |
| **PEAA/EIP** | EIP: **Datatype Channel** с конфликтом; **Idempotent Receiver**. |

#### Разрешение конфликтов (LWW, vector clocks, merge)

| | |
|---|---|
| **Проблема** | Две конкурентные записи без лидера. |
| **Компромиссы** | LWW прост, но теряет данные; векторные версии — сложность для клиента. |
| **Сбои** | Скрытые конфликты в LWW. |
| **Когда** | Leaderless, multi-leader, мобильная синхронизация. |
| **PEAA/EIP** | — |

#### Leaderless + quorum (Dynamo-style)

| | |
|---|---|
| **Проблема** | Высокая доступность записи без единого лидера. |
| **Компромиссы** | W + R > N → чтение увидит последнюю запись при строгих условиях; sloppy quorum ослабляет гарантии. |
| **Сбои** | Hinted handoff + конфликтные версии; anti-entropy (Merkle trees) отстаёт. |
| **Когда** | Cassandra, Riak, DynamoDB (с оговорками). |
| **PEAA/EIP** | EIP: **Competing Consumers** на чтении repair. |

---

### Глава 6. Секционирование (partitioning / sharding)

#### Секционирование по диапазону vs по хешу ключа

| | |
|---|---|
| **Проблема** | Данные не помещаются на один узел; нужен маршрут ключ → узел. |
| **Компромиссы** | Range — эффективные сканы, риск hot spots; hash — равномерность, нет range scan. |
| **Сбои** | Hot partition; skew при популярных ключах. |
| **Когда** | HBase/Cassandra token; custom sharding в приложении. |
| **PEAA/EIP** | — |

#### Skew и hot spots (случайные смещения, отдельная таблица hot keys)

| | |
|---|---|
| **Проблема** | Один ключ получает непропорциональный трафик. |
| **Компромиссы** | Сложность логики vs простой hash. |
| **Сбои** | Перегрузка одной секции при вирусном контенте. |
| **Когда** | Celebrity problem в соцсетях, счётчики. |
| **PEAA/EIP** | — |

#### Вторичные индексы в распределённой БД (document-partitioned vs term-partitioned)

| | |
|---|---|
| **Проблема** | Запрос не по partition key. |
| **Компромиссы** | Local index — scatter-gather чтение; global index — дорогая запись (multi-partition). |
| **Сбои** | Транзакции через секции; асинхронный индекс отстаёт. |
| **Когда** | Elasticsearch, Cassandra 2i, «database inside-out». |
| **PEAA/EIP** | EIP: **Scatter-Gather**; асинхронно — **Content Enricher**. |

#### Перебалансировка (fixed partitions, consistent hashing, dynamic splitting)

| | |
|---|---|
| **Проблема** | Добавление/удаление узлов без полного reshuffle. |
| **Компромиссы** | Fixed partitions — проще; consistent hashing — меньше движения данных при N change. |
| **Сбои** | Rebalance во время трафика → двойная запись, временная недоступность. |
| **Когда** | Kafka, Cassandra, Elasticsearch. |
| **PEAA/EIP** | — |

#### Маршрутизация (client / proxy / coordinator)

| | |
|---|---|
| **Проблема** | Кто знает карту partition → node? |
| **Компромиссы** | Client routing — нет hop; coordinator (e.g. mongos) — централизация. |
| **Сбои** | Устаревшая карта маршрутизации. |
| **Когда** | Любой sharded cluster. |
| **PEAA/EIP** | EIP: **Message Router**. |

---

### Глава 7. Транзакции

#### ACID (атомарность, согласованность, изоляция, долговечность)

| | |
|---|---|
| **Проблема** | Сбой посередине многошаговой операции; конкурентные запросы. |
| **Компромиссы** | Сильные гарантии — блокировки, latency, ограничение масштаба. |
| **Сбои** | Долгие транзакции блокируют других; deadlock. |
| **Когда** | OLTP с инвариантами на нескольких строках/таблицах. |
| **PEAA/EIP** | PEAA: **Unit of Work**, **Transaction Script** с явными границами. |

#### Уровни изоляции (read committed, snapshot isolation, serializable)

| | |
|---|---|
| **Проблема** | Аномалии: dirty read, lost update, write skew, phantoms. |
| **Компромиссы** | RC дешевле; SI — MVCC без большинства аномалий; serializable — дороже. |
| **Сбои** | Write skew при SI; lost update при read-modify-write без lock. |
| **Когда** | Явный выбор по типу нагрузки (отчёты → SI, инварианты → serializable). |
| **PEAA/EIP** | PEAA: **Optimistic Offline Lock** / **Pessimistic Offline Lock**. |

#### Двухфазная блокировка (2PL) и сериализуемость

| | |
|---|---|
| **Проблема** | Гарантировать сериализуемый порядок без MVCC-анализаторов. |
| **Компромиссы** | Блокировки на чтение/запись → contention. |
| **Сбои** | Deadlock; блокировки при distributed 2PC. |
| **Когда** | Классические RDBMS; основа понимания **2PC locks**. |
| **PEAA/EIP** | — |

#### SSI (serializable snapshot isolation)

| | |
|---|---|
| **Проблема** | Serializable без блокировок чтения. |
| **Компромиссы** | Abort при конфликте — нужен retry в приложении. |
| **Сбои** | Высокий abort rate под contention. |
| **Когда** | PostgreSQL serializable, FoundationDB. |
| **PEAA/EIP** | PEAA: **Optimistic Offline Lock**. |

#### Однообъектные vs многообъектные операции

| | |
|---|---|
| **Проблема** | Многие NoSQL дают атомарность только по одному ключу/документу. |
| **Компромиссы** | Без multi-object TX — саги, идемпотентность, eventual consistency. |
| **Сбои** | Частичное обновление агрегата. |
| **Когда** | Документ = aggregate root; cross-aggregate — messaging. |
| **PEAA/EIP** | PEAA: **Aggregate** (DDD); EIP: **Process Manager**. |

---

### Глава 8. Проблемы распределённых систем

#### Частичные отказы и ненадёжные сети

| | |
|---|---|
| **Проблема** | В кластере сбой — норма, не исключение. |
| **Компромиссы** | Redundancy, timeouts, retries увеличивают сложность. |
| **Сбои** | Retry storm; cascaded failure. |
| **Когда** | Всегда в распределённой архитектуре. |
| **PEAA/EIP** | EIP: **Circuit Breaker** (в литературе EIP — идея устойчивости). |

#### Обнаружение сбоев (timeouts, phi accrual)

| | |
|---|---|
| **Проблема** | Нет различия slow vs dead. |
| **Компромиссы** | Короткий timeout — ложные срабатывания; длинный — hung resources. |
| **Сбои** | GC pause → ложное объявление узла мёртвым (split brain при failover). |
| **Когда** | RPC, leader election, health checks. |
| **PEAA/EIP** | — |

#### Ненадёжные часы (wall clock, monotonic, NTP drift)

| | |
|---|---|
| **Проблема** | Порядок событий по timestamp некорректен. |
| **Компромиссы** | Логические часы / hybrid logical clocks vs синхронизация NTP. |
| **Сбои** | Leap second, clock jump backward → нарушение уникальности и порядка. |
| **Когда** | LWW, TTL, stream windows — только с осторожностью. |
| **PEAA/EIP** | — |

#### Truth defined by majority / византийские сбои

| | |
|---|---|
| **Проблема** | Что считать «истиной» при рассинхроне? |
| **Компромиссы** | Crash-stop проще; Byzantine — дорогой консенсус. |
| **Сбои** | FLP impossibility без randomness/timeouts. |
| **Когда** | Публичный блокчейн vs in-house DC. |
| **PEAA/EIP** | — |

---

### Глава 9. Согласованность и консенсус

#### CAP / PACELC (критика «бесполезной CAP»)

| | |
|---|---|
| **Проблема** | Маркетинг «CP vs AP» без контекста latency и нормальной работы. |
| **Компромиссы** | При partition — consistency vs availability; иначе — latency vs consistency. |
| **Сбои** | Неверный выбор «AP» там, где нужна линеаризуемость. |
| **Когда** | Выбор Dynamo-style vs RDBMS; объяснение quorum. |
| **PEAA/EIP** | — |

#### Линеаризуемость (linearizability)

| | |
|---|---|
| **Проблема** | Система должна выглядеть как один копия при конкурентных вызовах. |
| **Компромиссы** | Дорого: координация, latency, недоступность при partition (CP). |
| **Сбои** | Coordinator failover окно нелинейности. |
| **Когда** | Блокировки, leader election, уникальность имён, «compare-and-set» для всех. |
| **PEAA/EIP** | — |

#### Упорядоченность: порядковые номера, Lamport, total order broadcast

| | |
|---|---|
| **Проблема** | Согласовать причинный порядок без единого лидера (или с ним). |
| **Компромиссы** | Single leader — простой total order; consensus — универсально, но медленнее. |
| **Сбои** | Нарушение порядка → неверное состояние реплик (state machine replication). |
| **Когда** | Kafka partition, Raft log, ZooKeeper znodes. |
| **PEAA/EIP** | EIP: **Message Sequence**, **Resequencer**. |

#### State machine replication / репликация конечного автомата

| | |
|---|---|
| **Проблема** | Одинаковое конечное состояние на репликах. |
| **Компромиссы** | Детерминированные операции обязательны; недетерминизм ломает replay. |
| **Сбои** | Дрейф реплик при пропуске/переупорядочивании событий. |
| **Когда** | RDBMS replicas, event-sourced projections. |
| **PEAA/EIP** | PEAA: **Event Sourcing** (проекции). |

#### Двухфазная фиксация (2PC) и XA

| | |
|---|---|
| **Проблема** | Атомарность записи в БД + очередь + второй сервис. |
| **Компромиссы** | Сильные гарантии; coordinator SPOF; **in-doubt** locks; операционный кошмар. |
| **Сбои** | Зависшие prepared transactions; heuristic rollback → нарушение атомарности. |
| **Когда** | Редко: homogenous DB internal 2PC OK; heterogeneous XA — избегать. |
| **PEAA/EIP** | EIP: **Transactional Client**; **Idempotent Receiver** как альтернатива. |

#### Саги (компенсирующие транзакции)

| | |
|---|---|
| **Проблема** | Длительная бизнес-транзакция без распределённого lock. |
| **Компромиссы** | Локальные ACID + публичные компенсации; нет изоляции между шагами. |
| **Сбои** | Компенсация не восстанавливает семантику (отправлен email); видимые промежуточные состояния. |
| **Когда** | Микросервисы вместо XA; оркестрация/хореография (книга ссылается на Garcia-Molina). |
| **PEAA/EIP** | EIP: **Process Manager**; PEAA: компенсация на уровне домена. |

#### Отказоустойчивый консенсус (Paxos, Raft, ZooKeeper/etcd)

| | |
|---|---|
| **Проблема** | Единое согласованное решение при сбоях (leader, membership). |
| **Компромиссы** | Требует большинства; latency commit; не масштабируется на throughput записи. |
| **Сбои** | Split vote без quorum; слишком маленький кластер. |
| **Когда** | Метаданные, shard assignment, distributed locks (осторожно). |
| **PEAA/EIP** | — |

#### Сервисы членства и координации

| | |
|---|---|
| **Проблема** | Кто жив в кластере? Кто лидер? |
| **Компромиссы** | Fencing tokens против zombie leader. |
| **Сбои** | Split brain без STONITH/fencing. |
| **Когда** | Kafka controller, HBase, Kubernetes lease. |
| **PEAA/EIP** | — |

---

## Часть III. Производные данные

### Глава 10. Пакетная обработка

#### Unix pipelines / идиома: stdin/stdout, immutability

| | |
|---|---|
| **Проблема** | Повторяемая обработка больших файлов без «Big Data framework». |
| **Компромиссы** | Простота и композиция vs один узел. |
| **Сбои** | Ошибка в середине pipe без checkpoint. |
| **Когда** | ETL прототипы, log analysis; философия MapReduce. |
| **PEAA/EIP** | EIP: **Pipes and Filters**. |

#### MapReduce / HDFS

| | |
|---|---|
| **Проблема** | Параллельная обработка TB+ на commodity hardware. |
| **Компромиссы** | Высокая latency, batch-only; materialized intermediates; мало итераций. |
| **Сбои** | Straggler tasks; partial failure с re-run. |
| **Когда** | Историческая аналитика, индексация, ML feature gen (offline). |
| **PEAA/EIP** | — |

#### Материализация промежуточного состояния (batch)

| | |
|---|---|
| **Проблема** | Shuffle между map и reduce дорог. |
| **Компромиссы** | Full materialization — отказоустойчивость MR; Unix pipes — без mat. |
| **Сбои** | Диск заполнен HDFS; дубли при re-run без idempotent reduce. |
| **Когда** | Выбор Spark (memory) vs classic MR. |
| **PEAA/EIP** | — |

---

### Глава 11. Потоковая обработка

#### Брокер сообщений vs log-based (Kafka)

| | |
|---|---|
| **Проблема** | Доставить события многим потребителям с историей. |
| **Компромиссы** | Classic queue — сообщение «съедается»; log — retention, replay, ordering per partition. |
| **Сбои** | Consumer lag; unbounded retention cost. |
| **Когда** | Event bus, CDC backbone, stream processing input. |
| **PEAA/EIP** | EIP: **Message Channel**, **Publish-Subscribe Channel**, **Message Store**. |

#### Секционирование журнала (key → partition, ordering guarantees)

| | |
|---|---|
| **Проблема** | Масштабирование потока без потери порядка по сущности. |
| **Компромиссы** | Порядок только внутри partition; key skew → hot partition. |
| **Сбои** | Неверный partition key ломает causality. |
| **Когда** | Kafka, Pulsar. |
| **PEAA/EIP** | EIP: **Competing Consumers** (внутри partition group). |

#### Двойная запись (dual write) — антипаттерн

| | |
|---|---|
| **Проблема** | Синхронизировать БД + search index вручную в приложении. |
| **Компромиссы** | Без 2PC — race (рис. 11.4): разный порядок в системах. |
| **Сбои** | Одна запись успешна, вторая нет; конкурентные клиенты. |
| **Когда** | **Избегать**; заменить на CDC или event log as source of truth. |
| **PEAA/EIP** | EIP: **Transactional Client** (редко оправдан); **Idempotent Receiver**. |

#### CDC (Change Data Capture)

| | |
|---|---|
| **Проблема** | Производные системы должны отражать запись в БД в том же порядке. |
| **Компромиссы** | Async → replication lag; parse binlog vs triggers. |
| **Сбои** | Schema drift в логе; initial snapshot + offset coordination. |
| **Когда** | Debezium, search index, cache, DWH feed; **leader as source**. |
| **PEAA/EIP** | EIP: **Event-Driven Consumer**; **Message Translator**. |

#### Log compaction (уплотнение журнала)

| | |
|---|---|
| **Проблема** | Бесконечный log vs восстановление состояния. |
| **Компромиссы** | CDC compaction — последнее значение ключа; event sourcing — полная история. |
| **Сбои** | Удаление tombstone слишком рано. |
| **Когда** | Kafka compacted topics; KV changelog. |
| **PEAA/EIP** | — |

#### Event Sourcing (источники событий)

| | |
|---|---|
| **Проблема** | Моделировать домен как неизменяемые факты, а не mutable row. |
| **Компромиссы** | Отличная аудитируемость и новые read models; сложность команд/событий, нет compaction истории. |
| **Сбои** | Версионирование событий; длинный replay; команда должна валидироваться до append. |
| **Когда** | Сложная доменная логика, несколько представлений, audit. |
| **PEAA/EIP** | PEAA: **Event Sourcing**; EIP: **Event-Driven Architecture** (паттерн). |

#### Команды vs события

| | |
|---|---|
| **Проблема** | Где проверять инварианты? |
| **Компромиссы** | Синхронная валидация до append (serializable TX) vs двухфазное событие (reserve/confirm). |
| **Сбои** | Асинхронная валидация — окно несогласованности. |
| **Когда** | Бронирования, регистрация уникальных имён. |
| **PEAA/EIP** | PEAA: **Domain Model** + агрегаты. |

#### CQRS (разделение команд и запросов)

| | |
|---|---|
| **Проблема** | Одна модель не оптимальна и для записи, и для всех read patterns. |
| **Компромиссы** | Несколько read models; eventual consistency; operational complexity. |
| **Сбои** | Stale read после записи (как replication lag). |
| **Когда** | Разные SLA чтения/записи, event log как источник, множество представлений (Twitter timeline). |
| **PEAA/EIP** | Fowler CQRS; PEAA: разделение **Domain Model** / reporting DB. |

#### Состояние, потоки, неизменяемость

| | |
|---|---|
| **Проблема** | Производное состояние vs источник. |
| **Компромиссы** | Immutable log — простой replay и audit; mutable DB — быстрый point read. |
| **Сбои** | Правка события «задним числом» ломает все проекции. |
| **Когда** | Архитектура **derived data** (глава 12). |
| **PEAA/EIP** | PEAA: **Event Sourcing** snapshots. |

#### Идемпотентность и exactly-once в потоках

| | |
|---|---|
| **Проблема** | At-least-once + retry → дубли. |
| **Компромиссы** | Idempotent writes + deterministic processing; transactional sinks редки. |
| **Сбои** | Partial output перед failure. |
| **Когда** | Stream processors (Flink), consumers CDC. |
| **PEAA/EIP** | EIP: **Idempotent Receiver**, **Message Id**. |

#### Время в потоках (event time vs processing time, windows, watermarks)

| | |
|---|---|
| **Проблема** | Поздние события и reorder. |
| **Компромиссы** | Watermarks → completeness vs delay; session windows сложнее tumbling. |
| **Сбои** | Неверные агрегаты при clock skew. |
| **Когда** | Аналитика потоков, Lambda merge layer. |
| **PEAA/EIP** | — |

---

### Глава 12. Будущее информационных systems / интеграция

#### Система записи vs производные информационные системы (unbundling the database)

| | |
|---|---|
| **Проблема** | Один монолитный движок не покрывает OLTP + search + analytics + cache. |
| **Компромиссы** | Специализация vs операционный зоопарк; sync через log. |
| **Сбои** | Операционная сложность «поли storage». |
| **Когда** | Крупные продукты, **database inside-out**. |
| **PEAA/EIP** | EIP: **Enterprise Integration Patterns** (книга как карта интеграции). |

#### Пакет vs поток (batch as special case of streaming)

| | |
|---|---|
| **Проблема** | Два мира инструментов для одной логики. |
| **Компромиссы** | Flink/Beam unification; micro-batching tradeoffs. |
| **Сбои** | Дублирование кода в Lambda. |
| **Когда** | Выбор одного движка с replay from log. |
| **PEAA/EIP** | EIP: **Pipes and Filters** (batch chain). |

#### Повторная обработка (reprocessing) и эволюция схемы

| | |
|---|---|
| **Проблема** | Миграция read model без big-bang downtime. |
| **Компромиссы** | Два параллельных derived view + постепенный cutover (аналогия «двойной колеи»). |
| **Сбои** | Двойные затраты хранения/CPU на период миграции. |
| **Когда** | Новый индекс, смена CQRS projection, schema-on-read evolution. |
| **PEAA/EIP** | — |

#### Lambda-архитектура

| | |
|---|---|
| **Проблема** | Низкая latency (stream) + корректность/простота на истории (batch). |
| **Компромиссы** | Два пайплайна, merge при запросе, operational burden. |
| **Сбои** | Расхождение batch/speed layer; сложные joins/sessionization в merge. |
| **Когда** | Исторически Hadoop+Storm; сегодня — чаще замена унифицированным потоком. |
| **PEAA/EIP** | — |

#### Унификация пакетной и потоковой обработки (идея Kappa; в рус. пер. без термина «Kappa»)

| | |
|---|---|
| **Проблема** | Дублирование логики Lambda. |
| **Компромиссы** | Один процессор + replay log; нужны event-time semantics и exactly-once. |
| **Сбои** | Дорогой full replay; window bugs при reprocess. |
| **Когда** | Kafka + Flink/Beam, «stream-first». |
| **PEAA/EIP** | — |

#### Производные данные vs распределённые транзакции

| | |
|---|---|
| **Проблема** | Согласованность нескольких stores без XA. |
| **Компромиссы** | Log ordering + idempotent consumers vs linearizability across systems. |
| **Сбои** | Нет «read your writes» в search сразу после POST. |
| **Когда** | Микросервисы, CDC, org-wide log (Kreps «The Log»). |
| **PEAA/EIP** | EIP: **Process Manager**, **Claim Check** для крупных payload. |

#### End-to-end arguments, ограничения в приложении

| | |
|---|---|
| **Проблема** | Не все инварианты выразимы в БД constraints при шардинге. |
| **Компромиссы** | Асинхронная проверка + аудит vs sync constraint в одном узле. |
| **Сбои** | Временное нарушение invariant в derived view. |
| **Когда** | Географически распределённые системы (глава 12.3). |
| **PEAA/EIP** | PEAA: domain validation в **Domain Model**. |

#### Тотальный журнал организации (unifying abstraction)

| | |
|---|---|
| **Проблема** | Интеграция data silos. |
| **Компромиссы** | Единый ordered log масштабируется через partitioning; single leader bottleneck глобально. |
| **Сбои** | Governance, PII, schema registry discipline. |
| **Когда** | Стратегическая data platform. |
| **PEAA/EIP** | EIP: **Channel Adapter** на каждый legacy store → общий log. |

---

## Сводная матрица: репликация и согласованность

| Подход | Запись | Конфликты | Типичная согласованность | DDIA глава |
|--------|--------|-----------|--------------------------|------------|
| Single-leader | Один узел | Нет (на уровне логa) | Eventual read replicas; sync option | 5 |
| Multi-leader | Несколько | Да | Eventual + merge | 5 |
| Leaderless quorum | w узлов | Да (версии) | Tunable (R+W>N) | 5 |
| Consensus | Majority | Нет | Strong (linearizable) | 9 |
| CDC / log fan-out | Лидер БД | Порядок лога | Eventual на derived | 11–12 |

---

## Карта PEAA/EIP ↔ DDIA (быстрый указатель)

| DDIA тема | PEAA | EIP |
|-----------|------|-----|
| Event Sourcing, CQRS | Event Sourcing, Domain Model | Event-Driven Consumer, Message Store |
| CDC, репликация | Unit of Work | Message Translator, Publish-Subscribe |
| Микросервисная интеграция без 2PC | Transaction Script + domain sagas | Process Manager, Idempotent Receiver, Compensating Action |
| Очереди и потоки | — | Message Channel, Competing Consumers, Dead Letter Channel |
| ETL / batch | — | Pipes and Filters, Content Enricher, Scatter-Gather |
| Dual write (анти) | — | Transactional Client (осторожно) → предпочесть log |

---

*Документ подготовлен для репозитория `patterns` как справочник по архитектурным решениям DDIA, а не как замена книги.*