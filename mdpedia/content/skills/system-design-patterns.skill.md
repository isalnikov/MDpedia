---
name: system-design-patterns
description: >-
  Designs and reviews software architectures using the local pattern library
  (PEAA, DDIA, EIP, Continuous API Management). Use when the user asks to
  design a system, choose architecture, microservices vs monolith, data model,
  integration, API strategy, scalability, transactions, messaging, or references
  Fowler, Kleppmann, enterprise patterns, or this patterns repository.
---

# Проектирование систем (pattern library)

## Подготовка

1. Прочитай контекст задачи: домен, нагрузка, команда, legacy, сроки, регуляторика.
2. Открой релевантные файлы в `/home/igor/cursorwork/patterns/library/` (не весь корпус — только нужные разделы):
   - `INDEX.md` — маршрутизация между книгами
   - `peaa-patterns.md` — структура кода и приложения
   - `ddia-patterns.md` — хранение, консистентность, масштаб
   - `eip-patterns.md` — обмен между системами
   - `api-management-patterns.md` — публичные API и governance
3. При спорных терминах сверяйся с `books-md/*.md` (исходник после конвертации PDF).

## Процесс (обязательный порядок)

### Шаг 1 — Ограничения и качества

Зафиксируй в ответе:

- **Функциональные** требования (сценарии).
- **Нефункциональные:** RPS/latency (p50/p99), RTO/RPO, консистентность (strong/eventual), multi-tenant, compliance.
- Триада DDIA: reliability, scalability, maintainability — что важнее всего.

### Шаг 2 — Границы и слои (PEAA)

Выбери и обоснуй:

| Вопрос | Паттерны для сравнения |
|--------|------------------------|
| Доменная логика | Transaction Script vs Domain Model vs Table Module |
| Доступ к данным | Active Record vs Data Mapper; Gateway; Repository |
| Граница транзакции | Unit of Work; Service Layer |
| UI/API вход | Front Controller, MVC; DTO vs Domain Model в API |
| Удалённость | Remote Facade, Data Transfer Object |

Явно назови **отвергнутые** варианты и почему.

### Шаг 3 — Данные (DDIA)

Спроектируй:

- Модель данных (реляционная/документная/граф/колоночная) — ссылка на главу DDIA.
- **Запись/чтение:** один узел vs репликация; leader/follower vs multi-leader; quorum при leaderless.
- **Рост данных:** ключ секционирования, rebalance, вторичные индексы.
- **Транзакции:** граница ACID; распределённые — 2PC только если оправдан; иначе saga/compensation/outbox.
- **Производные данные:** CDC, event log, materialized views; не dual-write.

### Шаг 4 — Интеграция (EIP)

Если есть более одного приложения или асинхронность:

- Стиль: File Transfer / Shared DB (избегать) / Remote Procedure / Messaging.
- Канал, формат сообщения, маршрутизация (Router, Filter), трансформация (Translator, Envelope).
- Надёжность: Idempotent Receiver, Message Store, Dead Letter Channel, Wire Tap для наблюдаемости.

### Шаг 5 — API и эволюция (Continuous API Management)

Если есть внешние или межкомандные API:

- API как продукт: JTBD, DX, документация.
- Стадия жизненного цикла → допустимая агрессивность изменений.
- Governance: централизация vs децентрализация; 10 столпов; versioning & visibility.

## Формат ответа пользователю

```markdown
## Контекст
(кратко)

## Решение (overview)
(диаграмма Mermaid C4/container или компонентов — по возможности)

## Ключевые паттерны
| Область | Паттерн | Зачем |
|---------|---------|-------|

## Риски и сбои
(из DDIA: сети, часы, split brain; из EIP: poison message)

## Эволюция
(схема, API versioning, feature flags)

## Альтернативы
(что отвергли)
```

## Анти-паттерны (проверяй явно)

- **Smart UI** + богатый Domain Model без Service Layer.
- **Distributed monolith** — синхронная паутина без границ данных.
- **Dual write** между БД и брокером без outbox/CDC.
- **2PC/XA** через гетерогенные хранилища «для удобства».
- **Shared database** между автономными сервисами.
- **Anemic domain** при сложных инвариантах.
- API без стратегии версий и наблюдаемости (visibility pillar).

## Ревью существующей архитектуры

1. Составь список компонентов и потоков данных.
2. Для каждого стыка сопоставь с EIP; для каждой БД — с DDIA; для кода — с PEAA.
3. Отметь расхождения с выбранными паттернами и severity (operational / data loss / coupling).
4. Предложи минимальный дифф (принцип минимального scope).

## Примеры триггеров

- «Спроектируй заказ и склад с сагой» → PEAA Service Layer + DDIA outbox/saga + EIP Process Manager / Compensating transaction.
- «Каталог на 100M SKU» → DDIA partitioning + materialized views + PEAA Query Object.
- «Публикуем API партнёрам» → api-management + EIP DTO + Remote Facade.

---

# Шпаргалка выбора

## Сложность домена

| Низкая | Высокая |
|--------|---------|
| Transaction Script | Domain Model + Data Mapper |
| Table Module (Record Set) | Service Layer, Unit of Work |

## Консистентность vs доступность (упрощённо)

| Требование | DDIA-ориентир |
|------------|----------------|
| Баланс, платежи | Сильная консистентность, одна БД/лидер |
| Лента, метрики | Реплики, eventual, materialized views |
| Гео-запись | Multi-leader + конфликты (LWW/CRDT) |

## Синхрон vs асинхрон

| Синхрон | Асинхрон (EIP) |
|---------|----------------|
| Request-Reply, DTO | Publish-Subscribe, Event Message |
| Remote Facade | Message Channel, Idempotent Receiver |
| Тесная связность | Outbox + CDC (DDIA) |

Полные каталоги: `library/INDEX.md`.