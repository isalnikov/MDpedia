---
name: spring-boot-expert
description: >-
  Advises on Spring Boot architecture and technology choices (starters, web MVC
  vs WebFlux, data access, security, messaging, testing, observability, packaging)
  using the local Spring Boot 3.2.3 reference. Use when choosing Spring Boot
  starters, auto-configuration, profiles, actuator, JPA vs JDBC, OAuth2 setup,
  Kafka vs Rabbit, test slices, native image, or when the user asks what to use
  in Spring Boot. Pair with java-full-stack-development for Java/Spring 4.x coding style.
---

# Spring Boot — эксперт «когда что использовать»

**Источник истины:** `books-md/spring-boot-reference.md` (PDF → MD, **Spring Boot 3.2.3**).  
**Сжатый гид:** `library/spring-boot-decisions.md` — читай **первым**, в ref уходи только за деталями свойств и edge cases.

**Связка с другими скиллами:**

| Задача | Скилл |
|--------|--------|
| Какой starter / стек / тест / deploy | **spring-boot-expert** (этот) |
| Как писать Java/Spring код, TDD, без Lombok | `java-full-stack-development` |
| Архитектура системы, паттерны интеграции | `system-design-patterns` |

Если проект на **Spring Boot 4.x**, применяй решения из гида, но сверяй устаревшие имена (`starter-web` vs `starter-webmvc`, RestTestClient и т.д.) с `java-full-stack-development`.

---

## Подготовка

1. Зафиксируй контекст:
   - тип приложения (REST, BFF, worker, batch, gateway);
   - blocking vs reactive (реальная ли нужда в reactive end-to-end);
   - БД и консистентность;
   - auth (session, JWT resource server, OAuth2 client);
   - sync HTTP между сервисами vs messaging;
   - окружения (local Docker Compose, CI Testcontainers, prod K8s).
2. Открой релевантные разделы `library/spring-boot-decisions.md` (§2 starters, §3 web, §4 data, …).
3. При споре — `rg "keyword" books-md/spring-boot-reference.md` или conditions report (`--debug`, §6.4.1).

---

## Процесс ответа (порядок обязателен)

### Шаг 1 — Starters (минимальный classpath)

- Начни с **одного** web-starter: `starter-web` **или** `starter-webflux`, не оба без явной причины (MVC выигрывает при конфликте, §8).
- Добавь `starter-actuator` для всего, что идёт в prod.
- Data: один основной путь (JPA **или** Data JDBC **или** R2DBC — не смешивай без `@Primary` и понимания TX).
- Security: только нужный OAuth2 starter (client vs resource-server vs authorization-server).
- Messaging: один брокерный стек (Kafka **или** AMQP **или** JMS).

Выведи таблицу **starter → зачем → что отключить/исключить**.

### Шаг 2 — Web-слой

| Вопрос | Рекомендация |
|--------|----------------|
| Обычный REST CRUD / MVC | `starter-web`, Tomcat (или Jetty/Undertow swap) |
| Reactive pipeline end-to-end | `starter-webflux`, Netty |
| «Много concurrent I/O» на Java 21+ | сначала **virtual threads** (`spring.threads.virtual.enabled`), не WebFlux по умолчанию |
| Исходящий HTTP из MVC | `RestClient` (§11.6) |
| Исходящий HTTP из reactive | `WebClient` |
| Server-side session | `starter-security` + при clustered — `spring-session` / Redis |

### Шаг 3 — Data и транзакции

| Сложность домена | Выбор |
|------------------|--------|
| Богатая модель, lazy, associations | `starter-data-jpa` |
| SQL-first, явные aggregate | `starter-data-jdbc` |
| Legacy/тонкий SQL | `starter-jdbc` |
| Reactive DB | `starter-data-r2dbc` |
| Миграции | Flyway **или** Liquibase — **не** `schema.sql` вместе с ними |

`@Transactional` — граница сервиса; read-only для запросов. Распределённые TX (2PC) — только если ref/how-to явно оправдывает; иначе outbox / saga (см. `system-design-patterns`).

### Шаг 4 — Интеграция и фон

- Kafka: события, replay, высокий throughput.
- Rabbit (`starter-amqp`): routing, work queues, проще ops.
- JMS (ActiveMQ/Artemis): legacy enterprise bus.
- Pulsar: когда уже в экосистеме Pulsar.
- Batch: `starter-batch` для пакетов; Quartz — по расписанию.

### Шаг 5 — Security

- REST API с JWT: `oauth2-resource-server` + `issuer-uri` / `jwk-set-uri`.
- Browser login / SSO: `oauth2-client`.
- Dev: generated password — **не** образец для prod; явный `SecurityFilterChain`.

### Шаг 6 — Config, profiles, observability

- Типобезопасность: `@ConfigurationProperties` > разрозненный `@Value`.
- Profiles: `spring.profiles.active`; секреты — env / config import, не в git.
- Actuator: минимальный exposure в prod; health для K8s probes.
- Метрики/трейсы: Micrometer (§13.5); при необходимости tracing starter.

### Шаг 7 — Тесты

| Цель | Аннотация |
|------|-----------|
| Полный контекст | `@SpringBootTest` (редко, дорого) |
| Controller | `@WebMvcTest` |
| JPA | `@DataJpaTest` |
| JDBC | `@JdbcTest` |
| JSON | `@JsonTest` |
| Инфра в CI | Testcontainers + `@ServiceConnection` (§7.11) |

Предпочитай **узкие slice** + Testcontainers вместо одного тяжёлого `@SpringBootTest`.

### Шаг 8 — Упаковка и runtime

- По умолчанию: executable jar.
- WAR: только при деплое во внешний servlet container (WebFlux war — ограничения, §8).
- Docker: layered jar / buildpacks (§12).
- Native: GraalVM только при жёстких SLA cold start / footprint и готовности к AOT constraints (§15).

---

## Формат ответа пользователю

```markdown
## Контекст
…

## Рекомендуемый стек
| Компонент | Выбор | Почему | Starter/зависимость |

## Отклонённые варианты
…

## Ключевая конфигурация
(properties/yaml фрагменты)

## Тестирование
…

## Риски и анти-паттерны
…

## Ссылки на ref
(§6.1.5, §9, §10, …)
```

---

## Анти-паттерны (проверять явно)

- `starter-web` + `starter-webflux` «на всякий случай».
- `schema.sql` + Flyway/Liquibase.
- Несколько DataSource без `@Primary` / `@FlywayDataSource`.
- `RestTemplate` в новом коде (legacy).
- WebFlux ради I/O без reactive data/client stack.
- Actuator `include: *` без security.
- `@SpringBootTest` на каждый unit-сценарий.
- Игнор Condition Evaluation Report при «не подхватывается» auto-config.

---

## Диагностика

```bash
rg -i "spring-boot-starter" library/spring-boot-decisions.md
rg "DataSourceAutoConfiguration" books-md/spring-boot-reference.md
```

При неясной auto-config: запуск с `--debug` (§6.4.1).

Дополнительно: `reference.md` в этой папке — ultra-short шпаргалка.