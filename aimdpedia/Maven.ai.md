---
title: "Maven"
skill: [java, build-tools, maven]
level: intermediate
prerequisites: [Java]
embeddings:
  chunk_strategy: semantic-paragraphs
  max_tokens: 512
---

## TL;DR (Core Vector)
Maven — инструмент сборки и управления зависимостями для Java-проектов. Использует pom.xml для декларативного описания проекта, зависимостей, плагинов и этапов сборки. Convention over configuration — стандартная структура каталогов.

## Определение (Definition)
Apache Maven — система управления проектами на основе POM (Project Object Model), автоматизирующая сборку, управление зависимостями, тестирование и развёртывание через центральный репозиторий и систему плагинов.

## Ключевые факты (Facts)
- Apache Software Foundation, 2004
- pom.xml — Project Object Model: groupId, artifactId, version (GAV координаты)
- Жизненный цикл: validate → compile → test → package → verify → install → deploy
- Зависимости: Maven Central Repository (repo.maven.apache.org)
- Scope зависимостей: compile, provided, runtime, test, system
- Плагины: maven-compiler-plugin, maven-surefire-plugin, maven-jar-plugin
- Multi-module: parent POM → child modules (общие зависимости, версии)
- mvn clean install — полная сборка с установкой в локальный репозиторий (~/.m2)

## Ядро для ИИ (Embedding Target)
POM структура:
```xml
<project>
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>my-app</artifactId>
  <version>1.0-SNAPSHOT</version>
  <packaging>jar</packaging>

  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
      <version>3.4.0</version>
    </dependency>
  </dependencies>
</project>
```

Dependency resolution: транзитивные зависимости — если A зависит от B, а B от C, Maven разрешит весь граф. Conflict resolution: «nearest definition wins» (ближайшая в графе побеждает). <dependencyManagement> — централизованное управление версиями.

Profiles: mvn clean install -Pprod — активация профилей для разных окружений (dev/test/prod).

## Применение / Практическое использование
- Java Enterprise: стандарт для enterprise-проектов
- Spring Boot: spring-boot-starter-parent — родительский POM
- CI/CD: Jenkins, GitHub Actions — mvn clean verify
- Site generation: mvn site — документация проекта
- Release: mvn release:prepare && mvn release:perform

## Связи (Graph Hints)
- ТРЕБУЕТСЯ: [[Java]]
- РОДИТЕЛЬ: [[Сборка_проектов]]
- СМЕЖНЫЕ: [[Gradle]], [[Spring_Boot]], [[CI/CD]]

## Противоречия/Нюансы (Caveats)
- Maven медленнее Gradle для больших проектов (инкрементальная сборка)
- XML verbosity: pom.xml многословнее build.gradle.kts
- «Dependency Hell»: конфликт версий транзитивных зависимостей (mvn dependency:tree помогает)
- SNAPSHOT зависимости: нестабильные, кэшируются — mvn -U force update
