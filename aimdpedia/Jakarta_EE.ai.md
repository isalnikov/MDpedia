---
title: "Jakarta EE"
skill: [java, enterprise, jakarta-ee]
level: advanced
prerequisites: [Java, Servlet]
embeddings:
  chunk_strategy: semantic-paragraphs
  max_tokens: 512
---

## TL;DR (Core Vector)
Jakarta EE — спецификация enterprise-приложений на Java (наследник Java EE после передачи Oracle → Eclipse Foundation). Включает Servlet, JPA, CDI, JAX-RS, EJB, WebSocket, JSON-P/B. Реализации: Eclipse GlassFish, WildFly, OpenLiberty.

## Определение (Definition)
Jakarta EE — набор спецификаций для enterprise-приложений на Java, определяющий стандартные API для веб-сервисов, персистентности, безопасности, сообщений и транзакций в управляемом контейнером окружении.

## Ключевые факты (Facts)
- Java EE → Jakarta EE (2019, Eclipse Foundation)
- Пакетное пространство: javax.* → jakarta.* (breaking change, Jakarta EE 9+)
- Jakarta EE 11 (2025): Java 21+, CDI 4.1, JPA 3.2, REST 3.2
- Спецификации: Servlet, JAX-RS (REST), JPA, CDI, EJB, WebSocket, JSON-B, Validation
- Application Servers: GlassFish (reference), WildFly, OpenLiberty, Payara
- Web Profile: подмножество для веб-приложений (Servlet + JAX-RS + CDI + JPA)
- Full Profile: все спецификации включая EJB, JMS, Batch

## Ядро для ИИ (Embedding Target)
Jakarta EE определяет контракт между приложением и сервером приложений (App Server). Контейнер управляет жизненным циклом компонентов, DI, транзакциями, безопасностью.

Ключевые API:
- Servlet (6.1): HTTP request/response handling, фильтры, listeners
- JAX-RS (REST 3.2): @Path, @GET, @POST — RESTful веб-сервисы
- JPA (3.2): @Entity, EntityManager — ORM персистентность
- CDI (4.1): @Inject, @Named — Dependency Injection
- Bean Validation (3.1): @NotNull, @Size, @Email — валидация
- JSON-B / JSON-P: сериализация/десериализация JSON

MicroProfile: подпроект для микросервисов — Health, Metrics, OpenAPI, Fault Tolerance, Config — поверх Jakarta EE.

## Применение / Практическое использование
- Enterprise: банки, страховые, государственные системы
- MicroProfile: лёгкие микросервисы (Quarkus, Helidon, OpenLiberty)
- Cloud Native: Jakarta EE на Kubernetes (Eclipse MicroProfile)
- Migration: Java EE → Jakarta EE (javax → jakarta namespace)

## Связи (Graph Hints)
- ТРЕБУЕТСЯ: [[Java]], [[Servlet]]
- РОДИТЕЛЬ: [[Enterprise_Java]]
- СМЕЖНЫЕ: [[Spring_Framework]], [[Микросервисы]], [[JPA]]

## Противоречия/Нюансы (Caveats)
- javax → jakarta migration: breaking change, все импорты нужно менять
- Jakarta EE «умер» — миф: MicroProfile и Quarkus/Helidon развивают
- App Server vs Spring: Jakarta EE — стандарт, Spring — фреймворк (разные подходы)
- EJB устарел — CDI beans + JAX-RS современный стандарт
