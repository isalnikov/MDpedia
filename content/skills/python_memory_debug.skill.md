---
name: Python Memory Debug
version: 1.0
inputs: [python_code]
outputs: [memory_report, fix_suggestions]
tags: [python, debugging, memory]
---

# SKILL: Python Memory Debug

## Когда применять
- Утечка памяти в долгоживущем Python-процессе
- Подозрение на циклические ссылки
- Непонятный рост потребления RAM

## Алгоритм

### Шаг 1: Включить tracemalloc
```python
import tracemalloc
tracemalloc.start()

# ... ваш код ...

snapshot = tracemalloc.take_snapshot()
```

### Шаг 2: Сравнить снэпшоты
```python
snapshot1 = tracemalloc.take_snapshot()
# ... выполнить операцию ...
snapshot2 = tracemalloc.take_snapshot()

top_stats = snapshot2.compare_to(snapshot1, 'lineno')
for stat in top_stats[:10]:
    print(stat)
```

### Шаг 3: Проверить циклические ссылки
```python
import gc
gc.collect()
unreachable = gc.garbage
if unreachable:
    print(f"Найдено {len(unreachable)} недостижимых объектов")
```

### Шаг 4: Рекомендации
- Если найдены циклические ссылки → использовать `weakref`
- Если утечка в C-расширениях → проверить `Py_INCREF`/`Py_DECREF`
- Для долгосрочного мониторинга → `memray` или `objgraph`

## Связи
- ТРЕБУЕТСЯ: [[python_gc]]
- РОДИТЕЛЬ: [[memory_management]]
