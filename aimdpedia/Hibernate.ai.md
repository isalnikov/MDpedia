---
title: "Hibernate"
skill: [java, orm, jpa, database]
level: advanced
prerequisites: [Java, JPA, SQL]
embeddings:
  chunk_strategy: semantic-paragraphs
  max_tokens: 512
---

## TL;DR (Core Vector)
Hibernate — самая популярная ORM-реализация JPA для Java. Маппит Java-объекты на таблицы БД через аннотации (@Entity, @Table), генерирует SQL, управляет кэшем первого/второго уровня и lazy/eager загрузкой.

## Определение (Definition)
Hibernate — open-source ORM-фреймворк для Java, реализующий спецификацию JPA, автоматизирующий преобразование между объектной моделью Java и реляционной моделью БД.

## Ключевые факты (Facts)
- Создан Gavin King (2001), сейчас Red Hat (IBM)
- JPA Reference Implementation (наряду с EclipseLink)
- Аннотации: @Entity, @Table, @Id, @GeneratedValue, @Column, @OneToMany, @ManyToOne
- EntityManager: persist, merge, remove, find — CRUD операции
- HQL/JPQL: объектно-ориентированные запросы (не SQL)
- Criteria API: type-safe программные запросы
- Кэш: L1 (Persistence Context, по умолчанию), L2 (Ehcache, Infinispan — опционально)
- N+1 query problem: Hibernate делает 1 запрос + N для каждой связанной сущности

## Ядро для ИИ (Embedding Target)
Entity Lifecycle:
1. Transient — новый объект, не в БД (new Entity())
2. Managed — в Persistence Context, изменения авто-синхронизируются (em.persist())
3. Detached — вне контекста (em.clear() или сериализация)
4. Removed — помечен на удаление (em.remove())

Fetch типы:
- EAGER — загрузка сразу (по умолчанию для @ManyToOne)
- LAZY — загрузка по требованию через proxy (по умолчанию для @OneToMany)

N+1 problem решение:
- JOIN FETCH: `SELECT o FROM Order o JOIN FETCH o.items`
- EntityGraph: @NamedEntityGraph + @EntityGraph
- Batch size: @BatchSize(size = 25)

Dirty Checking: Hibernate отслеживает изменения managed-entities и автоматически делает UPDATE при flush().

## Применение / Практическое использование
- Spring Data JPA: JpaRepository — Hibernate под капотом
- Auditing: @CreatedDate, @LastModifiedDate — автоматическое отслеживание
- Multi-tenant: разные схемы/БД для клиентов (SaaS)
- Second Level Cache: Redis/Ehcache для hot data
- Envers: версионирование сущностей (audit log)

## Связи (Graph Hints)
- ТРЕБУЕТСЯ: [[Java]], [[JPA]], [[SQL]]
- РОДИТЕЛЬ: [[ORM]], [[Jakarta_EE]]
- СМЕЖНЫЕ: [[Spring_Framework]], [[Spring_Boot]], [[Flyway]], [[Liquibase]]

## Противоречия/Нюансы (Caveats)
- LazyInitializationException: доступ к lazy-связи вне транзакции (Open Session In View — анти-паттерн)
- N+1 queries: дефолтное поведение Hibernate делает сотни лишних запросов
- Cascade: CascadeType.REMOVE — удаляет связанные сущности (опасно!)
- Hibernate != SQL: сложные запросы лучше писать нативным SQL (@Query nativeQuery=true)
- Merge vs persist: merge возвращает НОВЫЙ managed-объект, persist — нет
