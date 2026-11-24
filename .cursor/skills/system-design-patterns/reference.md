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