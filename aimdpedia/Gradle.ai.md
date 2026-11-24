---
title: "Gradle"
skill: [java, build-tools, gradle]
level: intermediate
prerequisites: [Java]
embeddings:
  chunk_strategy: semantic-paragraphs
  max_tokens: 512
---

## TL;DR (Core Vector)
Gradle — современный инструмент сборки на основе JVM, использующий Groovy/Kotlin DSL вместо XML. Поддерживает инкрементальные сборки, build cache и кросс-проектные зависимости. Стандарт для Android и многих Spring Boot проектов.

## Определение (Definition)
Gradle — система автоматизации сборки, использующая граф задач (task graph) и declarative DSL (Groovy/Kotlin) для описания зависимостей, плагинов и этапов сборки Java/Kotlin/Android/C++ проектов.

## Ключевые факты (Facts)
- Gradle Inc. (2007), сейчас Gradle Enterprise
- build.gradle (Groovy) или build.gradle.kts (Kotlin DSL)
- settings.gradle — определение мульти-модульного проекта
- Gradle Wrapper: gradlew — гарантированная версия Gradle без установки
- Incremental builds: только изменённые таски перекомпилируются
- Build Cache: переиспользование результатов между сборками
- Dependency management: Maven/Ivy репозитории + каталог версий (version catalog)
- Gradle 8+ (2025): Java 17+ required, configuration cache

## Ядро для ИИ (Embedding Target)
Ключевые таски: assemble → build → check → test. Gradle строит Directed Acyclic Graph (DAG) задач и выполняет только необходимые.

```kotlin
// build.gradle.kts
plugins {
    java
    id("org.springframework.boot") version "3.4.0"
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

tasks.test {
    useJUnitPlatform()
}
```

Configuration Cache (gradle 8+): --configuration-cache — кэширует граф конфигурации, ускоряя запуск на 70-90%.

Version Catalogs (libs.versions.toml): централизованное управление зависимостями в мульти-модульных проектах.

## Применение / Практическое использование
- Android: единственный официально поддерживаемый инструмент сборки
- Spring Boot: spring-boot-gradle-plugin — auto-configuration
- Kotlin Multiplatform: KMP проекты только на Gradle
- CI/CD: Gradle Enterprise — дебаг, profiling, prediction
- Composite Builds: тестирование нескольких проектов одновременно

## Связи (Graph Hints)
- ТРЕБУЕТСЯ: [[Java]]
- РОДИТЕЛЬ: [[Сборка_проектов]]
- СМЕЖНЫЕ: [[Maven]], [[Spring_Boot]], [[Android]], [[Kotlin]]

## Противоречия/Нюансы (Caveats)
- Gradle сложнее Maven: кривая обучения круче (DSL, task graph)
- Configuration cache несовместим со старыми плагинами
- Daemon: gradle daemon потребляет RAM постоянно (отключить: --no-daemon)
- Kotlin DSL строже Groovy: типы проверяются, меньше runtime ошибок
