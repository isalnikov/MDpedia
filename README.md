# MDpedia

> **AI-first knowledge base** — Markdown + Graph + Skills

Знания, оптимизированные для ИИ-агентов, а не только для человеческого чтения.

## 🔥 Концепция

Обычная Википедия содержит шум, длинные тексты и не имеет явных связей — всё это мешает LLM эффективно использовать знания.

**MDpedia решает это через:**

| Компонент | Назначение |
|-----------|-----------|
| **Markdown-файлы** | Чистые факты без HTML-шума, chunk-friendly |
| **Граф связей** | Явные зависимости: «читай ЭТО перед тем» |
| **Скиллы** | Исполняемые инструкции, дающие ИИ агентность |

## 📁 Структура

```
mdpedia/
├── content/
│   ├── skills/        # Исполняемые инструкции
│   ├── concepts/      # База фактов
│   └── tutorials/     # Пошаговые руководства
├── graph/             # Граф связей и реестр скиллов
├── meta/              # Схемы валидации
├── context_rules/     # Правила сборки контекста
└── scripts/           # CLI инструменты
```

## 🚀 Быстрый старт

```bash
# Клонировать репозиторий
git clone https://github.com/isalnikov/MDpedia.git
cd MDpedia

# Валидация контента (после установки зависимостей)
npm run validate

# Построить граф связей
npm run build-graph
```

## 📖 Документация

- [**IMPLEMENTATION_PLAN.md**](./IMPLEMENTATION_PLAN.md) — детальный план реализации
- [**meta/schema.yaml**](./meta/schema.yaml) — спецификация фронтматтера
- [**meta/ai-hints.md**](./meta/ai-hints.md) — инструкции для парсеров

## 🎯 Use Cases

- **AI-агенты** — Cursor, Copilot, Claude используют MDpedia как базу знаний
- **RAG-пайплайны** — графовый поиск контекста вместо векторного similarity
- **Enterprise** — приватная вики компании с графом зависимостей проектов
- **Обучение** — навигация от beginner к advanced через граф prerequisites

## 🌍 Языки

- 🇷🇺 **Русский** (этот файл)
- 🇬🇧 [English](README_EN.md)
- 🇨🇳 [中文](README_ZH.md)

## 🤝 Contributing

Contributing guidelines в разработке. Следите за обновлениями.

## 📄 License

MIT
