# Pattern library workspace

Книги в PDF конвертированы в Markdown; из них собрана структурированная библиотека и скилл для проектирования.

## Структура

| Путь | Назначение |
|------|------------|
| `*.pdf`, `spring-boot-reference.pdf` | Исходные книги и Spring Boot Reference |
| `books-md/` | Текст после `scripts/pdf_to_md.py` (pdftotext) |
| `library/` | Каталоги паттернов, [INDEX.md](./library/INDEX.md), [INDEX.html](./library/INDEX.html) |
| `corpus/` | Точка входа для ИИ: `AGENT-INDEX.md`, `MANIFEST.json` |
| `mdpedia/` | Граф, concepts, копии скиллов (формат [MDpedia](https://github.com/isalnikov/MDpedia)) |
| `.cursor/skills/system-design-patterns/` | Скилл агента Cursor |
| `scripts/pdf_to_md.py` | Повторная конвертация PDF → MD |

## Источники

1. **Kleppmann** — *Высоконагруженные приложения* (DDIA)
2. **Fowler** — *Шаблоны корпоративных приложений* (PEAA)
3. **Hohpe & Woolf** — *Шаблоны интеграции корпоративных приложений* (EIP)
4. **Medjaoui et al.** — *Непрерывное развитие API* (Continuous API Management)
5. **Spring Boot Reference** 3.2.3 — `spring-boot-reference.pdf` → [spring-boot-decisions.md](./library/spring-boot-decisions.md)

> Файл `nepreriv_razvit.pdf` — это **Continuous API Management**, не Continuous Delivery (Humble/Farley).

## Использование

- Люди: [library/INDEX.html](./library/INDEX.html) или [library/INDEX.md](./library/INDEX.md).
- ИИ-агент (любая среда): [corpus/AGENT-INDEX.md](./corpus/AGENT-INDEX.md) → [mdpedia/graph/links.json](./mdpedia/graph/links.json) → скиллы в `mdpedia/content/skills/` или `.cursor/skills/`.
- Cursor: скиллы `system-design-patterns`, `spring-boot-expert`.

Пересборка корпуса: `python3 scripts/build-agent-corpus.py`

### Переконвертация книг

```bash
python3 scripts/pdf_to_md.py
```

## Субагенты

Каталоги в `library/` подготовлены отдельными агент-сессиями с разбором соответствующих `books-md/*.md`.