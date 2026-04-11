#!/usr/bin/env python3
"""
wiki2mdpedia.py — Wikipedia → MDpedia Converter

Пайплайн:
  1. trafilatura — извлечение чистого текста из Wikipedia URL
  2. LLM-дистилляция (OpenAI API / Ollama / совместимый endpoint)
  3. Генерация .ai.md файлов в папке aimdpedia/
  4. Построение graph.json из извлечённых связей

Зависимости:
  pip install trafilatura openai

Использование:
  python wiki2mdpedia.py                          # топ-10 статей по умолчанию
  python wiki2mdpedia.py --urls "url1,url2"       # конкретные URL
  python wiki2mdpedia.py --model ollama --base-url http://localhost:11434/v1
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

import trafilatura

try:
    from openai import OpenAI
except ImportError:
    print("❌ Установите openai: pip install openai")
    sys.exit(1)


# ──────────────────────────────────────────────────────────────
# Конфигурация по умолчанию
# ──────────────────────────────────────────────────────────────

TOP_20_URLS = [
    # ── Топ-10 общие (оригинальные) ──
    "https://ru.wikipedia.org/wiki/Python",
    "https://ru.wikipedia.org/wiki/Искусственный_интеллект",
    "https://ru.wikipedia.org/wiki/Машинное_обучение",
    "https://ru.wikipedia.org/wiki/Квантовая_запутанность",
    "https://ru.wikipedia.org/wiki/Теория_относительности",
    "https://ru.wikipedia.org/wiki/ДНК",
    "https://ru.wikipedia.org/wiki/Чёрная_дыра",
    "https://ru.wikipedia.org/wiki/Блокчейн",
    "https://ru.wikipedia.org/wiki/Интернет_вещей",
    "https://ru.wikipedia.org/wiki/Нейронная_сеть",
    # ── Топ-10 Java 25+ / Spring Boot 4+ ──
    "https://ru.wikipedia.org/wiki/Java",
    "https://ru.wikipedia.org/wiki/Java_Virtual_Machine",
    "https://ru.wikipedia.org/wiki/Spring_Framework",
    "https://ru.wikipedia.org/wiki/Spring_Boot",
    "https://ru.wikipedia.org/wiki/Maven",
    "https://ru.wikipedia.org/wiki/Gradle",
    "https://ru.wikipedia.org/wiki/Jakarta_EE",
    "https://ru.wikipedia.org/wiki/Hibernate",
    "https://ru.wikipedia.org/wiki/JUnit",
    "https://ru.wikipedia.org/wiki/Микросервисы",
]

OUTPUT_DIR = "aimdpedia"
GRAPH_FILE = "graph.json"
PROMPT_FILE = "distiller_prompt.txt"

# Ограничение длины входного текста (токены ~ 4 символя)
MAX_INPUT_CHARS = 25_000


# ──────────────────────────────────────────────────────────────
# Утилиты
# ──────────────────────────────────────────────────────────────

def sanitize_filename(title: str) -> str:
    """Превращает заголовок в безопасное имя файла."""
    name = title.replace(" ", "_").replace("/", "_").replace(":", "_")
    name = re.sub(r"[^\w\-\u0400-\u04FF]", "", name)
    return name[:80]  # обрезаем слишком длинные


def extract_title_from_url(url: str) -> str:
    """Извлекает заголовок статьи из URL Wikipedia."""
    last_part = url.rstrip("/").split("/")[-1]
    return last_part.replace("_", " ")


def fetch_and_clean(url: str) -> Optional[str]:
    """Загружает URL и извлекает чистый Markdown через trafilatura."""
    print(f"  ⬇️  Загрузка: {url}")
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            print(f"  ⚠️  Не удалось загрузить URL")
            return None

        text = trafilatura.extract(
            downloaded,
            output_format="markdown",
            include_links=False,
            include_images=False,
            include_tables=True,
        )

        if not text or len(text.strip()) < 100:
            # fallback — plain text
            text = trafilatura.extract(
                downloaded,
                output_format="txt",
                include_links=False,
                include_images=False,
            )

        return text.strip() if text else None
    except Exception as e:
        print(f"  ❌ Ошибка при извлечении: {e}")
        return None


def load_prompt(filepath: str = PROMPT_FILE) -> str:
    """Загружает системный промпт."""
    path = Path(__file__).parent / filepath
    if not path.exists():
        raise FileNotFoundError(f"Промпт не найден: {path}")
    return path.read_text(encoding="utf-8")


def call_llm(client: OpenAI, model: str, system_prompt: str, text: str) -> str:
    """Отправляет текст на дистилляцию через LLM."""
    truncated = text[:MAX_INPUT_CHARS]
    print(f"  🧠 LLM запрос ({model}) — {len(truncated)} символов…")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": truncated},
        ],
        temperature=0.1,
        max_tokens=4096,
    )
    return response.choices[0].message.content.strip()


def parse_links_from_output(text: str) -> list[str]:
    """Извлекает [[Wiki Links]] из ответа LLM."""
    pattern = r"\[\[([^\]]+)\]\]"
    return re.findall(pattern, text)


def build_frontmatter(ai_output: str, title: str) -> str:
    """
    Если LLM не вернула YAML фронтматтер — оборачиваем.
    Проверяем, есть ли уже `---` в начале.
    """
    if ai_output.startswith("---"):
        return ai_output
    # Вставляем минимальный фронтматтер
    fm = f"""---
title: "{title}"
skill: []
level: intermediate
prerequisites: []
embeddings:
  chunk_strategy: semantic-paragraphs
  max_tokens: 512
---

"""
    return fm + ai_output


# ──────────────────────────────────────────────────────────────
# Основная логика
# ──────────────────────────────────────────────────────────────

def process_article(
    client: OpenAI,
    model: str,
    prompt: str,
    url: str,
    output_dir: Path,
) -> Optional[dict]:
    """Обрабатывает одну статью: fetch → LLM → save."""

    title = extract_title_from_url(url)
    print(f"\n{'='*60}")
    print(f"📄 {title}")
    print(f"{'='*60}")

    # 1. Fetch & clean
    raw_text = fetch_and_clean(url)
    if not raw_text:
        return None

    print(f"  📝 Извлечено: {len(raw_text)} символов")

    # 2. LLM distillation
    try:
        ai_markdown = call_llm(client, model, prompt, raw_text)
    except Exception as e:
        print(f"  ❌ Ошибка LLM: {e}")
        return None

    # 3. Ensure frontmatter
    ai_markdown = build_frontmatter(ai_markdown, title)

    # 4. Save .ai.md
    safe_name = sanitize_filename(title)
    filename = f"{safe_name}.ai.md"
    filepath = output_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(ai_markdown)

    print(f"  ✅ Сохранено: {filepath}")

    # 5. Extract graph links
    links = parse_links_from_output(ai_markdown)
    print(f"  🔗 Найдено связей: {links}")

    return {
        "title": title,
        "file": filename,
        "url": url,
        "prerequisites": links,
        "chars": len(raw_text),
    }


def build_graph(articles: list[dict], output_dir: Path) -> None:
    """Строит graph.json из результатов обработки статей."""

    all_titles = {a["title"] for a in articles}
    nodes = {}
    edges = []

    for article in articles:
        title = article["title"]
        nodes[title] = {
            "file": article["file"],
            "url": article["url"],
            "prerequisites": article["prerequisites"],
            "weight": 1.0,
        }
        for prereq in article["prerequisites"]:
            edges.append({
                "from": title,
                "to": prereq,
                "relation": "DEPENDS_ON",
            })

    # Entry points — маппинг запросов на статьи
    entry_points = {}
    for article in articles:
        title = article["title"]
        entry_points[title.lower()] = title
        # aliases из URL
        url_title = extract_title_from_url(article["url"])
        entry_points[url_title.lower()] = title

    graph = {
        "nodes": nodes,
        "edges": edges,
        "entry_points": {
            "query_patterns": entry_points
        },
        "stats": {
            "total_articles": len(articles),
            "total_edges": len(edges),
        },
    }

    graph_path = output_dir / GRAPH_FILE
    with open(graph_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)

    print(f"\n📊 Граф сохранён: {graph_path}")
    print(f"   📈 Узлов: {len(nodes)}, Рёбер: {len(edges)}")


def main():
    parser = argparse.ArgumentParser(description="Wikipedia → MDpedia Converter")
    parser.add_argument(
        "--urls",
        type=str,
        default=None,
        help="Список URL через запятую (по умолчанию — топ-10)",
    )
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="LLM модель")
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="Base URL для API (для Ollama: http://localhost:11434/v1)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.environ.get("OPENAI_API_KEY", ""),
        help="API ключ (или переменная OPENAI_API_KEY)",
    )
    parser.add_argument("--output", type=str, default=OUTPUT_DIR, help="Папка вывода")
    parser.add_argument(
        "--prompt", type=str, default=PROMPT_FILE, help="Файл промпта"
    )
    parser.add_argument(
        "--delay", type=int, default=2, help="Задержка между запросами (сек)"
    )
    args = parser.parse_args()

    # URLs
    urls = (
        [u.strip() for u in args.urls.split(",") if u.strip()]
        if args.urls
        else TOP_20_URLS
    )

    # Output dir
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Client
    client_kwargs = {"api_key": args.api_key} if args.api_key else {}
    if args.base_url:
        client_kwargs["base_url"] = args.base_url
    client = OpenAI(**client_kwargs)

    # Prompt
    system_prompt = load_prompt(args.prompt)

    # Process
    print(f"🚀 MDpedia Converter — {len(urls)} статей")
    print(f"   Модель: {args.model}")
    print(f"   Вывод:  {output_dir}")
    print(f"   Задержка: {args.delay}с")

    articles = []
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}]")
        result = process_article(client, args.model, system_prompt, url, output_dir)
        if result:
            articles.append(result)

        if i < len(urls):
            time.sleep(args.delay)

    if not articles:
        print("\n❌ Ни одна статья не обработана")
        sys.exit(1)

    # Build graph
    print(f"\n{'='*60}")
    print("🔨 Построение графа…")
    build_graph(articles, output_dir)

    print(f"\n🎉 Готово! {len(articles)} статей в {output_dir}/")
    print(f"   Запусти: cat {output_dir}/graph.json")


if __name__ == "__main__":
    main()
