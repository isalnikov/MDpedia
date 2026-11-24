# MDpedia (интеграция)

Структура и метаданные по [MDpedia](https://github.com/isalnikov/MDpedia) (MIT): `meta/schema.yaml`, `meta/ai-hints.md`, `distiller_prompt.txt`, `IMPLEMENTATION_PLAN.md`.

Контент `content/` и `aimdpedia/` — **только** материалы репозитория `patterns` (дословные фрагменты и копии скиллов). Генерация: `python3 scripts/build-agent-corpus.py`.

Точка входа для ИИ: `corpus/AGENT-INDEX.md`, граф: `graph/links.json`.