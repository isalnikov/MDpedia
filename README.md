# MDpedia — pattern library & agent corpus

> **AI-first knowledge base** — Markdown + Graph + Skills (см. также [README_EN.md](./README_EN.md), [README_ZH.md](./README_ZH.md))

Книги в PDF конвертированы в Markdown; из них собрана библиотека паттернов, корпус для ИИ-агентов и скиллы для проектирования и Spring Boot.

## Структура репозитория

| Путь | Назначение |
|------|------------|
| `aimdpedia/`, `content/`, `graph/`, `meta/` | Исходный каркас MDpedia (демо-концепты) |
| `library/` | Каталоги паттернов, [INDEX.md](./library/INDEX.md), [INDEX.html](./library/INDEX.html) |
| `corpus/` | Точка входа для ИИ: `AGENT-INDEX.md`, `MANIFEST.json` |
| `mdpedia/` | Корпус паттернов: граф, concepts, копии скиллов |
| `books-md/` | Первичные тексты (из PDF) |
| `*.pdf` | **Только локально** (в `.gitignore`, не в GitHub) |
| `.cursor/skills/` | Скиллы Cursor |
| `scripts/` | `pdf_to_md.py`, `build-agent-corpus.py` |

## Источники каталогов

1. Kleppmann — DDIA  
2. Fowler — PEAA  
3. Hohpe & Woolf — EIP  
4. Medjaoui et al. — Continuous API Management  
5. Spring Boot Reference 3.2.3 → [spring-boot-decisions.md](./library/spring-boot-decisions.md)

## Использование

- **Люди:** [library/INDEX.html](./library/INDEX.html)  
- **ИИ-агент:** [corpus/AGENT-INDEX.md](./corpus/AGENT-INDEX.md) → [mdpedia/graph/links.json](./mdpedia/graph/links.json)  
- **Cursor:** скиллы `system-design-patterns`, `spring-boot-expert`  

```bash
python3 scripts/build-agent-corpus.py
python3 scripts/pdf_to_md.py
```

Документация формата: [mdpedia/IMPLEMENTATION_PLAN.md](./mdpedia/IMPLEMENTATION_PLAN.md), [meta/ai-hints.md](./meta/ai-hints.md).

## License

MIT