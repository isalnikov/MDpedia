#!/usr/bin/env python3
"""Build MDpedia corpus from existing project files only (verbatim excerpts)."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MDPEDIA = ROOT / "mdpedia"
CORPUS = ROOT / "corpus"
EMBED_MAX_LINES = 120
EMBED_MAX_CHARS = 24_000

CONCEPTS = [
    ("peaa-patterns", ROOT / "library/peaa-patterns.md", ["peaa", "domain", "enterprise"]),
    ("ddia-patterns", ROOT / "library/ddia-patterns.md", ["ddia", "data", "distributed"]),
    ("eip-patterns", ROOT / "library/eip-patterns.md", ["eip", "integration", "messaging"]),
    ("api-management-patterns", ROOT / "library/api-management-patterns.md", ["api", "governance"]),
    ("spring-boot-decisions", ROOT / "library/spring-boot-decisions.md", ["spring-boot", "java"]),
    ("sql-fundamentals", ROOT / "library/sql/sql-fundamentals.md", ["sql", "mysql", "ddl"]),
    ("sql-recipes", ROOT / "library/sql/sql-recipes-and-queries.md", ["sql", "queries"]),
    ("mysql-performance", ROOT / "library/sql/mysql-performance-patterns.md", ["mysql", "performance"]),
    ("sql-transactions-ha", ROOT / "library/sql/sql-transactions-and-ha.md", ["sql", "transactions", "ha"]),
]

SKILLS = [
    ("system-design-patterns", ROOT / ".cursor/skills/system-design-patterns"),
    ("spring-boot-expert", ROOT / ".cursor/skills/spring-boot-expert"),
    ("sql-expert", ROOT / ".cursor/skills/sql-expert"),
]

BOOKS_MD = sorted((ROOT / "books-md").glob("*.md")) if (ROOT / "books-md").exists() else []
SQL_BOOKS_MD = (
    sorted((ROOT / "sql/books-md").glob("*.md")) if (ROOT / "sql/books-md").exists() else []
)

LEVEL_BY_NAME = {
    "peaa-patterns": "intermediate",
    "ddia-patterns": "advanced",
    "eip-patterns": "intermediate",
    "api-management-patterns": "intermediate",
    "spring-boot-decisions": "intermediate",
    "sql-fundamentals": "beginner",
    "sql-recipes": "intermediate",
    "mysql-performance": "advanced",
    "sql-transactions-ha": "advanced",
}


def read_head(lines: list[str], max_lines: int, max_chars: int) -> str:
    chunk: list[str] = []
    total = 0
    for line in lines[:max_lines]:
        if total + len(line) > max_chars:
            break
        chunk.append(line)
        total += len(line) + 1
    return "".join(chunk).rstrip() + "\n"


def yaml_quote(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def write_concept(slug: str, src: Path, skills: list[str]) -> Path:
    text = src.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    title_m = re.search(r"^#\s+(.+)", text, re.M)
    title = title_m.group(1).strip() if title_m else slug
    level = LEVEL_BY_NAME.get(slug, "intermediate")
    excerpt = read_head(lines, EMBED_MAX_LINES, EMBED_MAX_CHARS)
    rel_src = src.relative_to(ROOT)
    out = MDPEDIA / "content/concepts" / f"{slug}.md"
    body = f"""---
title: {yaml_quote(title)}
skill: {json.dumps(skills, ensure_ascii=False)}
level: {level}
source: {yaml_quote(str(rel_src))}
embeddings:
  chunk_strategy: headings
  max_tokens: 2048
relations:
  parent: corpus/AGENT-INDEX.md
---

# {title}

## Источник (полный текст)

`{rel_src}`

## Ядро для ИИ (Embedding Target)

> Дословный фрагмент из `{rel_src}` (первые {EMBED_MAX_LINES} строк, не более {EMBED_MAX_CHARS} символов).

{excerpt}

## Навигация

- [[corpus/AGENT-INDEX.md|Индекс агента]]
- [[library/INDEX.md|Библиотека (люди)]]
"""
    out.write_text(body, encoding="utf-8")
    aim = MDPEDIA / "aimdpedia" / f"{slug}.ai.md"
    aim.write_text(
        f"---\ntitle: {yaml_quote(title)}\nsource: {yaml_quote(str(rel_src))}\n---\n\n"
        f"## TL;DR (Core Vector)\n\nСм. полный каталог: `{rel_src}`.\n\n"
        f"## Ядро для ИИ (Embedding Target)\n\n{excerpt}\n",
        encoding="utf-8",
    )
    return out


def copy_skills() -> list[dict]:
    registry = []
    for name, skill_dir in SKILLS:
        skill_md = skill_dir / "SKILL.md"
        ref_md = skill_dir / "reference.md"
        dest = MDPEDIA / "content/skills" / f"{name}.skill.md"
        if skill_md.exists():
            shutil.copy2(skill_md, dest)
        if ref_md.exists():
            appendix = dest.read_text(encoding="utf-8") + "\n\n---\n\n"
            appendix += ref_md.read_text(encoding="utf-8")
            dest.write_text(appendix, encoding="utf-8")
        registry.append(
            {
                "name": name,
                "file": str(dest.relative_to(ROOT)),
                "cursor_skill": str(skill_dir.relative_to(ROOT)),
                "type": "skill",
            }
        )
    return registry


def build_graph(concept_files: list[tuple[str, Path]]) -> dict:
    nodes = {}
    edges = []
    for slug, path in concept_files:
        nodes[slug] = {
            "file": str(path.relative_to(ROOT)),
            "title": slug,
            "type": "concept",
        }
    skill_edges = [
        ("system-design-patterns", "peaa-patterns", "uses"),
        ("system-design-patterns", "ddia-patterns", "uses"),
        ("system-design-patterns", "eip-patterns", "uses"),
        ("system-design-patterns", "api-management-patterns", "uses"),
        ("spring-boot-expert", "spring-boot-decisions", "uses"),
        ("spring-boot-expert", "system-design-patterns", "relates"),
        ("peaa-patterns", "ddia-patterns", "relates"),
        ("peaa-patterns", "eip-patterns", "relates"),
        ("ddia-patterns", "eip-patterns", "relates"),
        ("spring-boot-decisions", "peaa-patterns", "relates"),
        ("spring-boot-decisions", "eip-patterns", "relates"),
        ("spring-boot-decisions", "api-management-patterns", "relates"),
        ("sql-expert", "sql-fundamentals", "uses"),
        ("sql-expert", "sql-recipes", "uses"),
        ("sql-expert", "mysql-performance", "uses"),
        ("sql-expert", "sql-transactions-ha", "uses"),
        ("sql-expert", "ddia-patterns", "relates"),
        ("sql-expert", "spring-boot-decisions", "relates"),
        ("mysql-performance", "sql-transactions-ha", "relates"),
        ("sql-recipes", "sql-fundamentals", "requires"),
    ]
    for a, b, rel in skill_edges:
        if a not in nodes and a in {s[0] for s in SKILLS}:
            nodes[a] = {
                "file": f"mdpedia/content/skills/{a}.skill.md",
                "type": "skill",
            }
        if a in nodes and b in nodes:
            edges.append({"from": a, "to": b, "relation": rel})

    agent_flow = [
        "Если задача = архитектура / паттерны / микросервисы: corpus/AGENT-INDEX.md → skill:system-design-patterns → concepts по INDEX.md",
        "Если задача = Spring Boot стек / starters / тесты: corpus/AGENT-INDEX.md → skill:spring-boot-expert → spring-boot-decisions",
        "Если нужна первичка: books-md/*.md (архитектура); sql/books-md/*.md (SQL, локальные PDF)",
        "Если задача = SQL / MySQL: corpus/AGENT-INDEX.md → skill:sql-expert → library/sql/ + sql/prompts/",
    ]
    return {"nodes": nodes, "edges": edges, "agent_flow": agent_flow}


def write_agent_index() -> None:
    index_md = (ROOT / "library/INDEX.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    ai_hints = (MDPEDIA / "meta/ai-hints.md").read_text(encoding="utf-8")
    tutorial = MDPEDIA / "content/tutorials/AGENT-READORDER.md"
    tutorial.write_text(
        "---\ntitle: Порядок чтения для агента\nlevel: beginner\n---\n\n"
        + "# Порядок чтения для агента\n\n"
        + "Источник: `library/INDEX.md` и `README.md` (дословно).\n\n"
        + "## library/INDEX.md\n\n"
        + index_md
        + "\n\n## README.md\n\n"
        + readme
        + "\n",
        encoding="utf-8",
    )
    CORPUS.mkdir(exist_ok=True)
    manifest = {
        "root": str(ROOT),
        "entry_points": [
            "corpus/AGENT-INDEX.md",
            "corpus/CONNECT.md",
            "mdpedia/meta/ai-hints.md",
            "mdpedia/meta/distiller_prompt.txt",
            "mdpedia/graph/links.json",
            "library/INDEX.md",
            "library/INDEX.html",
        ],
        "skills": [f"mdpedia/content/skills/{n}.skill.md" for n, _ in SKILLS],
        "concepts": [f"mdpedia/content/concepts/{s[0]}.md" for s in CONCEPTS],
        "books_md": [str(p.relative_to(ROOT)) for p in BOOKS_MD],
        "sql_books_md": [str(p.relative_to(ROOT)) for p in SQL_BOOKS_MD],
        "sql_prompts": [str(p.relative_to(ROOT)) for p in sorted((ROOT / "sql/prompts").glob("*.md"))],
        "sql_library": [str(p.relative_to(ROOT)) for p in sorted((ROOT / "library/sql").glob("*.md"))],
        "cursor_skills": [str((ROOT / ".cursor/skills" / n).relative_to(ROOT)) for n, _ in SKILLS],
    }
    (CORPUS / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    agent_index = CORPUS / "AGENT-INDEX.md"
    agent_index.write_text(
        "---\ntitle: Agent Index\n---\n\n"
        "# Корпус знаний patterns (точка входа для ИИ)\n\n"
        "## Подключение (MDpedia)\n\n"
        + ai_hints
        + "\n\n## MANIFEST\n\n"
        + f"См. `corpus/MANIFEST.json`.\n\n"
        + "## Индекс библиотеки\n\n"
        + index_md
        + "\n\n## Репозиторий\n\n"
        + readme
        + "\n",
        encoding="utf-8",
    )


def write_context_rules() -> None:
    index = (ROOT / "library/INDEX.md").read_text(encoding="utf-8")
    chains = re.search(
        r"## Типовые цепочки решений(.*)",
        index,
        re.S,
    )
    block = chains.group(1) if chains else ""
    (MDPEDIA / "context_rules/design-and-spring.graph.md").write_text(
        "---\ntitle: Context routing\n---\n\n"
        "# Context routing (из library/INDEX.md)\n\n"
        + block.strip()
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    concept_paths = []
    for slug, src, tags in CONCEPTS:
        if not src.exists():
            continue
        concept_paths.append((slug, write_concept(slug, src, tags)))
    skills_reg = copy_skills()
    graph = build_graph(concept_paths)
    (MDPEDIA / "graph/links.json").write_text(
        json.dumps(graph, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (MDPEDIA / "graph/skills.json").write_text(
        json.dumps({"skills": skills_reg}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_agent_index()
    write_context_rules()
    print("Corpus built:", CORPUS / "AGENT-INDEX.md")


if __name__ == "__main__":
    main()