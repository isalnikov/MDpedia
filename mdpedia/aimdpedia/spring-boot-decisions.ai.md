---
title: "Spring Boot 3.2.3 — решения и выбор технологий"
source: "library/spring-boot-decisions.md"
---

## TL;DR (Core Vector)

См. полный каталог: `library/spring-boot-decisions.md`.

## Ядро для ИИ (Embedding Target)

---
source: books-md/spring-boot-reference.md
version: "3.2.3"
document: Spring Boot Reference Documentation (TOC: §3–§18, приложения)
purpose: экспертный гид «когда что выбирать» для Spring Boot 3.2.3
language: ru
technical_terms: en
---

# Spring Boot 3.2.3 — решения и выбор технологий

Сжатый operational guide по официальному reference. Ссылки на разделы — по **Table of Contents** PDF ref 3.2.3.

**Базовый принцип:** starter = транзитивные зависимости + auto-configuration. Свой `@Bean` того же типа **вытесняет** (back off) соответствующий auto-config (§6.4.1).

---

## 1. Метаданные

| Поле | Значение |
|------|----------|
| Источник | `books-md/spring-boot-reference.md` |
| Версия | 3.2.3 |
| Java (native) | GraalVM Community 22.3+ (§4.2.2) |
| Servlet containers | Tomcat / Jetty / Undertow (§4.2.1, Table 3 starters) |

---

## 2. Матрица выбора starter’ов (§6.1.5, Tables 1–3)

### 2.1 Обязательная база

| Сценарий | Starter | Что даёт auto-config |
|----------|---------|----------------------|
| Любое приложение | `spring-boot-starter` | Core, logging (Logback по умолчанию), YAML |
| Production readiness | `spring-boot-starter-actuator` | Endpoints, health, metrics hooks (§13) |
| Тесты | `spring-boot-starter-test` | JUnit Jupiter, Mockito, AssertJ, slice annotations (§7.9) |

### 2.2 Web

| Сценарий | Starter | Auto-config (кратко) |
|----------|---------|------------------------|
| REST/MVC, blocking | `spring-boot-starter-web` | Spring MVC, Jackson (`starter-json`), **embedded Tomcat** |
| Reactive HTTP API | `spring-boot-starter-webflux` | WebFlux, codecs, **Reactor Netty** |
| Только WebClient в MVC-приложении | `spring-boot-starter-webflux` *или* dependency `spring-webflux` | ⚠ См. §3 — MVC побеждает при обоих starters |
| WebSocket (servlet) | `spring-boot-starter-websocket` | MVC WebSocket (§8.5) |
| GraphQL API | `spring-boot-starter-graphql` + transport starter | §8.6 |
| SOAP / XML WS | `spring-boot-starter-web-services` | Spring-WS (§11.7) |
| Jersey (JAX-RS) | `spring-boot-starter-jersey` | Альтернатива MVC (§18.5) |
| View (Thymeleaf и др.) | `starter-thymeleaf` / `freemarker` / `mustache` | Шаблонизатор + MVC |

**Swap embedded server:** `spring-boot-starter-jetty` / `undertow` — исключить `starter-tomcat` (Table 3).

### 2.3 Data

| Сценарий | Starter | Auto-config |
|----------|---------|-------------|
| ORM, сложная модель | `spring-boot-starter-data-jpa` | DataSource, JPA/Hibernate, repositories |
| SQL без ORM, «тонкий» DDD | `spring-boot-starter-data-jdbc` | DataSource, `JdbcTemplate`, JDBC repos |
| Raw JDBC / legacy SQL | `spring-boot-starter-jdbc` | HikariCP, `JdbcTemplate`, `JdbcClient` |
| Reactive SQL | `spring-boot-starter-data-r2dbc` | `ConnectionFactory`, R2DBC repos (§9.1.8) |
| Документы | `spring-boot-starter-data-mongodb` | Mongo client, repos |
| Кэш (Redis) | `spring-boot-starter-data-redis` | Lettuce, RedisTemplate |
| LDAP | `spring-boot-starter-data-ldap` | `LdapContextSource`, LDAP repos (§9.2.7) |
| Миграции | `flyway-core` / `liquibase-core` (не отдельный starter) | Flyway/Liquibase auto-config при наличии DataSource (§18.9.5) |
| Типобезопасный SQL | `spring-boot-starter-jooq` | jOOQ (§9.1.7) |

### 2.4 Messaging (§10)

| Сценарий | Starter | Протокол / брокер |
|----------|---------|-------------------|
| RabbitMQ | `spring-boot-starter-amqp` | AMQP, `RabbitTemplate`, `@RabbitListener` |
| ActiveMQ Classic | `spring-boot-starter-activemq` | JMS |
| Artemis | `spring-boot-starter-artemis` | JMS |
| Kafka | `spring-kafka` (+ Boot autoconfig) | `KafkaTemplate`, listeners, streams (§10.3) |
| Pulsar | `spring-boot-starter-pulsar` (+ reactive) | Spring for Apache Pulsar (§10.4) |
| EIP / адаптеры | `spring-boot-starter-integration` | Spring Integration + опц. RSocket (§10.6) |

### 2.5 Security (§8.4)

| Сценарий | Starter | Роль |
|----------|---------|------|
| Базовая защита | `spring-boot-starter-security` | Default `SecurityFilterChain`, generated password dev (§8.4) |
| Login через IdP | `spring-boot-starter-oauth2-client` | OAuth2/OIDC **client** |
| API с JWT | `spring-boot-starter-oauth2-resource-server` | **Resource server**, `jwk-set-uri` / `issuer-uri` |
| Свой authorization server | `spring-boot-starter-oauth2-authorization-server` | Spring Authorization Server |

### 2.6 Cross-cutting

| Сценарий | Starter | Примечание |
|----------|---------|------------|
| Кэш abstraction | `spring-boot-starter-cache` | Провайдер на classpath (Caffeine, JCache, Redis…) (§8.2) |
| Validation | `spring-boot-starter-validation` | Jakarta Bean Validation |
| AOP | `spring-boot-starter-aop` | `@Aspect` |
| Mail | `spring-boot-starter-mail` | JavaMail |
| Batch | `spring-boot-starter-batch` | Jobs, schema init (§18.9.4) |
| Quartz | `spring-boot-starter-quartz` | Scheduler |
| RSocket | `spring-boot-starter-rsocket` | TCP/WS messaging |

### 2.7 Cloud-adjacent (в ref 3.2.3, не Spring Cloud)

| Потребность | В Boot 3.2.3 | Вне ref |
|-------------|--------------|---------|
| External config / secrets | `spring.config.import`, configtree (§7.2.3) | **Spring Cloud Config** — отдельный проект; типично `spring.config.import=optional:configserver:` |
| Service discovery | — | Spring Cloud / K8s |
| Distributed tracing export | Micrometer Tracing, `@AutoConfigureObservability` в тестах (§7.9.3) | Полный stack — BOM Spring Boot + Micrometer |

---

## 3. Web stack: Web vs WebFlux vs WebMvc (§7.1.8, §8.2–§8.3, §11.6)

### 3.1 Алгоритм выбора `WebApplicationType` (§7.1.8)

| Условие на classpath | Контекст |
|----------------------|----------|
| Spring **MVC** присутствует | `AnnotationConfigServletWebServerApplicationContext` |
| MVC нет, **WebFlux** есть | Reactive web server context |
| Иначе | Non-web `ApplicationContext` |

Переопределение: `SpringApplication.setWebApplicationType(...)` или `spring.main.web-application-type`.

