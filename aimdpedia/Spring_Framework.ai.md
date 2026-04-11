---
title: "Spring Framework"
skill: [spring, java, dependency-injection]
level: advanced
prerequisites: [Java, Java_Virtual_Machine, Dependency_Injection]
embeddings:
  chunk_strategy: semantic-paragraphs
  max_tokens: 512
---

## TL;DR (Core Vector)
Spring Framework — open-source фреймворк для Java-приложений с Dependency Injection, Aspect-Oriented Programming, интеграцией данных и веб. Ядро — IoC Container (ApplicationContext), управляющий жизненным циклом бинов.

## Определение (Definition)
Spring Framework — комплексный фреймворк для enterprise-приложений на Java, обеспечивающий инфраструктурную поддержку: IoC/DI, AOP, транзакции, безопасность, доступ к данным, REST и MVC.

## Ключевые факты (Facts)
- Создан Rod Johnson (2002), сейчас VMware (Broadcom)
- IoC Container: BeanFactory → ApplicationContext (расширенный контекст)
- Dependency Injection: @Autowired, @Qualifier, @Primary, Constructor Injection
- AOP: @Aspect, @Before, @After, @Around — перехват методов
- @Configuration + @Bean — Java-based конфигурация (замена XML)
- Component Scanning: @Component, @Service, @Repository, @Controller
- Spring Data: JpaRepository, MongoRepository — авто-репозитории
- Spring Security: аутентификация, авторизация, OAuth2, JWT

## Ядро для ИИ (Embedding Target)
Spring IoC Container управляет бинами (объектами): создание, зависимость-инъекция, инициализация, уничтожение. ApplicationContext — основной интерфейс: AnnotationConfigApplicationContext, ClassPathXmlApplicationContext, WebApplicationContext.

Жизненный цикл бина:
1. Instantiation → создание объекта
2. Populate properties → DI (@Autowired)
3. BeanNameAware, BeanFactoryAware → callback'и
4. @PostConstruct / afterPropertiesSet → инициализация
5. Bean готов к использованию
6. @PreDestroy / destroy → очистка

Транзакции: @Transactional — декларативное управление. propagation (REQUIRED, REQUIRES_NEW), isolation (READ_COMMITTED, SERIALIZABLE), rollbackFor. Spring использует AOP proxy: если метод вызывает сам себя — @Transactional не сработает (proxy bypass).

Spring MVC: DispatcherServlet → HandlerMapping → Controller → View/ResponseBody. REST: @RestController + @RequestMapping + @GetMapping.

## Применение / Практическое использование
- Enterprise бэкенд: банки, телеком, e-commerce
- Spring Data JPA: @Entity + JpaRepository → CRUD без boilerplate
- Spring Security: OAuth2 login, JWT validation, method security
- Spring Batch: пакетная обработка миллионов записей
- Spring Integration: Enterprise Integration Patterns

## Связи (Graph Hints)
- ТРЕБУЕТСЯ: [[Java]], [[Dependency_Injection]]
- РОДИТЕЛЬ: [[Java_Framework]]
- СМЕЖНЫЕ: [[Spring_Boot]], [[Hibernate]], [[Микросервисы]], [[REST]]

## Противоречия/Нюансы (Caveats)
- «Магия Spring» — аннотации скрывают логику, сложно дебажить без понимания AOP proxy
- Circular dependency: A→B→A — Spring Boot 2.6+ запрещает по умолчанию
- @Transactional не работает внутри одного класса (self-invocation proxy issue)
- Heavy footprint: полный Spring Framework ~2MB+ jar, Spring Boot решил это
