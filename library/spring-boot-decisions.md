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

### 3.2 Сравнение starters

| | `spring-boot-starter-web` | `spring-boot-starter-webflux` |
|--|---------------------------|-------------------------------|
| Стек | Servlet (Tomcat/Jetty/Undertow) | Netty (reactor-netty) |
| API | `@RestController`, `MockMvc` | `RouterFunction`, `WebTestClient` |
| Блокирующий I/O | Норма | **Анти-паттерн** на event loop |
| WAR deploy | Да (§18.19.1) | **Нет** — «not deployed as war» (§8.3) |
| Virtual threads | Java 21+: `spring.threads.virtual.enabled=true` (§7.1.14) | Отдельная модель (reactive) |

### 3.3 Оба starter’а на classpath (важно)

> Adding both `spring-boot-starter-web` and `spring-boot-starter-webflux` → **auto-config выбирает Spring MVC, не WebFlux** (§8.3 NOTE).

Типичный случай: MVC-приложение + **WebClient**. Решения:

- Оставить как есть (MVC + WebClient), или
- `spring.main.web-application-type=reactive` / `WebApplicationType.REACTIVE` для чистого WebFlux.

### 3.4 Когда **НЕ** reactive (WebFlux)

| Оставайтесь на MVC (`starter-web`) |
|-----------------------------------|
| Команда и кодовая база servlet/blocking |
| Тяжёлый JDBC/JPA в request path без полного reactive pipeline |
| Деплой **WAR** в внешний Tomcat |
| Экосистема завязана на Servlet filters, Spring Session servlet, часть Spring Security servlet-only |
| Нет измеримой выгоды по concurrency; **virtual threads** закрывают I/O-bound на MVC (§7.1.14) |

| Выбирайте WebFlux |
|-------------------|
| End-to-end reactive: R2DBC, reactive Redis/Kafka/Mongo, backpressure |
| Высокая плотность одновременных **долгих** I/O без thread-per-request |
| RSocket / reactive GraphQL transport (§8.6 таблица) |

### 3.5 `spring-boot-starter-webmvc`

В 3.2.x основной artifact — **`spring-boot-starter-web`** (включает Spring MVC). Отдельного `webmvc` starter в Table 1 нет — MVC = `starter-web`.

---

## 4. Data layer (§9)

### 4.1 Матрица доступа к данным

| Технология | Starter / API | Когда выбирать | Когда не выбирать |
|------------|---------------|----------------|-------------------|
| **Spring Data JPA** | `data-jpa` | Богатая доменная модель, lazy loading, портативный JPQL, зрелая команда Hibernate | Простой CRUD без ORM; жёсткий контроль SQL; native image сложнее |
| **Spring Data JDBC** | `data-jdbc` | SQL-центрично, агрегаты без lazy-графа, проще чем JPA | Сложные связи many-to-many в ORM-стиле |
| **JdbcTemplate / JdbcClient** | `starter-jdbc` | Процедурный SQL, отчёты, batch-вставки, legacy | Много boilerplate без repos |
| **R2DBC** | `data-r2dbc` | Reactive stack, неблокирующий SQL | Вместе с blocking JPA в том же request — путаница |
| **MongoDB** | `data-mongodb` | Документная модель, гибкая схема | Транзакции между агрегатами как в SQL |
| **LDAP** | `data-ldap` | Каталог пользователей, read-heavy directory (§9.2.7) | Основное transactional хранилище бизнес-данных |

### 4.2 Транзакции

| Стек | Механизм |
|------|----------|
| JPA / JDBC / Data JDBC | `PlatformTransactionManager`, `@Transactional` (JTA — §11.8) |
| R2DBC | `ReactiveTransactionManager` — **не auto-config** в reactive Neo4j примере; для R2DBC — настраивать явно при необходимости (§9.2.3 NOTE) |
| Kafka | `ChainedKafkaTransactionManager` — при нескольких TM помечать `@Primary` (how-to §18) |

**Open EntityManager in View:** по умолчанию `spring.jpa.open-in-view=true` для web; для API часто **`false`** (§9.1.4).

### 4.3 Инициализация схемы

| Подход | Правило из ref |
|--------|----------------|
| `schema.sql` / `data.sql` | Для простых случаев; с JPA — `spring.jpa.defer-datasource-initialization=true` |
| **Flyway** / **Liquibase** | **Только они** для prod schema; **не смешивать** с `schema.sql`/`data.sql` — support будет удалён (§18.9.3) |
| Hibernate `ddl-auto` | Embedded без Flyway/Liquibase: `create-drop`; иначе `none` (how-to) |
| Порядок | Hibernate **depends on** Flyway, чтобы миграции шли первыми |

**Выбор Flyway vs Liquibase:** в Boot паритет auto-config; Flyway — SQL/Java callbacks; Liquibase — changelog YAML/XML (§18.9.5).

### 4.4 Embedded DB (dev)

H2 console: servlet web + `h2` + **devtools** (или `spring.h2.console.enabled=true`); **не в prod** (§9.1.6).

---

## 5. HTTP clients (§11.6)

| Client | Рекомендация ref 3.2.3 | Модель |
|--------|------------------------|--------|
| **RestClient** | **Default для blocking** приложений без WebFlux/Reactor (§11.6.2) | Sync, functional API, prototype `RestClient.Builder` |
| **WebClient** | Если **WebFlux on classpath** (§11.6.1) | Reactive, non-blocking |
| **RestTemplate** | Legacy; «predates RestClient»; миграция по желанию (§11.6.3) | Нет готового bean — только `RestTemplateBuilder` |

### 5.1 Практические правила

| Ситуация | Выбор |
|----------|--------|
| Новый sync microservice, MVC | `RestClient.Builder` inject |
| Reactive service | `WebClient.Builder` |
| Существующий RestTemplate | `RestTemplateBuilder` до рефакторинга |
| SSL bundles | `RestClientSsl` / аналоги для WebClient (§11.6.2–11.6.3) |
| HTTP client backend | Auto-detection для RestClient и RestTemplate (§11.6.4) |
| Тест клиента | `@RestClientTest` + `MockRestServiceServer` (§7.9) |

---

## 6. Security (§8.4)

### 6.1 Default при `starter-security`

| Поведение |
|-----------|
| Все web endpoints secured |
| Сгенерированный пароль user (dev) — см. лог WARN |
| Form login или HTTP Basic по `Accept` |
| Actuator тоже secured, если actuator on classpath |

**Prod:** свой `SecurityFilterChain` → отключает default web security, **не** отключает UserDetailsService auto-config, пока не объявлен свой `UserDetailsService` / `AuthenticationManager`.

### 6.2 OAuth2 starters

| Starter | Применение | Ключевые properties |
|---------|------------|---------------------|
| `oauth2-client` | Браузерный/login app, вызов APIs от имени user | `spring.security.oauth2.client.registration.*`, `provider.*`, `issuer-uri` для OIDC discovery |
| `oauth2-resource-server` | **Stateless API**, Bearer JWT | `resourceserver.jwt.jwk-set-uri` или `issuer-uri` (§8.4.3) |
| `oauth2-authorization-server` | Вы **выдаёте** токены | Отдельный сервис авторизации |

**Back-off:** при `oauth2-client` / `oauth2-resource-server` / SAML на classpath default **in-memory UserDetails** отключается — свой `InMemoryUserDetailsManager` если нужен и OAuth2.

### 6.3 Actuator + Security

| Риск | Действие |
|------|----------|
| Sensitive endpoints | За firewall или Spring Security; `EndpointRequest` / `PathRequest` helpers (§8.4.1, §13) |
| CSRF на actuator POST | По умолчанию CSRF on (§13) |

---

## 7. Configuration (§7.2, §7.3, §18.2)

### 7.1 `application.properties` vs YAML

| | Properties | YAML (`application.yml`) |
|--|------------|---------------------------|
| Структура | Плоские ключи | Иерархия, multi-document (`---`) |
| В Boot | Оба first-class; snakeyaml через starter | §7.2.5 |
| Профили | `application-{profile}.properties` | `application-{profile}.yml` |

Выбор — taste команды; **complex config** удобнее в YAML.

### 7.2 `@ConfigurationProperties` vs `@Value` (§7.2.8, таблица p.114)

| Feature | `@ConfigurationProperties` | `@Value` |
|---------|----------------------------|----------|
| Relaxed binding | Да | Ограниченно |
| Meta-data (IDE) | Да | Нет |
| SpEL | Нет | Да |
| Группы настроек | `@EnableConfigurationProperties` | Точечные поля |

**Правило:** новые bounded contexts настроек → **typed `@ConfigurationProperties`**; одиночные значения / SpEL → `@Value` (canonical kebab-case).

### 7.3 Profiles (§7.3)

| Механизм | Использование |
|----------|---------------|
| `spring.profiles.active` | dev / staging / prod |
| Profile groups | Комбо профилей (§7.3.2) |
| `@Profile` на `@Configuration` | Beans по среде |
| Profile-specific files | `application-prod.yml` |

### 7.4 Import и внешние источники (§7.2.3)

| Механизм | Пример |
|----------|--------|
| `spring.config.import` | `optional:file:./dev.properties`, multi-location |
| Config tree (K8s) | `optional:configtree:/etc/config/`, secrets: `/run/secrets/` |
| `spring.config.additional-location` | Доп. файлы без замены порядка |
| Command line | Высший приоритет в Environment |

**Spring Cloud Config:** в ref 3.2.3 нет отдельной главы; на практике — dependency Spring Cloud + import URI; для локальной разработки достаточно `spring.config.import` / configtree.

---

## 8. Observability (§7.4, §13)

### 8.1 Actuator (`spring-boot-starter-actuator`)

| Тема | По умолчанию / совет |
|------|----------------------|
| Base path | `/actuator` |
| Health | `/actuator/health`, liveness/readiness (§7.1.6) |
| Exposure | Ограничить в prod (`management.endpoints.web.exposure.include`) |
| Security | Spring Security → actuator rules (§13) |

Полезные: `configprops`, `env`, `flyway`, `liquibase`, `metrics`, `integrationgraph` (§13).

### 8.2 Metrics (Micrometer)

| Аспект | Деталь |
|--------|--------|
| Registry | Auto-configured в prod; **не** в полном `@SpringBootTest` (кроме `@AutoConfigureObservability`) (§7.9.3) |
| Bindings | JVM, Tomcat, Logback, DataSource, Kafka, Rabbit, JMS, Mongo… (§13.7–13.8) |
| Теги / кастом | `MeterRegistryCustomizer`, отключение per-tech `management.metrics.*.enabled` |

### 8.3 Tracing

| Аспект | Деталь |
|--------|--------|
| Reporting | **Не** auto-config в `@SpringBootTest` |
| Тесты | `@AutoConfigureObservability` → no-op tracer в slices |
| Correlation | В log format при включённом tracing (§7.4.1) |

### 8.4 Logging (§7.4)

| | |
|--|--|
| Default | Logback (`spring-boot-starter-logging`) |
| Swap | `starter-log4j2` — исключить default logging |
| Уровни | `logging.level.*`, log groups (§7.4.6) |
| JSON / structured | Custom logback-spring.xml, profile-specific (§7.4.9) |

---

## 9. Testing (§7.9, §7.11)

### 9.1 Пирамида slice vs full

| Аннотация | Объём контекста | Типичное использование |
|-----------|-----------------|------------------------|
| `@SpringBootTest` | Полный (или почти) | Интеграция, `@MockBean`, random port |
| `@WebMvcTest` | MVC slice, только `@Controller` | Unit web layer + `MockMvc` (§7.9) |
| `@DataJpaTest` | JPA + embedded DB | Repositories, `@DataJpaTest` + TestEntityManager |
| `@DataJdbcTest` / `@JdbcTest` | JDBC repos / чистый JDBC | |
| `@JsonTest` | Jackson/Gson/Jsonb | DTO сериализация |
| `@RestClientTest` | REST clients | MockRestServiceServer |
| `@DataLdapTest` | LDAP slice | exclude `EmbeddedLdapAutoConfiguration` при внешнем LDAP |

### 9.2 `WebEnvironment`

| Значение | Когда |
|----------|-------|
| `MOCK` (default) | MockMvc, быстро |
| `RANDOM_PORT` / `DEFINED_PORT` | TestRestTemplate, WebTestClient live |
| Reactive tests | `spring.main.web-application-type=reactive` на `@SpringBootTest` |

### 9.3 Testcontainers (§7.9.4, §7.11)

| Паттерн | Деталь |
|---------|--------|
| `@Testcontainers` + `@Container` | Dockerized real DB/broker |
| `@ServiceConnection` | Auto wire connection details (Neo4j, Redis, Kafka…) |
| Dev time | Testcontainers + DevTools (§7.11.1) |

**Когда slices недостаточно:** реальный Postgres/Kafka → `@SpringBootTest` + Testcontainers, не embedded H2 «как prod».

---

## 10. Caching, scheduling, async, validation

| Capability | Starter / enable | Auto-config заметки |
|------------|------------------|---------------------|
| Cache | `spring-boot-starter-cache` + `@EnableCaching` | Caffeine/JCache/Redis по classpath (§8.2) |
| `@Scheduled` | Включено с `@EnableScheduling` | `TaskScheduler` bean; virtual threads → `SimpleAsyncTaskScheduler` (§7.8, §7.1.14) |
| `@Async` | `@EnableAsync` | `TaskExecutor`; virtual threads → `SimpleAsyncTaskExecutor` |
| Validation | `spring-boot-starter-validation` | `LocalValidatorFactoryBean`; с `@ConfigurationProperties` — Jakarta validation (§7.2.8) |

---

## 11. Messaging: выбор брокера (§10)

Критерии из структуры ref (platform support, не «один лучший»):

| Брокер | Starter | Сильные стороны (контекст ref) | Выбирать когда |
|--------|---------|--------------------------------|----------------|
| **RabbitMQ** | `starter-amqp` | AMQP, легковесный broker, routing, Spring Integration | Task queues, routing, moderate throughput, классический enterprise AMQP |
| **Kafka** | Spring Kafka autoconfig | Log-based stream, replay, Kafka Streams (§10.3.3) | High throughput event streaming, event sourcing, stream processing |
| **JMS** (ActiveMQ/Artemis) | `starter-activemq` / `artemis` | Jakarta JMS, `JmsTemplate`, XA (§11.8) | Legacy JMS, app server, XA с JTA |
| **Pulsar** | `starter-pulsar` | Multi-tenancy, geo-replication (новый stack в Boot 3.x) | Greenfield с Pulsar ops, unified messaging+streaming |

| Общий слой | `starter-integration` | FTP, HTTP, TCP, файлы, EIP — **не замена** брокеру, а orchestration (§10.6) |

**Embedded tests:** Kafka — Embedded Kafka (§10.3.5); Rabbit/Kafka — Testcontainers.

---

## 12. Batch, Integration, WebSocket, GraphQL

| Технология | Starter | Когда | Ref |
|------------|---------|-------|-----|
| **Spring Batch** | `starter-batch` | Chunk-oriented ETL, scheduled jobs, restartable jobs | §10.5, schema `spring.batch.jdbc.initialize-schema` |
| **Spring Integration** | `starter-integration` | Маршруты, адаптеры, legacy protocol bridges | §10.6, actuator `integrationgraph` |
| **WebSocket** | `starter-websocket` (servlet) или WebFlux | Push, STOMP (§10) | Servlet vs reactive stack |
| **GraphQL** | `starter-graphql` + transport | API schema-first, clients need flexible queries | §8.6 — transport: `web` / `webflux` / `websocket` / `rsocket` |

**GraphQL rule:** minimum `starter-graphql` **+** один transport starter (таблица §8.6).

---

## 13. Native image vs JVM (§15, §4.2.2)

| JVM (default) | GraalVM Native Image |
|---------------|----------------------|
| Dynamic classpath, reflection «как есть» | Closed world, AOT, **beans frozen** at build time |
| DevTools, быстрый цикл | Малый footprint, **быстрый cold start**, FaaS/K8s scale-to-zero |
| Все starters | Проверять limitations + Spring AOT hints |

**Когда native (§15.1):** container/FaaS, строгие SLO на startup/memory; команда готова к **native-test** pipeline (§15.3).

**Когда остаться на JVM:** heavy reflection/dynamic features, Groovy, полный JPA/Hibernate без AOT tuning, быстрые итерации dev.

**Сборка:** Buildpacks (`paketobuildpacks`) или Native Build Tools (§15.2.2–15.2.3). Требование: GraalVM 22.3+.

---

## 14. Packaging (§4.4.7, §6.9, §12, §18.19.1)

| Формат | Когда |
|--------|-------|
| **Executable JAR** (`bootJar` / `spring-boot-maven-plugin`) | Default cloud/microservices, `java -jar` |
| **WAR** + `SpringBootServletInitializer` | Корпоративный Tomcat/WebLogic; **не** для WebFlux war (§8.3) |
| **Layered JAR/WAR** | Docker cache: `dependencies` → `snapshot-dependencies` → `application` (§12.1.1) |
| **Cloud Native Buildpacks** | `pack build` / Maven-goal; Paketo layers.idx (§12.3) |
| **Fully executable jar** | Linux init.d — «exec» jar format (production deploy how-to) |

**Docker anti-pattern:** один fat layer uber-jar — использовать **layered** или buildpacks (§12.1).

---

## 15. Анти-паттерны и конфликты auto-config (§6.4)

### 15.1 Частые конфликты

| Симптом | Причина | Лечение |
|---------|---------|---------|
| MVC вместо WebFlux | Оба `web` + `webflux` | Явный `web-application-type` или убрать лишний starter (§8.3) |
| Два DataSource без @Primary | Flyway/Liquibase/JPA не знают куда | Один `@Primary` DataSource; `@FlywayDataSource` для второго (§18.9.5) |
| Embedded H2 в prod-test «как prod» | `@DataJpaTest` defaults | Testcontainers + `@ServiceConnection` |
| schema.sql + Flyway | Deprecated combo | Только Flyway/Liquibase (§18.9.3) |
| Default security в prod | `starter-security` без config | `SecurityFilterChain` + OAuth2/resource server |
| Actuator открыт | `include: *` | Exposure + Security |
| Собственный DataSource не подхватился | Auto-config back off partially | Свой bean — проверить `--debug` conditions report (§6.4.1) |

### 15.2 Отключение auto-config

| Способ | Пример |
|--------|--------|
| `@SpringBootApplication(exclude = …)` | `DataSourceAutoConfiguration.class` (§6.4.2) |
| `spring.autoconfigure.exclude` | Список FQCN |
| `@…Test(excludeAutoConfiguration = …)` | Slice tests |
| Свой `@Bean` | Back off matching auto-config |

### 15.3 `@Primary`

| Случай | Зачем |
|--------|-------|
| Несколько `DataSource` | JPA, Flyway, Liquibase default wiring |
| Несколько `KafkaTransactionManager` | Kafka TX chain |
| Custom `LdapTemplate` | Пометить custom context source как primary (how-to LDAP) |

### 15.4 Диагностика

```text
java -jar app.jar --debug
```

→ Condition evaluation report в логе (§6.4.1); DevTools — delta on restart (§6.8.3).

---

## Быстрые decision trees

### Новый REST-сервис (2024+, Java 21)

1. `starter-web` + `starter-actuator` + `starter-validation`
2. Data: `data-jpa` или `data-jdbc` по сложности домена
3. Security: `oauth2-resource-server` для API / `oauth2-client` для BFF
4. HTTP out: `RestClient.Builder`
5. Tests: `@WebMvcTest` + `@DataJpaTest` + Testcontainers для CI
6. Опционально: `spring.threads.virtual.enabled=true` вместо WebFlux «ради concurrency»

### Event-driven микросервис

1. Kafka → `spring-kafka`; Rabbit → `starter-amqp`
2. `starter-actuator` + metrics tags
3. `@SpringBootTest` + `@ServiceConnection` Kafka/Rabbit container
4. Идемпотентность consumers — вне Boot, но не embedded broker для contract tests

---

## Связь с паттернами репозитория

| Тема Boot | См. также в `library/` |
|-----------|-------------------------|
| Транзакции, репликация | `ddia-patterns.md` |
| Messaging | `eip-patterns.md` |
| Domain / Repository | `peaa-patterns.md` |
| API exposure | `api-management-patterns.md` |

---

*Документ синтезирован из Spring Boot Reference 3.2.3; при апгрейде Boot сверяйте TOC и appendix auto-configuration.*