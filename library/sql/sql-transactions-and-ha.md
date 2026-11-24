# SQL: транзакции, конкурентность и высокая доступность MySQL

Источники:
- *Transactional Information Systems* (Weikum & Vossen, 2002) — `sql/books-md/transaction.md`
- *MySQL High Availability* / «Обеспечение высокой доступности систем на основе MySQL» (Bell, Kindahl, Thalmann, 2012) — `sql/books-md/Обеспечение высокой доступности систем на основе MySQL.md`

Связанные материалы в репозитории: [ddia-patterns.md](../ddia-patterns.md) (репликация, кворумы, multi-leader).

Легенда: **проблема → механизм → компромиссы → сбои → когда применять**.

---

## Транзакционный контракт (ACID)

| | |
|---|---|
| **Проблема** | Совместный доступ к данным без явной координации в коде приложения. |
| **Механизм** | **Atomicity** — commit/rollback; **Consistency** — инварианты (частично приложение, частично БД); **Isolation** — эквивалентность последовательному выполнению; **Durability** — переживает сбой после commit. |
| **Компромиссы** | Изоляция и durability стоят I/O, блокировок и задержек; «быстро без транзакций» против «корректно под нагрузкой». |
| **Сбои** | Откат на consistency violation; после crash без WAL — потеря committed данных. |
| **Когда** | Любая операция «всё или ничего» (перевод, заказ, инвентарь). |
| **Интерфейс** | `BEGIN` / `COMMIT` / `ROLLBACK`; границы транзакции задаёт приложение динамически. |

Компоненты сервера под ACID (Weikum & Vossen): **concurrency control** (изоляция) и **recovery** (атомарность + durability). Производительность измеряют throughput и response time при сохранении контракта.

---

## Изоляция и уровни SQL

| | |
|---|---|
| **Проблема** | Параллельные транзакции дают аномалии: dirty read, lost update, non-repeatable read, phantom. |
| **Механизм** | Классы расписаний (CSR, serializability); в SQL — **isolation levels** как контролируемые ослабления **strict 2PL (S2PL)**. |
| **Уровни (книга TP)** | **READ UNCOMMITTED** — write locks до конца TX, read locks нет; **READ COMMITTED** — write S2PL, read lock на время операции; **SERIALIZABLE** — полный S2PL. **REPEATABLE READ** в стандарте — ослабленная serializability (допускает phantom при определённых протоколах). |
| **MVCC-варианты** | **Multiversion read committed** — читает последнюю committed-версию на момент read; **Snapshot isolation** — снимок на момент начала TX + запись с exclusive locks; близко к serializable для read-only, но write-write аномалии возможны. |
| **MySQL InnoDB** | По умолчанию **REPEATABLE READ** + snapshot (MVCC); phantom частично гасятся **next-key locks**; **READ COMMITTED** — меньше блокировок, выше риск lost update без осторожного кода. |
| **Когда** | Отчёты/статистика — RC или даже dirty (осознанно); OLTP с балансом — RR; критичная финансовая логика — SERIALIZABLE или явные `SELECT … FOR UPDATE`. |

```
Аномалия          | RU | RC | RR/SI | Serializable
------------------+----+----+-------+-------------
Dirty read        | да | нет| нет   | нет
Lost update       | да | да | риск  | нет
Non-repeatable    | да | да | нет*  | нет
Phantom           | да | да | риск  | нет
* при корректном MVCC/2PL на выбранном движке
```

---

## Блокировки и two-phase locking (2PL)

| | |
|---|---|
| **Проблема** | Обеспечить conflict-serializability без полного запрета параллелизма. |
| **Механизм** | **2PL**: фаза наращивания locks (нет unlock до первого unlock) → фаза снятия. Read/write locks; **upgrade** read→write. |
| **Компромиссы** | Строже уровень — больше ожиданий и deadlock; короткие транзакции снижают contention. |
| **Гранулярность** | Строка, страница, таблица — trade-off параллелизм vs накладные расходы. |
| **MySQL** | InnoDB — row-level + intention locks; MyISAM — table locks (без MVCC/rollback). |

---

## Взаимоблокировки (deadlocks)

| | |
|---|---|
| **Проблема** | Циклическое ожидание locks (классика: t1 держит x, ждёт y; t2 наоборот; или concurrent lock upgrade). |
| **Механизм** | **Waits-for graph**; обнаружение continuous vs periodic; **victim selection** — abort одной TX из цикла. |
| **Сбои** | Жертва откатывается; приложение должно **retry** idempotent операций. |
| **MySQL** | InnoDB детектирует deadlock, откатывает «дешёвую» TX; в логах — `SHOW ENGINE INNODB STATUS`. |
| **Практика** | Единый порядок захвата ресурсов; короткие TX; избегать user interaction внутри TX. |

---

## Распределённые транзакции: two-phase commit (2PC)

| | |
|---|---|
| **Проблема** | Атомарность commit/abort на нескольких узлах (XA, 2 DB, message + DB). |
| **Механизм** | Фаза 1: coordinator **prepare** → participants vote yes/no, пишут **prepared** в log; фаза 2: **commit** или **abort** всем. |
| **Компромиссы** | **Blocking protocol**: participant в Prepared ждёт coordinator; locks удерживаются. Гарантия глобальной атомарности ценой автономии и availability. |
| **Сбои** | Coordinator crash после prepare — блокировка до восстановления; **reinfected participants** (отложенные FK/trigger на commit). **Невозможно** independent recovery при множественных сбоях (теорема). |
| **MySQL** | `XA START` / `XA END` / `XA PREPARE` / `XA COMMIT`; репликация **не** делает распределённый commit автоматически. |
| **Когда** | Редко: 2–3 надёжных узла, короткие TX; чаще лучше **saga/outbox** (см. DDIA). |

---

## Репликация MySQL: топологии

| Топология | Схема | Назначение | Риски |
|-----------|--------|------------|--------|
| **Master → slaves** | Один писатель, N читателей | Масштаб чтения, отчёты | Async lag; stale reads |
| **Hot standby** | Master + slave-клон с `log-slave-updates` | Planned/unplanned failover | Сопоставление binlog позиций; `START SLAVE UNTIL` + `CHANGE MASTER` |
| **Active/Passive dual master** | Два master, один пишет | Симметричный switch | Split-brain; конфликты при двух пишущих |
| **Dual active (multi-master)** | Оба пишут + репликация | Геораспределение, локальный latency | Конфликты строк; eventual consistency |
| **Shared disk (SAN)** | Оба mysqld, один datadir | Быстрый failover без binlog remap | SPOF SAN; split-brain без fencing |
| **DRBD + Heartbeat** | Блочная репликация диска | Passive HA, тот же binlog | Медленнее SAN; fencing через STONITH |
| **Relay / hierarchy** | Master → relay → slaves | Фан-аут, снижение нагрузки на master | Доп. hop lag |
| **Circular** | A→B→C→A | Спец. топологии | `replicate-same-server-id`; нужен дизайн |
| **Semisync** (5.5+) | Master ждёт ack slave (relay log на диске) | ≤1 потерянная TX на соединение при crash master | Latency; fallback в async по timeout |

Потоки: **Binlog Dump** (master), **Slave IO** + **Slave SQL** (slave). Форматы: **statement** vs **row** (детерминизм, триггеры).

---

## Failover: процедуры и решения

| | |
|---|---|
| **Проблема** | Crash master; подчинённые на разных `Exec_Master_Log_Pos`. |
| **Planned switchover** (master жив) | Стоп slave + standby на одной позиции (`SHOW SLAVE STATUS`, `START SLAVE UNTIL`, `MASTER_POS_WAIT`); `SHOW MASTER STATUS` на standby; `CHANGE MASTER` для остальных slaves. |
| **Unplanned** | Выбрать **наиболее «осведомлённый»** slave (максимальный применённый binlog); **не** повышать отстающий hot standby если другой slave впереди. |
| **Традиционное promotion** | `STOP SLAVE` → `RESET MASTER` на кандидате → остальные `CHANGE MASTER` с начала нового binlog — **риск**: предполагает, что slave получил все события (часто ложно). |
| **Подготовка к promotion** | На кандидатах: `log-bin`, user `REPLICATION SLAVE`; осознанный выбор `log-slave-updates`. |
| **Split-brain** | Два primary; общий диск/DRBD требует **fencing** (SCSI reserve, STONITH). |
| **Автоматизация** | Книга 2012: Python/Replicant, ручные шаги; см. ниже MHA/Orchestrator как наследники этой модели. |

---

## MHA и Galera (вне книги 2012; операционный слой)

В Bell et al. автоматический failover не выделен в отдельный продукт; ниже — как практика накладывается на главы 4 и 11.

### MHA (Master High Availability Manager)

| | |
|---|---|
| **Проблема** | Ручной promotion медленен и ошибкоопасен при crash master. |
| **Механизм** | Мониторинг master; выбор **latest relay-applied** slave; перестройка топологии (`CHANGE MASTER` для остальных slaves); часто **VIP/DNS** cutover. |
| **Компромиссы** | Не устраняет async gap; semisync снижает RPO, не до нуля без sync quorum. |
| **Связь с книгой** | Автоматизирует «повышение подчинённого» + согласование slaves; требует тех же предпосылок (`log-bin`, replication user). |

### Galera / Percona XtraDB Cluster (синхронный кластер)

| | |
|---|---|
| **Проблема** | Multi-master async + конфликты и split-brain; желание **синхронного commit** на кворуме. |
| **Механизм** | **Group replication / Galera**: certification на commit; все узлы — writers (с оговорками); **synchronous** репликация на majority. |
| **Компромиссы** | Latency записи = RTT кворума; конфликты certifiable transactions → rollback клиенту; не замена бэкапов. |
| **Связь с книгой** | Противопоставление **асинхронной репликации** (гл. 4–5) и **MySQL Cluster/NDB** (гл. 15): Cluster — другой движок (NDB), Galera — InnoDB + wsrep. |
| **Когда** | Несколько AZ, write на любом узле, RPO≈0 на кворуме; не для «один master + много read replicas» без необходимости sync. |

### MySQL Cluster (NDB) — из книги HA

| | |
|---|---|
| **Архитектура** | **mysqld** (SQL) + **NDB** data nodes + **management**; данные секционированы, **NoOfReplicas**. |
| **Транзакции** | Синхронная репликация внутри кластера; не классический InnoDB binlog replication. |
| **Split-brain** | **Arbitrator** (SQL или mgmt node без data); меньшинство останавливается. |
| **Когда** | Telco/встроенные сценарии, жёсткие HA SLA; сложность эксплуатации выше классической репликации. |

---

## Резервное копирование и восстановление

| | |
|---|---|
| **Принцип HA-книги** | **Репликация ≠ бэкап**; redundancy + backup; PITR через binlog. |
| **HA vs DR** | HA — непрерывность; **аварийное восстановление** — восстановление из копии при катастрофе. |

### Сравнение способов (табл. 12-4, HA-книга)

| Метод | Hot | Тип | Скорость копии | Восстановление | Движки / ОС |
|-------|-----|-----|----------------|----------------|-------------|
| **mysqldump** | да* | Логический SQL | Медленно | Медленно | Все; портативно |
| **Физическое копирование** | нет | Физический | Быстро | Быстро | Нужен stop/lock |
| **InnoDB Hot Backup / innobackup** | да | Физический | Средне | Быстро | InnoDB (+MyISAM) |
| **XtraBackup** | да | Физический | Средне | Быстро | InnoDB/XtraDB |
| **LVM / ZFS snapshot** | да** | Физический | Быстро | Быстро | LVM-capable OS |

\* `--single-transaction` для InnoDB. \*\* flush/lock таблиц, отдельный том для datadir.

### Решения «когда что»

| Сценарий | Выбор |
|----------|--------|
| Малый объём, миграция, правка данных в sed | **mysqldump** |
| Большой InnoDB, минимум downtime | **XtraBackup** / Percona |
| Плановый clone slave | `mysqldump --master-data` или snapshot + binlog coord |
| **PITR** | Полный бэкап + **archive binlog** (`mysqlbinlog` replay) |
| Только MyISAM, same host | **mysqlhotcopy** (устаревающий путь) |
| Репликация как «бэкап» | Отдельный delayed slave; не заменяет off-site backup |

Репликация + backup: slave для бэкапа снижает нагрузку на master; фильтры `binlog-do-db` / `replicate-*` **ломают PITR**, если режут журнал.

---

## Мониторинг и устранение сбоев репликации

| Проверка | Команды / поля |
|----------|----------------|
| Lag | `Seconds_Behind_Master`, `SHOW SLAVE STATUS` |
| Потоки | `SHOW PROCESSLIST` — Slave IO/SQL states |
| Master | `SHOW MASTER STATUS`, `SHOW BINARY LOGS` |
| После сбоя | Изучить топологию; безопасный `STOP SLAVE`; не слепо `START SLAVE` — сверить GTID/binlog (в эпохе книги — file+pos) |

---

## Быстрые цепочки решений

### Новый OLTP-сервис на MySQL

1. **InnoDB**, явные транзакции, уровень изоляции по нагрузке (обычно RR).
2. **Master + replicas** для чтения; semisync если RPO критичен.
3. **Ежедневный физический бэкап** + binlog; тест restore.
4. Runbook failover: выбор slave, `log-slave-updates`, документированные позиции.

### «Нельзя терять запись при падении master»

1. Semisync или **Galera/XtraDB Cluster** (кворум).
2. Не полагаться на `RESET MASTER` promotion без проверки lag.
3. Orchestrator/MHA + мониторинг + fencing при dual-master.

### Распределённая транзакция (2 БД)

1. Сначала **избежать 2PC** (saga, outbox, идемпотентность).
2. Если XA неизбежен — короткие TX, надёжный coordinator, план unblock Prepared.

---

## Источники по файлам

| Тема | transaction.md | HA MySQL |
|------|------------------|----------|
| ACID, 2PL, deadlocks | гл. 1, 4, 10 | — |
| 2PC, blocking | гл. 19 | binlog XA (гл. 3) |
| Isolation levels | §10.6.2 | InnoDB (косвенно) |
| Replication topologies | — | гл. 2–6, 10–11 |
| Failover | — | гл. 4 |
| Backup | recovery гл. 13–15 | гл. 12 |
| MySQL Cluster | — | гл. 15 |