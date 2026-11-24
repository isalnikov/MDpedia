# Подключение корпуса к внешнему ИИ-агенту

Источник путей: `corpus/MANIFEST.json` (генерируется `scripts/build-agent-corpus.py`).

## Точки входа

| Файл | Назначение |
|------|------------|
| `corpus/AGENT-INDEX.md` | Индекс + `library/INDEX.md` + `README.md` + `mdpedia/meta/ai-hints.md` |
| `mdpedia/graph/links.json` | Маршрутизация skill → concept |
| `mdpedia/graph/skills.json` | Реестр скиллов |
| `mdpedia/meta/schema.yaml` | Схема frontmatter |
| `mdpedia/meta/distiller_prompt.txt` | Промпт MDpedia (для будущей дистилляции **только** из `books-md/`) |
| `mdpedia/content/tutorials/AGENT-READORDER.md` | `INDEX.md` + `README.md` |

## Скиллы (исполняемые инструкции)

- `mdpedia/content/skills/system-design-patterns.skill.md` — копия `.cursor/skills/system-design-patterns/SKILL.md`
- `mdpedia/content/skills/spring-boot-expert.skill.md` — копия `.cursor/skills/spring-boot-expert/SKILL.md`

## Концепты (вложения для RAG)

`mdpedia/content/concepts/*.md` — frontmatter MDpedia + дословный фрагмент из `library/*.md`.

## Первичка

`books-md/*.md` — полные тексты из PDF (см. `MANIFEST.json` → `books_md`).