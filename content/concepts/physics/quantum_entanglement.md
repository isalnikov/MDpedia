---
title: "Квантовая запутанность"
skill: [quantum-physics, cryptography]
level: advanced
prerequisites: [quantum-superposition, linear-algebra-basics]
embeddings:
  chunk_strategy: semantic-paragraphs
  max_tokens: 512
relations:
  requires: [quantum_superposition]
  parent: quantum_mechanics
  contradicts: [local_realism]
---

# Тема: Квантовая запутанность

## Определение
Явление, при котором квантовые состояния двух частиц оказываются
взаимозависимыми независимо от расстояния между ними.

## Ядро для ИИ (Embedding Target)
Запутанность не передаёт информацию быстрее света. Измерение одной
частицы мгновенно определяет состояние другой. Применяется в протоколе
E91 для квантовой криптографии и в квантовых вычислениях.

Ключевые формулы:
- Состояние Белла: |Φ+⟩ = (|00⟩ + |11⟩) / √2
- Неравенство CHSH: |S| ≤ 2 (классика), |S| ≤ 2√2 (квант)

## Примеры использования
- Квантовая телепортация состояний
- Протокол E91 для защищённой связи
- Квантовые вычисления (纠错 коды)

## Связи (Граф)
- ТРЕБУЕТСЯ: [[quantum_superposition]]
- РОДИТЕЛЬ: [[quantum_mechanics]]
- ПРОТИВОРЕЧИТ: [[local_realism]]

## Скиллы (Вызов)
- `execute_simulation.skill.md` — симуляция схемы Белла
