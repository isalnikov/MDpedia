---
title: "SQL: транзакции, конкурентность и высокая доступность MySQL"
skill: ["sql", "transactions", "ha"]
level: advanced
source: "library/sql/sql-transactions-and-ha.md"
embeddings:
  chunk_strategy: headings
  max_tokens: 2048
relations:
  parent: corpus/AGENT-INDEX.md
---

# SQL: транзакции, конкурентность и высокая доступность MySQL

## Источник (полный текст)

`library/sql/sql-transactions-and-ha.md`

## Ядро для ИИ (Embedding Target)

> Дословный фрагмент из `library/sql/sql-transactions-and-ha.md` (первые 120 строк, не более 24000 символов).

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


## Навигация

- [[corpus/AGENT-INDEX.md|Индекс агента]]
- [[library/INDEX.md|Библиотека (люди)]]
