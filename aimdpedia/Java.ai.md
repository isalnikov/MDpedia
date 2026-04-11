---
title: "Java"
skill: [java, programming, oop]
level: intermediate
prerequisites: [ООП, Язык_программирования]
embeddings:
  chunk_strategy: semantic-paragraphs
  max_tokens: 512
---

## TL;DR (Core Vector)
Java — объектно-ориентированный язык программирования со статической типизацией, работающий на JVM. Принцип «Write Once, Run Anywhere». Версия 25 (2025) включает паттерн-матчинг, виртуальные потоки, записи и управляемые внешние функции.

## Определение (Definition)
Java — строго типизированный, объектно-ориентированный язык программирования общего назначения, компилируемый в байт-код для Java Virtual Machine (JVM), обеспечивающий кроссплатформенность.

## Ключевые факты (Facts)
- Создан Джеймсом Гослингом (Sun Microsystems, 1995), сейчас Oracle
- JVM + JIT-компиляция — байт-код компилируется в машинный на лету
- Автоматическое управление памятью: Garbage Collector (G1, ZGC, Shenandoah)
- Java 25 (2025): виртуальные потоки (Project Loom), Pattern Matching, Records, Sealed Classes
- Экосистема: Maven/Gradle, Spring Boot, Jakarta EE, JUnit
- Память: Heap (Young/Old Gen), Metaspace, Stack — настраиваемые флаги -Xmx, -Xms
- Collection Framework: List, Set, Map, Queue — иерархия интерфейсов и реализаций

## Ядро для ИИ (Embedding Target)
Java использует статическую типизацию и строгую проверку на этапе компиляции. Все данные — объекты (кроме примитивов: int, long, double, boolean и др.).

JVM-архитектура: Java-код → javac → .class (байт-код) → JVM (interpretation + JIT via C1/C2 compiler → машинный код). Граб-коллектор (G1GC по умолчанию) автоматически управляет памятью.

Java 21+ ключевые фичи:
- Virtual Threads (JEP 444) — лёгкие потоки, millions concurrent
- Record Patterns (JEP 440) — деструктуризация записей
- Pattern Matching for switch (JEP 441)
- Sequenced Collections (JEP 431) — упорядоченные коллекции
- Scoped Values (incubator) — иммутабельные переменные для виртуальных потоков

## Применение / Практическое использование
- Enterprise: Spring Boot, Jakarta EE — бэкенд корпоративных систем
- Android: основная платформа (до Kotlin)
- Big Data: Apache Hadoop, Spark, Kafka, Flink
- Финансы: банковские системы, trading platforms
- Микросервисы: Quarkus, Micronaut, Helidon

## Связи (Graph Hints)
- ТРЕБУЕТСЯ: [[ООП]], [[Java_Virtual_Machine]]
- РОДИТЕЛЬ: [[Язык_программирования]]
- СМЕЖНЫЕ: [[Spring_Framework]], [[Spring_Boot]], [[Maven]], [[Gradle]], [[Микросервисы]]

## Противоречия/Нюансы (Caveats)
- «Java медленная» — устаревший миф: JIT + AOT (GraalVM) сопоставимы с C++
- Verbosity: Java многословнее Python/Kotlin (компенсируется Records, var, Pattern Matching)
- JVM startup время: 1-3 сек (GraalVM Native Image решает — <100ms)
- Java != JavaScript — совершенно разные языки
