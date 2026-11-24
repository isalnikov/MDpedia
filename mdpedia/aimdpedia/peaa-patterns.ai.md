---
title: "Типовые решения PEAA (Patterns of Enterprise Application Architecture)"
source: "library/peaa-patterns.md"
---

## TL;DR (Core Vector)

См. полный каталог: `library/peaa-patterns.md`.

## Ядро для ИИ (Embedding Target)

---
source: "Martin Fowler — Patterns of Enterprise Application Architecture (PEAA); RU ed. Williams, 2006; books-md/Martin_Fauler_quot_Shablony_korporativnykh_prilozheny_quot.md"
pattern_count: 51
note: "Aggregate и Domain Event в этой книге не оформлены как типовые решения PEAA (см. Evans, Domain-Driven Design). Session Facade — родственное решение Core J2EE, обсуждается рядом с Remote Facade."
---

# Типовые решения PEAA (Patterns of Enterprise Application Architecture)

Справочник по **51** именованному паттерну из части II книги Мартина Фаулера. Группировка соответствует главам PEAA.

---

## Часть II, глава 9 — Представление бизнес-логики (Domain Logic)

### Transaction Script / Сценарий транзакции

**Problem.** Бизнес-приложение — последовательность транзакций; каждой нужна своя порция логики без тяжёлой объектной модели.

**Solution.** Организовать доменную логику в процедурах (классах/функциях): одна процедура обслуживает один запрос представления, обращается к БД напрямую или через тонкий шлюз.

**When to use.** Простая бизнес-логика; маленькие приложения; мало повторяющихся правил; нужны простота и производительность.

**When not.** Растущая сложность, дублирование кода между сценариями; богатые инварианты и поведение — переходите к Domain Model.

**Collaborating patterns.** Table Data Gateway, Row Data Gateway, Record Set, Gateway, Service Layer (как фасад над сценариями).

**Implementation notes.** Выделяйте сценарии из слоя представления; не вызывайте UI из сценариев; один класс на много сценариев или Command-на-каждый-сценарий; обычно один сценарий ≈ одна DB-транзакция.

**Example sketch.**

```text
class RecognizeRevenue {
  execute(contractId, asOfDate) {
    contract = ContractGateway.find(contractId)
  revenue = calculate(contract, asOfDate)
    ContractGateway.updateRevenue(contractId, revenue)
  }
}
```

---

### Domain Model / Модель предметной области

**Problem.** Сложная бизнес-логика не укладывается в процедуры без копипаста; правила и данные должны жить в связной объектной модели.

**Solution.** Объектная модель домена: сущности и объекты-значения с поведением и данными; сценарии делегируют работу объектам.

**When to use.** Нетривиальная логика, инварианты, полиморфизм; долгоживущий проект; важны тестируемость и структура.

**When not.** CRUD и простые отчёты — Transaction Script или Table Module дешевле.

**Collaborating patterns.** Service Layer, Data Mapper, Active Record, Unit of Work, Identity Map, Lazy Load, Repository, Value Object, Money.

**Implementation notes.** Избегайте anemic domain; отделяйте логику от UI и ORM-артефактов; со Active Record связь с БД сильнее, с Data Mapper — слабее.

**Example sketch.**

```text
class Contract {
  recognizeRevenue(asOfDate) { ... uses RevenueRecognition rules ... }
}
class RecognitionService {
  recognizeFor(contractId, date) {
    contract = repo.find(contractId)
    contract.recognizeRevenue(date)
    uow.commit()
  }
}
```

---

### Table Module / Модуль таблицы

**Problem.** Логика сгруппирована вокруг таблиц/наборов записей (часто в Record Set / DataSet), а не вокруг богатых объектов.

**Solution.** Один модуль (класс) на логическую таблицу: методы обрабатывают все строки таблицы (расчёты, обновления набора).

**When to use.** .NET DataSet / ADO Recordset-стиль; умеренная сложность; среда с сильной поддержкой табличных наборов.

**When not.** Богатая объектная модель с полиморфизмом — Domain Model + Mapper; простейшие случаи — Transaction Script.

**Collaborating patterns.** Table Data Gateway, Record Set, Layer Supertype.

**Implementation notes.** Не смешивать с Active Record (одна строка = один объект); хорошо стыкуется с Table Data Gateway, возвращающим Record Set.

**Example sketch.**

```text
class ContractModule {
  recognizeRevenue(contracts: RecordSet, asOfDate) {
    for row in contracts.rows()
      row.revenue = formula(row, asOfDate)
  }
}
```

---

### Service Layer / Слой служб

**Problem.** Нужна чёткая граница приложения (API): какие операции доступны снаружи и как координируется ответ.

**Solution.** Слой сервисов определяет набор операций, оркестрирует домен, транзакции и отклик; тонкий фасад над Domain Model или Transaction Script.

**When to use.** Несколько клиентов (Web, batch, remote); явный application boundary; транзакционные границы на уровне use-case.

**When not.** Один тонкий UI напрямую к домену при очень малом приложении (редко).

**Collaborating patterns.** Domain Model, Transaction Script, Remote Facade, DTO, Unit of Work, Layer Supertype, Transaction boundaries.

**Implementation notes.** Сервисы не должны быть «утончёнными» — логика в домене; удалённый доступ — Remote Facade над сервисами, не «толстый» EJB на каждую сущность.

**Example sketch.**

```text
interface RevenueService {
  recognizeRevenue(contractId, asOfDate)
}

