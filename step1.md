Отлично! Давай спроектируем реальный пайплайн для создания **AI-pedia MVP**. Я распишу спецификацию так, чтобы ты мог запустить это хоть на своем ноутбуке с локальной LLM (Llama/Qwen) или через API OpenAI.

## 🎯 Цель MVP
Взять **1 статью из Википедии** (или любой длинный HTML/PDF) и превратить её в структурированный `.md` файл с графом зависимостей в формате JSON.

## 🏗️ Архитектура Парсера (Pipeline)

Процесс будет трехэтапным. Сразу перейдем к сути.

### Этап 1: Экстракция и очистка (Pre-processor)
**Инструмент:** Python + `trafilatura` или `readability-lxml`.
**Задача:** Убрать меню, баннеры, сноски вида `[1]`.

**Промпт для нейросети на этом этапе не нужен, это чистая утилита.**

```python
# Пример кода экстрактора
import trafilatura

def extract_clean_text(url_or_html):
    downloaded = trafilatura.fetch_url(url_or_html)
    # 'xml' режим сохраняет базовую структуру заголовков и ссылок
    clean_markdown = trafilatura.extract(downloaded, output_format='markdown', 
                                         include_links=True, include_images=False)
    return clean_markdown
```

---

### Этап 2: Дистилляция в AI-Markdown (LLM Core)
**Инструмент:** Любая LLM (GPT-4o-mini, Claude Haiku, локальная Qwen2.5-7B).
**Задача:** Сжать «человеческую простыню» в строгую структуру для RAG.

**Вот промпт, который нужно отправить модели (сохрани его как `distiller_prompt.txt`):**

```text
Ты — парсер знаний для AI-агента. Преобразуй предоставленный текст статьи в формат AI-Markdown.

ПРАВИЛА СТРОГОГО ФОРМАТА:

1. **Заголовок H1**: Точное название сущности.
2. **`## TL;DR (Core Vector)`**: 1-2 предложения. Максимально фактологическая выжимка. Это будет подаваться в эмбеддинги.
3. **`## Определение (Definition)`**: Строгое формальное определение (как в словаре).
4. **`## Ключевые факты (Facts)`**: Маркированный список. **Запрещены** вводные слова (например, "Следует отметить, что..."). Только сухие данные.
5. **`## Связи (Graph Hints)`**: Выдели из текста 3-5 ключевых терминов, без понимания которых нельзя понять эту статью. Формат: `- ТЕРМИН (причина важности)`.
6. **`## Противоречия/Нюансы (Caveats)`**: О чем часто ошибаются люди или ИИ? Если есть.

Игнорируй историю открытия, биографии ученых и примечания редакторов.
```

---

### Этап 3: Построение Графа (Graph Builder)
**Инструмент:** Python + `networkx` или просто JSON.
**Задача:** Связать созданные файлы в единую базу.

**Спецификация файла `graph.json` (MVP-версия):**

Нам нужно создать файл, который будет управлять вниманием ИИ (Context Routing).

```json
{
  "nodes": {
    "Квантовая_запутанность": {
      "file": "quantum_entanglement.ai.md",
      "embedding_key": "Квантовая запутанность - это явление корреляции квантовых состояний частиц...",
      "prerequisites": ["Квантовая_суперпозиция"],
      "weight": 1.0
    }
  },
  "edges": [
    {
      "from": "Квантовая_запутанность",
      "to": "Квантовая_суперпозиция",
      "relation": "DEPENDS_ON"
    }
  ],
  "entry_points": {
    "query_patterns": {
      "запутанность": "Квантовая_запутанность",
      "квантовая нелокальность": "Квантовая_запутанность"
    }
  }
}
```

---

## 🚀 Реализация MVP: Код парсера (Python)

Вот готовый скрипт, который можно запустить прямо сейчас. Установи зависимости:
```bash
pip install trafilatura openai networkx
```

**Скрипт `wiki2aipedia.py`:**

```python
import trafilatura
import json
import os
import re
from openai import OpenAI # Или замени на requests для локальной LLM

# --- КОНФИГУРАЦИЯ ---
LLM_MODEL = "gpt-4o-mini" # или "qwen2.5:7b" если через Ollama
API_KEY = "your_key_here"
# --------------------

def call_llm(prompt, text_chunk):
    """Отправляем запрос к LLM для дистилляции"""
    client = OpenAI(api_key=API_KEY)
    
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text_chunk[:15000]} # Ограничиваем контекст
        ],
        temperature=0.1 # Низкая температура для фактологии
    )
    return response.choices[0].message.content

def extract_links_for_graph(text):
    """Грубый поиск вики-ссылок [[...]] или упоминаний для графа"""
    # В реальности нужно использовать NLP, но для MVP сойдет regex по ключевым фразам
    # Парсим связи, которые сгенерировала LLM в секции "## Связи"
    links = []
    pattern = r"^- \[\[(.*?)\]\]|^- (.*?) \("
    matches = re.findall(pattern, text, re.MULTILINE)
    for m in matches:
        link = m[0] if m[0] else m[1]
        if link:
            links.append(link.strip())
    return links

def main(url):
    print(f"🔄 Скачиваем и чистим: {url}")
    downloaded = trafilatura.fetch_url(url)
    raw_text = trafilatura.extract(downloaded, output_format='markdown')
    
    # Если trafilatura не справилась, берем сырой текст без HTML
    if not raw_text:
        raw_text = trafilatura.extract(downloaded, output_format='txt')
    
    title = url.split('/')[-1].replace('_', ' ')
    
    print("🧠 Дистиллируем знания через LLM...")
    with open("distiller_prompt.txt", "r", encoding="utf-8") as f:
        system_prompt = f.read()
    
    ai_markdown = call_llm(system_prompt, raw_text)
    
    # Сохраняем файл .ai.md
    safe_title = re.sub(r'[^\w\-_\. ]', '_', title)
    filename = f"pedia/{safe_title}.ai.md"
    os.makedirs("pedia", exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(ai_markdown)
    
    print(f"✅ Файл сохранен: {filename}")
    
    # Обновляем граф (MVP: просто создаем/дополняем JSON)
    graph_file = "pedia/graph.json"
    graph_data = {"nodes": {}, "edges": []}
    
    if os.path.exists(graph_file):
        with open(graph_file, "r") as f:
            graph_data = json.load(f)
    
    # Добавляем ноду
    graph_data["nodes"][title] = {
        "file": filename,
        "prerequisites": extract_links_for_graph(ai_markdown)
    }
    
    # Строим Edges
    for prereq in graph_data["nodes"][title]["prerequisites"]:
        graph_data["edges"].append({
            "from": title,
            "to": prereq,
            "relation": "DEPENDS_ON"
        })
    
    with open(graph_file, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Граф обновлен: {graph_file}")

if __name__ == "__main__":
    # ТЕСТ: Запуск на статье про Python
    main("https://ru.wikipedia.org/wiki/Python")
```

---

## 📄 Результат работы: Как будет выглядеть файл `.ai.md`

После прогона статьи «Квантовая запутанность» через этот парсер, получится примерно такой файл:

```markdown
# Квантовая запутанность

## TL;DR (Core Vector)
Квантовая запутанность — явление, при котором состояния двух или более частиц оказываются взаимозависимыми независимо от расстояния между ними. Изменение состояния одной частицы мгновенно отражается на состоянии другой.

## Определение (Definition)
Квантовая запутанность — квантовомеханическое явление, описывающее состояние системы из двух и более частиц, которое не может быть факторизовано как произведение состояний отдельных подсистем.

## Ключевые факты (Facts)
- Запутанные частицы ведут себя как единая система.
- Измерение параметра одной частицы мгновенно коллапсирует волновую функцию второй.
- Скорость передачи информации ограничена скоростью света; запутанность не нарушает принцип причинности.
- Используется в протоколах квантовой телепортации и шифрования (BB84, E91).

## Связи (Graph Hints)
- Квантовая_суперпозиция (базовый принцип, из которого вытекает запутанность).
- Парадокс_Эйнштейна_Подольского_Розена (критика полноты квантовой механики).
- Неравенства_Белла (экспериментальное подтверждение нелокальности).
- Квантовый_компьютер (практическое применение запутанных кубитов).

## Противоречия/Нюансы (Caveats)
- Запутанность не позволяет передавать информацию быстрее света.
- Состояние запутанности крайне хрупко и разрушается при взаимодействии с окружением (декогеренция).
```

## 🔮 Следующие шаги развития MVP

1.  **Обработка дампа**: Вместо URL подавать на вход скрипту `.xml.bz2` файл дампа Википедии и парсить его потоково.
2.  **Skill Generator**: Научить скрипт находить в статьях категорию «Алгоритмы» и генерировать не просто `.ai.md`, а `.skill.md` (с кодом на Python/JS внутри).
3.  **Векторная БД**: После создания всех `.ai.md`, проиндексировать секции `TL;DR` через `sentence-transformers` для быстрого поиска по графу.

Это полностью рабочая спецификация. Можем начать с запуска на одной статье прямо сейчас, если есть API ключ.