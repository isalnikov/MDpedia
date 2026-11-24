# Spring Boot — шпаргалка

**Док:** `library/spring-boot-decisions.md` · **Ref:** 3.2.3

## Starters (90% случаев)

| Нужно | Starter |
|-------|---------|
| REST API | `spring-boot-starter-web` |
| Reactive API | `spring-boot-starter-webflux` |
| JPA | `spring-boot-starter-data-jpa` |
| SQL repos без ORM | `spring-boot-starter-data-jdbc` |
| Reactive SQL | `spring-boot-starter-data-r2dbc` |
| JWT API | `spring-boot-starter-oauth2-resource-server` |
| Kafka | `spring-kafka` |
| Rabbit | `spring-boot-starter-amqp` |
| Prod ops | `spring-boot-starter-actuator` |
| Tests | `spring-boot-starter-test` |

## HTTP clients (Boot 3.2)

| Контекст | API |
|----------|-----|
| Blocking service | `RestClient` |
| Reactive | `WebClient` |
| Legacy | `RestTemplate` (избегать) |

## Тесты

`@WebMvcTest` · `@DataJpaTest` · `@JdbcTest` · Testcontainers `@ServiceConnection`

## Одна строка

**Сначала минимальные starters + virtual threads; WebFlux — только если reactive stack end-to-end.**