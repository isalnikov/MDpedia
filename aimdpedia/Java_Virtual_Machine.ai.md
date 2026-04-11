---
title: "Java Virtual Machine"
skill: [jvm, java, runtime]
level: advanced
prerequisites: [Java, Компилятор]
embeddings:
  chunk_strategy: semantic-paragraphs
  max_tokens: 512
---

## TL;DR (Core Vector)
JVM — виртуальная машина для выполнения байт-кода Java. Обеспечивает кроссплатформенность, автоматическое управление памятью (GC), JIT-компиляцию и безопасность через sandbox. Работает не только с Java, но и Kotlin, Scala, Groovy.

## Определение (Definition)
Java Virtual Machine — абстрактная вычислительная машина, выполняющая байт-код Java (.class файлы), обеспечивающая независимость от платформы, управление памятью и оптимизацию выполнения через JIT/AOT.

## Ключевые факты (Facts)
- Спецификация JVM описывает набор инструкций, стек, кучу, области методов
- Реализации: HotSpot (Oracle/OpenJDK), GraalVM, Eclipse OpenJ9, Azul Zing
- Память JVM: Heap (Eden, Survivor, Old Gen), Metaspace, Stack, Code Cache
- GC алгоритмы: Serial, Parallel, CMS (deprecated), G1 (default), ZGC (low-latency), Shenandoah
- JIT-компиляция: C1 (client, быстрая компиляция), C2 (server, агрессивная оптимизация)
- ClassLoader: Bootstrap → Extension → Application → Custom (иерархия делегирования)
- GraalVM: AOT-компиляция → Native Image, полиглот (Java + JavaScript + Python + Ruby)

## Ядро для ИИ (Embedding Target)
JVM-архитектура:
- Program Counter (PC) register — адрес текущей инструкции
- JVM Stack — фреймы вызовов методов (локальные переменные, операнды)
- Heap — общая область для всех объектов, управляется GC
- Metaspace — метаданные классов (замена PermGen с Java 8)

JIT-компиляция: код сначала интерпретируется. «Горячие» методы (частые вызовы) компилируются C1/C2 в машинный код. Inlining, escape analysis, dead code elimination — ключевые оптимизации.

Garbage Collection:
- G1 (Garbage-First): разделяет heap на регионы, предсказуемые паузы (~200ms target)
- ZGC: <1ms паузы, throughput ~15% overhead, масштабируется до терабайт
- Shenandoah: аналог ZGC от Red Hat, concurrent compaction

## Применение / Практическое использование
- Настройка GC: -XX:+UseZGC -Xmx16g (low-latency сервисы)
- Диагностика: jcmd, jmap, jstack, VisualVM, Java Flight Recorder
- GraalVM Native Image: компиляция в бинарник — startup <100ms, RAM <50MB
- Мультитенантность: -XX:MaxRAMPercentage=75.0 для контейнеров (Docker/K8s)

## Связи (Graph Hints)
- ТРЕБУЕТСЯ: [[Java]], [[Компилятор]]
- РОДИТЕЛЬ: [[Виртуальная_машина]]
- СМЕЖНЫЕ: [[GraalVM]], [[Kotlin]], [[Scala]]

## Противоречия/Нюансы (Caveats)
- JVM «ест много памяти» — контейнеры без настроек -XX:MaxRAMPercentage оверкоммитят
- Native Image: не вся рефлексия работает, динамические прокси ограничены
- GC tuning — не серебро: throughput vs latency tradeoff
- «Утечки памяти в Java» — возможны через classloader leaks, ThreadLocal, static collections
