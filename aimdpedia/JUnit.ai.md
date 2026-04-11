---
title: "JUnit"
skill: [java, testing, unit-testing]
level: beginner
prerequisites: [Java]
embeddings:
  chunk_strategy: semantic-paragraphs
  max_tokens: 512
---

## TL;DR (Core Vector)
JUnit — стандарт де-факто для unit-тестирования Java-приложений. JUnit 5 (Jupiter) использует аннотации @Test, @BeforeEach, @ParameterizedTest и Assertions для проверяемых утверждений. Интегрируется с Maven/Gradle и IDE.

## Определение (Definition)
JUnit — open-source фреймворк для модульного тестирования Java, поддерживающий аннотации, assertions, параметризованные тесты, extension model и интеграцию с инструментами сборки.

## Ключевые факты (Facts)
- JUnit 5 (2017): JUnit Platform + JUnit Jupiter (API) + JUnit Vintage (обратная совместимость 3/4)
- @Test, @BeforeEach, @AfterEach, @BeforeAll, @AfterAll — lifecycle
- Assertions: assertEquals, assertTrue, assertThrows, assertTimeout, assertAll
- @ParameterizedTest + @ValueSource, @CsvSource, @MethodSource — параметризация
- @DisplayName — читаемые названия тестов в отчётах
- @Nested — вложенные тестовые группы
- Mockito: @Mock, @InjectMocks, when().thenReturn() — мокирование зависимостей
- Testcontainers: Docker-контейнеры для интеграционных тестов (БД, Kafka, Redis)

## Ядро для ИИ (Embedding Target)
Структура теста:
```java
@Test
@DisplayName("При пустом списке возвращается пустой Optional")
void shouldReturnEmptyForEmptyList() {
    Optional<String> result = service.findById("nonexistent");
    assertTrue(result.isEmpty());
}
```

Test Lifecycle:
1. @BeforeAll — один раз до всех тестов (static метод)
2. @BeforeEach — перед каждым тестом
3. @Test — сам тест
4. @AfterEach — после каждого теста
5. @AfterAll — один раз после всех тестов

Parameterized Tests:
```java
@ParameterizedTest
@CsvSource({"1, true", "0, false", "-1, false"})
void testIsPositive(int input, boolean expected) {
    assertEquals(expected, MathUtils.isPositive(input));
}
```

Mockito Integration:
```java
@ExtendWith(MockitoExtension.class)
class ServiceTest {
    @Mock Repository repo;
    @InjectMocks Service service;
    @Test void test() { when(repo.findById(1)).thenReturn(Optional.of(entity)); }
}
```

## Применение / Практическое использование
- Unit-тесты: каждый метод сервиса/утилиты
- Интеграционные: @SpringBootTest + Testcontainers
- Performance: @RepeatedTest(100) — нагрузочные тесты
- CI/CD: mvn test / gradle test → JaCoCo coverage report
- TDD: Red-Green-Refactor цикл

## Связи (Graph Hints)
- ТРЕБУЕТСЯ: [[Java]]
- РОДИТЕЛЬ: [[Тестирование]]
- СМЕЖНЫЕ: [[Mockito]], [[Testcontainers]], [[Spring_Boot]], [[CI/CD]]

## Противоречия/Нюансы (Caveats)
- Тестирование приватных методов — анти-паттерн (тестируйте через public API)
- Избыточные моки: тестирование мок-объектов вместо реальных — false positive
- @SpringBootTest тяжелый — используйте @WebMvcTest / @DataJpaTest для скорости
- Flaky tests: тесты, проходящие не всегда — CI/CD проблема №1
- 100% coverage ≠ качество: важно тестировать поведение, не строки
