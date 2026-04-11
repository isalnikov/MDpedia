# MDpedia

> **AI优先的知识库** — Markdown + 图（Graph） + 技能（Skills）

为AI代理优化的知识库，而非仅供人类阅读。

## 🔥 理念

传统维基百科包含噪音、冗长文本且缺乏明确的关联——这些都阻碍大语言模型（LLM）高效利用知识。

**MDpedia 通过以下方式解决：**

| 组件 | 用途 |
|------|------|
| **Markdown 文件** | 纯净的事实，无HTML噪音，适合分块处理 |
| **知识图谱** | 明确的依赖关系："先读这个，再读那个" |
| **技能（Skills）** | 可执行指令，赋予AI行动能力 |

## 📁 项目结构

```
mdpedia/
├── content/
│   ├── skills/        # 可执行指令（技能）
│   ├── concepts/      # 事实知识库
│   └── tutorials/     # 分步教程
├── graph/             # 知识图谱和技能注册表
├── meta/              # 验证模式
├── context_rules/     # 上下文组装规则
└── scripts/           # CLI 工具
```

## 📊 当前内容（20篇文章）

### 🔬 科学（4篇）
量子纠缠、相对论、DNA、黑洞

### 🤖 AI/ML（3篇）
人工智能、机器学习、神经网络

### 💻 通用技术（3篇）
Python、区块链、物联网

### ☕ Java 25+ / Spring Boot 4+ 生态（10篇）
Java、JVM、Spring Framework、Spring Boot、Maven、Gradle、Jakarta EE、Hibernate、JUnit、微服务

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/isalnikov/MDpedia.git
cd MDpedia

# 安装依赖
pip install trafilatura openai

# 运行 Wikipedia → MDpedia 转换器（需要 Ollama 或 OpenAI API）
python3 wiki2mdpedia.py --model qwen2.5:7b --base-url http://localhost:11434/v1 --api-key ollama
```

## 🛠️ 转换流水线

```
Wikipedia URL → trafilatura（清理提取）→ LLM 蒸馏 → .ai.md 文件 → graph.json
```

| 步骤 | 工具 | 用途 |
|------|------|------|
| 1. 提取 | `trafilatura` | 从HTML中清理文本，去除噪音 |
| 2. 蒸馏 | LLM（Qwen/GPT）| 转换为AI-Markdown格式 |
| 3. 构建图谱 | `wiki2mdpedia.py` | 提取 `[[链接]]` → `graph.json` |

## 📖 文档

- [**IMPLEMENTATION_PLAN.md**](./IMPLEMENTATION_PLAN.md) — 详细实现计划
- [**meta/schema.yaml**](./meta/schema.yaml) — frontmatter 规范
- [**meta/ai-hints.md**](./meta/ai-hints.md) — 解析器指令
- [**distiller_prompt.txt**](./distiller_prompt.txt) — LLM 转换提示词

## 🎯 应用场景

- **AI 代理** — Cursor、Copilot、Claude 使用 MDpedia 作为知识库
- **RAG 流水线** — 基于图谱的上下文检索，替代向量相似度
- **企业** — 带项目依赖图谱的私有公司维基
- **教育** — 通过前置依赖图谱从入门导航到进阶

## 📄 示例：AI-Markdown 文件

```markdown
---
title: "量子纠缠"
skill: [quantum-physics, cryptography]
level: advanced
prerequisites: [quantum-superposition]
---

## TL;DR（核心向量）
量子纠缠——粒子间无论距离多远都相互依赖的现象。

## 定义
多粒子量子系统的不可分解态。

## 关键事实
- 贝尔态：|Φ+⟩ = (|00⟩ + |11⟩) / √2
- 不超光速传递信息
- 用于E91量子加密协议

## 图谱链接
- 需要：[[quantum_superposition]]
- 父主题：[[quantum_mechanics]]
```

## 🌍 语言

- 🇷🇺 [Русский](README.md)
- 🇬🇧 [English](README_EN.md)
- 🇨🇳 [中文](README_ZH.md)

## 🤝 贡献

贡献指南正在制定中，敬请期待。

## 📄 许可证

MIT
