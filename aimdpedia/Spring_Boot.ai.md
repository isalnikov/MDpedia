---
title: "Spring Boot"
skill: [spring-boot, java, microservices]
level: intermediate
prerequisites: [Java, Spring_Framework]
embeddings:
  chunk_strategy: semantic-paragraphs
  max_tokens: 512
---

## TL;DR (Core Vector)
Spring Boot — надстройка над Spring Framework для быстрого создания production-ready приложений с автоконфигурацией, встроенным сервером (Tomcat/Undertow) и Spring Boot Actuator для мониторинга. Устраняет boilerplate-конфигурацию Spring.

## Определение (Definition)
Spring Boot — opinionated фреймворк, автоматизирующий конфигурацию Spring-приложений через auto-configuration, embedded серверы и starter-зависимости. Позволяет запустить приложение одной командой.

## Ключевые факты (Facts)
- Spring Boot 4.x (2025): требует Java 21+, поддерживает Spring Framework 7
- @SpringBootApplication = @Configuration + @EnableAutoConfiguration + @ComponentScan
- Auto-configuration: classpath scanning → автоматические бины (DataSource, JPA, MVC, Security)
- Starter POMs: spring-boot-starter-web, -data-jpa, -security, -test, -actuator
- Embedded серверы: Tomcat (default), Jetty, Undertow
- application.properties / application.yml — внешняя конфигурация
- Actuator: /actuator/health, /metrics, /env, /beans — мониторинг production
- Spring Boot DevTools: auto-restart, LiveReload для разработки

## Ядро для ИИ (Embedding Target)
Принцип работы Auto-configuration:
1. spring.factories / org.springframework.boot.autoconfigure.AutoConfiguration.imports → список авто-конфигов
2. @ConditionalOnClass, @ConditionalOnMissingBean — условия активации
3. Пример: если H2 на classpath и нет DataSource бина → создаётся H2 DataSource

Профили: @Profile("dev"), application-dev.yml, spring.profiles.active=dev — разделение конфигурации по окружениям.

Структура проекта:
```
src/main/java/
  Application.java          // @SpringBootApplication
  controller/               // REST endpoints
  service/                  // бизнес-логика
  repository/               // доступ к данным
  config/                   // кастомная конфигурация
src/main/resources/
  application.yml           # конфигурация
  application-dev.yml       # dev профиль
```

Production фичи:
- Graceful shutdown: server.shutdown=graceful
- Health checks: /actuator/health — liveness/readiness для K8s
- Metrics: Micrometer + Prometheus/Grafana
- Externalized config: env vars, CLI args, config server

## Применение / Практическое использование
- REST API: spring-boot-starter-web → @RestController за 5 минут
- Микросервисы: Spring Boot + Spring Cloud (Eureka, Config, Gateway)
- Batch jobs: @Scheduled, Spring Batch
- Reactive: spring-boot-starter-webflux (WebFlux, Project Reactor)
- Native: GraalVM Native Image компиляция → бинарник <50MB

## Связи (Graph Hints)
- ТРЕБУЕТСЯ: [[Java]], [[Spring_Framework]]
- РОДИТЕЛЬ: [[Spring_Framework]]
- СМЕЖНЫЕ: [[Микросервисы]], [[REST]], [[Docker]], [[Kubernetes]]

## Противоречия/Нюансы (Caveats)
- Auto-configuration «магия» — сложно понять почему бин не создался (debug: true в application.yml помогает)
- Memory footprint: минимальный Spring Boot ~200-400MB RAM (GraalVM Native Image решает)
- Startup time: 3-10 сек (Spring Boot 3.x + AOT + GraalVM → <1 сек)
- «Fat JAR»: все зависимости внутри — большой файл, но самодостаточный
