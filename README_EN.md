# MDpedia

> **AI-first knowledge base** — Markdown + Graph + Skills

Knowledge optimized for AI agents, not just human reading.

## 🔥 Concept

Traditional Wikipedia contains noise, long texts, and lacks explicit connections — all of which prevent LLMs from efficiently using knowledge.

**MDpedia solves this through:**

| Component | Purpose |
|-----------|---------|
| **Markdown files** | Clean facts without HTML noise, chunk-friendly |
| **Knowledge Graph** | Explicit dependencies: "read THIS before that" |
| **Skills** | Executable instructions giving AI agency |

## 📁 Structure

```
mdpedia/
├── content/
│   ├── skills/        # Executable instructions
│   ├── concepts/      # Knowledge base
│   └── tutorials/     # Step-by-step guides
├── graph/             # Knowledge graph and skills registry
├── meta/              # Validation schemas
├── context_rules/     # Context assembly rules
└── scripts/           # CLI tools
```

## 📊 Current Content (20 Articles)

### Science (4)
Quantum Entanglement, Theory of Relativity, DNA, Black Hole

### AI/ML (3)
Artificial Intelligence, Machine Learning, Neural Network

### General Tech (3)
Python, Blockchain, Internet of Things

### Java 25+ / Spring Boot 4+ Ecosystem (10)
Java, JVM, Spring Framework, Spring Boot, Maven, Gradle, Jakarta EE, Hibernate, JUnit, Microservices

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/isalnikov/MDpedia.git
cd MDpedia

# Install dependencies
pip install trafilatura openai

# Run Wikipedia → MDpedia converter (requires Ollama or OpenAI API)
python3 wiki2mdpedia.py --model qwen2.5:7b --base-url http://localhost:11434/v1 --api-key ollama
```

## 🛠️ Pipeline

```
Wikipedia URL → trafilatura (clean extraction) → LLM distillation → .ai.md file → graph.json
```

| Step | Tool | Purpose |
|------|------|---------|
| 1. Extract | `trafilatura` | Clean text from HTML, remove noise |
| 2. Distill | LLM (Qwen/GPT) | Convert to AI-Markdown format |
| 3. Build Graph | `wiki2mdpedia.py` | Extract `[[links]]` → `graph.json` |

## 📖 Documentation

- [**IMPLEMENTATION_PLAN.md**](./IMPLEMENTATION_PLAN.md) — detailed implementation plan
- [**meta/schema.yaml**](./meta/schema.yaml) — frontmatter specification
- [**meta/ai-hints.md**](./meta/ai-hints.md) — parser instructions
- [**distiller_prompt.txt**](./distiller_prompt.txt) — LLM prompt for conversion

## 🎯 Use Cases

- **AI Agents** — Cursor, Copilot, Claude use MDpedia as a knowledge base
- **RAG Pipelines** — graph-based context retrieval instead of vector similarity
- **Enterprise** — private company wiki with project dependency graph
- **Education** — navigation from beginner to advanced via prerequisite graph

## 📄 Example: AI-Markdown File

```markdown
---
title: "Quantum Entanglement"
skill: [quantum-physics, cryptography]
level: advanced
prerequisites: [quantum-superposition]
---

## TL;DR (Core Vector)
Quantum entanglement — phenomenon where particle states become interdependent
regardless of distance.

## Definition
Non-factorizable state of a multi-particle quantum system.

## Key Facts
- Bell state: |Φ+⟩ = (|00⟩ + |11⟩) / √2
- Does not transmit information faster than light
- Used in E91 quantum cryptography protocol

## Graph Links
- REQUIRES: [[quantum_superposition]]
- PARENT: [[quantum_mechanics]]
```

## 🌍 Languages

- 🇷🇺 [Русский](README.md)
- 🇬🇧 [English](README_EN.md)
- 🇨🇳 [中文](README_ZH.md)

## 🤝 Contributing

Contributing guidelines in development. Stay tuned.

## 📄 License

MIT
