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
class RevenueServiceImpl {
  recognizeRevenue(id, date) {
    tx.begin()
    contract = contracts.find(id)
    contract.recognizeRevenue(date)
    tx.commit()
  }
}
```

---

## Часть II, глава 10 — Архитектурные решения источников данных (Data Source Architectural)

### Table Data Gateway / Шлюз таблицы данных

**Problem.** Нужен доступ к SQL/таблице без размазывания ADO/JDBC по приложению.

**Solution.** Объект-шлюз (Gateway) с методами find/update по таблице; возвращает примитивы, DTO или Record Set.

**When to use.** Transaction Script, Table Module; простой SQL-доступ к целой таблице.

**When not.** Rich Domain Model с отслеживанием графа объектов — Data Mapper + Repository.

**Collaborating patterns.** Gateway, Record Set, Transaction Script, Table Module, Row Data Gateway.

**Implementation notes.** Не путать с DAO (часто строка-ориентирован); один gateway на таблицу; статические vs инстанс-методы.

**Example sketch.**

```text
class PersonGateway {
  static find(id): Row { sql "SELECT * FROM person WHERE id=?" }
  static update(row) { ... }
}
```

---

### Row Data Gateway / Шлюз записи данных

**Problem.** Нужна оболочка вокруг **одной** строки БД, а не всей таблицы.

**Solution.** Класс записи: поля соответствуют колонкам; методы load/save/update для одного экземпляра.

**When to use.** Transaction Script с объектной «обёрткой» строки; простые CRUD без полного Active Record.

**When not.** Domain Model + Mapper — Row Gateway даёт слабую связь объект↔БД при сложных графах.

**Collaborating patterns.** Gateway, Transaction Script; контраст с Active Record (богаче поведение в AR).

**Implementation notes.** Легко перерастает в Active Record, если добавить доменные методы на объект строки.

**Example sketch.**

```text
class PersonRow {
  id, name, departmentId
  static find(id): PersonRow
  update() { sql UPDATE ... }
}
```

---

### Active Record / Активная запись

**Problem.** Связать строку БД и объект с минимальным отображением; CRUD и часть логики на самом объекте.

**Solution.** Каждая сущность знает, как загрузить/сохранить себя; статические finders; таблица ≈ класс.

**When to use.** Простой и средний домен; Rails-стиль; быстрый старт; мало сложного OR-mapping.

**When not.** Сложные ассоциации, наследование, независимость домена от БД — Data Mapper.

**Collaborating patterns.** Table Data Gateway, Identity Field, Lazy Load (ограниченно), Transaction Script.

**Implementation notes.** Домен и персистентность смешаны — труднее тестировать и эволюционировать; хорош для прототипов.

**Example sketch.**

```text
class Person extends ActiveRecord {
  static find(id): Person
  save() { insert or update self }
  def transfer(dept) { self.deptId = dept.id; save() }
}
```

---

### Data Mapper / Преобразователь данных

**Problem.** Доменные объекты не должны знать о SQL; нужен явный слой переноса между БД и моделью.

**Solution.** Отдельные Mapper-классы: load/save/update/delete; домен остаётся «чистым».

**When to use.** Domain Model со сложными связями, наследованием, тестами без БД.

**When not.** Простой CRUD — Active Record или Gateway дешевле в разработке.

**Collaborating patterns.** Mapper, Unit of Work, Identity Map, Identity Field, Lazy Load, Metadata Mapping, Repository, все OR structure patterns.

**Implementation notes.** Методы поиска часто выносят в отдельные finder/repository; метаданные снижают бойлерплейт.

**Example sketch.**

```text
class PersonMapper {
  find(id): Person
  insert(person)
  update(person)
}
// Person has no SQL
```

---

## Часть II, глава 11 — ОР-поведение (Object-Relational Behavioral)

### Unit of Work / Единица работы

**Problem.** Много изменений в памяти за одну бизнес-транзакцию; нельзя писать в БД после каждого setter; нужен учёт dirty/new/deleted и порядок flush.

**Solution.** UoW регистрирует объекты при чтении/изменении; при commit открывает DB-транзакцию, проверяет concurrency, пишет пакетом.

**When to use.** Domain Model + Data Mapper; любая нетривиальная бизнес-транзакция в памяти.

**When not.** Transaction Script с одним UPDATE на запрос.

**Collaborating patterns.** Data Mapper, Identity Map, Optimistic/Pessimistic Offline Lock, Identity Field.

**Implementation notes.** Caller vs object registration vs aspect-generated registration; интеграция с сессией/request scope.

**Example sketch.**

```text
uow = UnitOfWork.current()
person = mapper.load(1); uow.registerClean(person)
person.name = "Ann"; uow.registerDirty(person)
uow.commit() // mapper issues SQL in order
```

---

### Identity Map / Коллекция объектов

**Problem.** Повторная загрузка одного и того же id создаёт дубликаты в памяти и ломает identity semantics.

**Solution.** Кэш в рамках UoW/транзакции: перед load проверить map по id; один объект — один экземпляр.

**When to use.** Любой Data Mapper в одной бизнес-транзакции; обход графа с циклами.

**When not.** Stateless read-only API без общего контекста (можно map на запрос).

**Collaborating patterns.** Unit of Work, Lazy Load, Data Mapper.

**Implementation notes.** Ключи: числовой id, составной, per-class maps; место — в Mapper или UoW.

**Example sketch.**

```text
find(id) {
  if (map.contains(id)) return map.get(id)
  row = db.query(id)
  obj = hydrate(row); map.put(id, obj); return obj
}
```

---

### Lazy Load / Загрузка по требованию

**Problem.** Eager load всего графа — медленно и избыточно; нужны данные только при обращении.

**Solution.** Прокси, virtual proxy, value holder или ghost: связь загружается при первом доступе.

**When to use.** Domain Model с ассоциациями; удалённые вызовы (осторожно с chatty load).

**When not.** Маленькие фиксированные графы; batch-отчёты — лучше eager/join.

**Collaborating patterns.** Identity Map, Foreign Key Mapping, Data Mapper, Remote Facade (минимизировать round-trips).

**Implementation notes.** Варианты: lazy initialization, virtual proxy, value holder, ghost; осторожно с Lazy Load через сеть.

**Example sketch.**

```text
class DepartmentProxy {
  getEmployees() {
    if (!loaded) employees = mapper.loadEmployees(deptId)
    return employees
  }
}
```

---

## Часть II, глава 12 — ОР-структура (Object-Relational Structural)

### Identity Field / Поле идентификации

**Problem.** Объект в памяти должен стабильно соответствовать строке БД.

**Solution.** Поле (или Key class) хранит первичный ключ БД; маппер использует его для read/insert/update.

**When to use.** Всегда с Data Mapper / Active Record при суррогатных или натуральных ключах.

**When not.** Transaction Script без объектной identity.

**Collaborating patterns.** Data Mapper, Foreign Key Mapping, Unit of Work.

**Implementation notes.** Генерация ключей: DB sequence, key table, UUID; composite keys → Key class.

**Example sketch.**

```text
class Person {
  PersonKey id  // wraps long or composite
}
```

---

### Foreign Key Mapping / Отображение внешних ключей

**Problem.** Ассоциация объект↔объект должна стать FK в реляционной схеме.

**Solution.** Хранить id связанной сущности (или коллекцию id); mapper загружает ссылку через find.

**When to use.** 1..1 и 1..N через FK-столбец.

**When not.** M..N без поля на стороне — Association Table Mapping.

**Collaborating patterns.** Lazy Load, Identity Map, Association Table Mapping.

**Implementation notes.** Многотабличные join при load; коллекции ссылок — отдельная таблица или FK с обратной стороны.

**Example sketch.**

```text
// person.department_id -> Department
loadPerson(row) {
  p = new Person(row.id)
  p.department = departmentMapper.find(row.dept_id)
}
```

---

### Association Table Mapping / Отображение через таблицу ассоциаций

**Problem.** Многие-ко-многим нет места для FK на одной стороне.

**Solution.** Связующая таблица с двумя FK; mapper читает/пишет пары id.

**When to use.** M..N: сотрудник–навыки, студент–курс.

**When not.** 1..N с FK на дочерней таблице.

**Collaborating patterns.** Foreign Key Mapping, Lazy Load.

**Implementation notes.** Можно загружать коллекцию одним запросом IN (...).

**Example sketch.**

```text
// employee_skill(employee_id, skill_id)
loadSkills(employeeId) {
  ids = sql "SELECT skill_id FROM employee_skill WHERE employee_id=?"
  return ids.map(skillMapper::find)
}
```

---

### Dependent Mapping / Отображение зависимых объектов

**Problem.** Дочерние объекты без собственной identity в БД (зависимые) — только вместе с родителем.

**Solution.** Mapper родителя полностью владеет load/save дочерних строк; отдельного mapper для child нет (или он подчинён).

**When to use.** Композиция: альбом–треки, заказ–строки без глобального id строки.

**When not.** Дочерняя сущность со своим PK и отдельным жизненным циклом — Foreign Key / Repository.

**Collaborating patterns.** Unit of Work, Identity Field.

**Implementation notes.** Удаление родителя каскадирует; обновление часто delete-and-reinsert для зависимых.

**Example sketch.**

```text
saveAlbum(album) {
  save album row
  delete tracks where album_id=album.id
  for t in album.tracks: insert track row
}
```

---

### Embedded Value / Внедрённое значение

**Problem.** Value Object в домене (Money, Address) не имеет отдельной таблицы.

**Solution.** Колонки родительской таблицы хранят поля VO (amount, currency, street, ...).

**When to use.** Небольшие immutable value objects без identity.

**When not.** Ссылка на разделяемый справочник с id — отдельная таблица + FK.

**Collaborating patterns.** Value Object, Money, Serialized LOB (альтернатива для сложного VO).

**Implementation notes.** Null-семантика по группе полей; маппинг в один embedded блок.

**Example sketch.**

```text
// columns: amount, currency
hydrateMoney(row) = new Money(row.amount, row.currency)
```

---

### Serialized LOB / Сериализованный крупный объект

**Problem.** Граф или иерархия не ложится на нормальные колонки; нужен один BLOB/CLOB.

**Solution.** Сериализовать (XML, JSON, Java serialize) в LOB-поле.

**When to use.** Редко меняющиеся структуры; иерархия отделов; документный фрагмент.

**When not.** Нужны запросы по частям структуры — нормализовать таблицами.

**Collaborating patterns.** Embedded Value, Dependent Mapping.

**Implementation notes.** Версионирование формата сериализации; нет FK-целостности внутри LOB.

**Example sketch.**

```text
saveOrgTree(dept) {
  blob = xmlSerialize(dept.tree)
  sql "UPDATE dept SET tree_lob=? WHERE id=?"
}
```

---

### Single Table Inheritance / Наследование с одной таблицей

**Problem.** Иерархия классов в ООП, одна таблица в БД.

**Solution.** Одна таблица, discriminator + nullable колонки для всех подклассов.

**When to use.** Небольшая иерархия, редкие поля у подклассов.

**When not.** Много специфичных колонок → sparse table; Class Table или Concrete Table.

**Collaborating patterns.** Inheritance Mappers, Identity Field.

**Implementation notes.** Discriminator column; null в неиспользуемых полях подклассов.

**Example sketch.**

```text
// players: type DISC='soccer'|'cricket', поля всех видов в одной таблице
load(row) = switch(row.type) { ... }
```

---

### Class Table Inheritance / Наследование с таблицей на класс

**Problem.** Нормализовать подклассы — отдельная таблица на каждый класс в иерархии.

**Solution.** Таблица суперкласса + таблицы подклассов с FK на базовую строку.

**When to use.** Много полей подклассов; важна нормализация.

**When not.** Глубокая иерархия — много join при load.

**Collaborating patterns.** Inheritance Mappers, Foreign Key Mapping.

**Implementation notes.** Load = join base + subclass; insert в несколько таблиц в транзакции.

**Example sketch.**

```text
loadSoccerPlayer(id) {
  base = loadPlayer(id)
  extra = loadSoccerRow(id)
  return merge(base, extra)
}
```

---

### Concrete Table Inheritance / Наследование с таблицей на конкретный класс

**Problem.** Каждый конкретный тип — своя полная таблица без общей родительской.

**Solution.** Отдельная таблица на leaf-класс со всеми полями (дублирование общих колонок).

**When to use.** Подклассы слабо связаны; редкие полиморфные запросы по всей иерархии.

**When not.** Частые запросы «все Player» — сложно UNION.

**Collaborating patterns.** Inheritance Mappers.

**Implementation notes.** Полиморфный find = UNION или отдельные запросы.

**Example sketch.**

```text
// soccer_player, cricket_player — нет общей player
findAllPlayers() = union(findSoccer(), findCricket())
```

---

### Inheritance Mappers / Преобразователи наследования

**Problem.** Координация several mappers для одной иерархии классов.

**Solution.** Базовый Mapper + подклассовые mappers; общий API load/save по иерархии.

**When to use.** Любое OR-наследование (single/class/concrete table).

**When not.** Composition over inheritance в домене — плоские mappers.

**Collaborating patterns.** Data Mapper, все inheritance table patterns.

**Implementation notes.** Фабрика mapper по discriminator; shared insert/update pipeline.

**Example sketch.**

```text
class PlayerMapper {
  load(id) { disc = readType(id); return mappers[disc].load(id) }
}
```

---

## Часть II, глава 13 — ОР с метаданными (Metadata Mapping)

### Metadata Mapping / Отображение метаданных

**Problem.** Повторяющийся код mappers для похожих сущностей.

**Solution.** Описание колонок, связей, наследования в метаданных; generic mapper интерпретирует метаданные (часто reflection).

**When to use.** Много сущностей; внутренние ORM/framework; снижение дублирования.

**When not.** Одна-две таблицы — ручной mapper проще.

**Collaborating patterns.** Data Mapper, Query Object, Repository.

**Implementation notes.** Хранение metadata: XML, аннотации, БД; синхронизация с миграциями схемы.

**Example sketch.**

```text
metadata["Person"] = { table: "person", fields: { name: "name", id: "id" } }
genericMapper.load("Person", id)
```

---

### Query Object / Объект запроса

**Problem.** Динамические или переиспользуемые запросы размазаны по коде.

**Solution.** Объект, инкапсулирующий SQL/HQL и параметры; можно композировать и тестировать.

**When to use.** Сложные фильтры, отчёты, один запрос из многих мест.

**When not.** Статический findById в mapper.

**Collaborating patterns.** Repository, Metadata Mapping.

**Implementation notes.** Отделить построение SQL от выполнения; защита от SQL-injection через bind params.

**Example sketch.**

```text
class EmployeesByDeptQuery {
  deptId
  execute() = sql "SELECT * FROM person WHERE dept_id = ?", deptId
}
```

---

### Repository / Хранилище

**Problem.** Домену нужна коллекция-подобная абстракция персистентности, а не детали SQL.

**Solution.** Repository: find by id, add, remove, possibly specifications; делегирует mapper/UoW.

**When to use.** Domain Model; DDD-стиль доступа к агрегатам (концепция агрегата — из Evans, не отдельный паттерн PEAA).

**When not.** Transaction Script + Gateway напрямую.

**Collaborating patterns.** Data Mapper, Query Object, Unit of Work, Identity Map.

**Implementation notes.** Один repository на aggregate root; не generic DAO на каждую таблицу без доменного смысла.

**Example sketch.**

```text
interface PersonRepository {
  find(id): Person
  findByManager(managerId): List<Person>
  save(person)
}
```

---

## Часть II, глава 14 — Web-представление (Web Presentation)

### Model View Controller (MVC) / Модель—представление—контроллер

**Problem.** Смешение UI, обработки ввода и доменной логики в одном месте.

**Solution.** Model — данные/домен; View — отображение; Controller — реакция на ввод, обновление model и выбор view.

**When to use.** Любое интерактивное UI; базовая схема для Web и desktop.

**When not.** Не заменяет выбор Page vs Front Controller — это уточнение C в Web.

**Collaborating patterns.** Page Controller, Front Controller, Application Controller, Template View.

**Implementation notes.** Толстый controller — антипаттерн; model не должна знать о HTTP.

**Example sketch.**

```text
Controller.handle(request) {
  model = service.load(...)
  return View.render(model)
}
```

---

### Page Controller / Контроллер страниц

**Problem.** Простой сайт: один URL ≈ одна страница/действие.

**Solution.** Отдельный контроллер (servlet, code-behind, handler) на страницу или логическое действие.

**When to use.** Простой поток, мало общей инфраструктуры запросов.

**When not.** Сложная маршрутизация, единая точка безопасности/локализации — Front Controller.

**Collaborating patterns.** Template View, MVC, Transaction Script / Service Layer.

**Implementation notes.** JSP как controller — слабее, чем отдельный servlet + Template View.

**Example sketch.**

```text
class EditPersonPage {
  handle(req) {
    if (POST) PersonService.update(req)
    model.person = PersonService.find(req.id)
    forward("editPerson.jsp", model)
  }
}
```

---

### Front Controller / Контроллер запросов

**Problem.** Единая точка входа HTTP: auth, логирование, маршрутизация, общий layout.

**Solution.** Один front controller диспетчеризует ко множеству actions/handlers по URL/команде.

**When to use.** Сложный site flow, i18n, security filter chain, REST-style единый entry.

**When not.** Маленький статический site.

**Collaborating patterns.** Application Controller, MVC, Template View, Page Controller (actions внутри).

**Implementation notes.** Servlet Filter + Dispatcher; не дублировать бизнес-логику в controller.

**Example sketch.**

```text
FrontController.service(req) {
  handler = router.match(req.path)
  handler.execute(req, res)
}
```

---

### Template View / Представление по шаблону

**Problem.** Нужен HTML, который правят дизайнеры, с вставкой динамики.

**Solution.** Статический шаблон + маркеры/скриплеты/ taglibs (JSP, Velocity, Razor) для подстановки данных.

**When to use.** Основной способ server-side HTML в PEAA-эпохе.

**When not.** API-only backend; чистый client-side SPA (вне фокуса книги).

**Collaborating patterns.** Page Controller, Front Controller, Two Step View.

**Implementation notes.** Минимум логики в view; helper objects для форматирования.

**Example sketch.**

```text
<!-- person.jsp -->
<h1>${person.name}</h1>
<c:forEach items="${person.orders}" var="o">...</c:forEach>
```

---

### Transform View / Представление с преобразованием

**Problem.** Генерация markup через последовательное преобразование DOM-дерева или потока элементов.

**Solution.** View обходит структуру model и пишет HTML (или SAX-подобный pipeline).

**When to use.** Древовидные модели; XSLT-подобные pipeline без шаблонов с маркерами.

**When not.** Команда привыкла к WYSIWYG HTML-шаблонам — Template View.

**Collaborating patterns.** MVC, Two Step View.

**Implementation notes.** Проще для программистов, труднее для дизайнеров.

**Example sketch.**

```text
class PersonTransformView {
  render(person, writer) {
    writer.tag("h1").text(person.name).end()
  }
}
```

---

### Two Step View / Двухэтапное представление

**Problem.** Несколько скинов/форматов (HTML, WAP) из одной model; переиспользование «логической страницы».

**Solution.** Шаг 1: model → логический XML/структура; шаг 2: XSLT/преобразование в целевой формат.

**When to use.** Мульти-канальный вывод; единая логическая разметка.

**When not.** Один HTML-сайт — лишняя сложность.

**Collaborating patterns.** Template View, Transform View.

**Implementation notes.** Стоимость XSLT-отладки; сильная связка с инструментом.

**Example sketch.**

```text
logical = LogicalPageBuilder.build(model)
html = xslt(logical, "site.xsl")
```

---

### Application Controller / Контроллер приложения

**Problem.** Навигация между экранами и use-case не равна одному HTTP-запросу; нужна state machine потока.

**Solution.** Централизованный контроллер приложения выбирает следующий экран/действие по состоянию workflow.

**When to use.** Многошаговые мастера, сложные UI flow поверх Front/Page controllers.

**When not.** Простые CRUD-страницы.

**Collaborating patterns.** Front Controller, MVC, Service Layer.

**Implementation notes.** Отделяет **flow** от **page** handling.

**Example sketch.**

```text
AppController.next(state, event) {
  return transitions[state][event] // e.g. SHIPPING -> PAYMENT
}
```

---

## Часть II, глава 15 — Распределённая обработка (Distribution)

### Remote Facade / Интерфейс удаленного доступа

**Problem.** Fine-grained объекты дают слишком много remote calls; latency и marshalling дороги.

**Solution.** Грубый фасад: мало методов, передающих агрегированные DTO; внутри — вызовы fine-grained domain.

**When to use.** Remote client к богатой Domain Model; EJB session bean style; внутрипроцессный — не нужен.

**When not.** Всё в одном процессе — обычный Service Layer.

**Collaborating patterns.** DTO, Service Layer, Session Facade (EJB-идiom), Data Mapper.

**Implementation notes.** Фасад без доменной логики; bulk getters/setters; не expose lazy associations remotely.

**Example sketch.**

```text
class OrderRemoteFacade {
  getOrderDetails(orderId): OrderDTO {
    order = orderService.load(orderId) // many local calls
    return OrderDTO.from(order)
  }
}
```

**Related:** **Session Facade** (Core J2EE) — тот же принцип для компонентов сеанса EJB; в PEAA обсуждается в связке с Remote Facade.

---

### Data Transfer Object (DTO) / Объект переноса данных

**Problem.** Много remote вызовов при передаче объектов по полю; нельзя сериализовать lazy graph.

**Solution.** Простой сериализуемый объект с полями (arrays of primitives, nested DTO), собранный за один вызов.

**When to use.** Remote Facade, Web API между слоями (осторожно — не abuse между локальными слоями).

**When not.** Локальный Domain Model в одном процессе — передавайте domain, не клонируйте в DTO без нужды.

**Collaborating patterns.** Remote Facade, Service Layer, Record Set (альтернатива табличного переноса).

**Implementation notes.** Assembler на границе; версионирование DTO; избегать «анемичного домена» из DTO.

**Example sketch.**

```text
class AlbumDTO { id, title, artistName, trackNames[] }
assembler.toDTO(album: Album): AlbumDTO
```

---

## Часть II, глава 16 — Автономный параллелизм (Offline Concurrency)

### Optimistic Offline Lock / Оптимистическая автономная блокировка

**Problem.** Длинная бизнес-транзакция в памяти; несколько пользователей меняют одни данные.

**Solution.** При commit сравнить version/timestamp с БД; при конфликте — откат и ошибка пользователю.

**When to use.** Редкие коллизии; read-mostly; хорош UX без долгих DB locks.

**When not.** Высокая конкуренция на запись — Pessimistic или Coarse-Grained.

**Collaborating patterns.** Unit of Work, Data Mapper, Identity Field (version column).

**Implementation notes.** Version column на корне; проверка при UPDATE ... WHERE version=?.

**Example sketch.**

```text
commit() {
  if (db.update(person, expectedVersion) == 0)
    throw ConcurrencyException
}
```

---

### Pessimistic Offline Lock / Пессимистическая автономная блокировка

**Problem.** Нужно гарантировать эксклюзивный доступ на время редактирования в памяти.

**Solution.** Lock table / flag при открытии редактирования; снятие при commit/rollback; блокирует чужие сессии.

**When to use.** Высокая вероятность конфликта; критичные финансовые документы.

**When not.** Масштаб и длительные сессии — риск «зависших» блокировок.

**Collaborating patterns.** Unit of Work, Implicit Lock.

**Implementation notes.** Таймауты владельца блокировки; админ release.

**Example sketch.**

```text
edit(id) {
  if (!lockManager.acquire(id, sessionId)) throw Locked
  return load(id)
}
```

---

### Coarse-Grained Lock / Блокировка с низкой степенью детализации

**Problem.** Блокировать каждую строку в агрегате — дорого и deadlock-prone.

**Solution.** Блокировать корневой объект (или весь aggregate), охватывая связанный граф.

**When to use.** Domain Model с кластером связанных объектов; optimistic или pessimistic на root.

**When not.** Независимые строки без общего корня.

**Collaborating patterns.** Optimistic/Pessimistic Offline Lock, Unit of Work.

**Implementation notes.** Связано с идеей aggregate consistency (концепция DDD; в PEAA — через lock root).

**Example sketch.**

```text
lock(orderId) // locks order + line items as one unit
```

---

### Implicit Lock / Неявная блокировка

**Problem.** Разработчики забывают вызывать lock/unlock явно.

**Solution.** Инфраструктура (Layer Supertype, framework) накладывает lock при load/save автоматически.

**When to use.** Единообразие offline lock в большой команде.

**When not.** Нужен явный UX «документ занят» — комбинируйте с explicit API.

**Collaborating patterns.** Pessimistic Offline Lock, Layer Supertype, Unit of Work.

**Implementation notes.** Load через locked finder; session-bound lock token.

**Example sketch.**

```text
class DomainObject extends LayerSupertype {
  onLoad() { lockPolicy.onLoad(this) }
}
```

---

## Часть II, глава 17 — Состояние сеанса (Session State)

### Client Session State / Сохранение состояния сеанса на клиенте

**Problem.** HTTP stateless; нужно хранить cart/session без server memory.

**Solution.** Сериализованное состояние в cookie/hidden field (подписанное/зашифрованное).

**When to use.** Мало данных; горизонтальное масштабирование без sticky session.

**When not.** Большие или чувствительные данные — server/DB session.

**Collaborating patterns.** Server Session State, security signing.

**Implementation notes.** Размер cookie; tamper protection.

**Example sketch.**

```text
cookie = encrypt(serialize(sessionState))
```

---

### Server Session State / Сохранение состояния сеанса на сервере

**Problem.** Больше данных сессии, чем допустимо в cookie.

**Solution.** Session id в клиенте → объект сессии в памяти сервера или cluster replicate.

**When to use.** Классический server-side session (Servlet session).

**When not.** Без sticky sessions при in-memory без репликации.

**Collaborating patterns.** Database Session State, Client Session State.

**Implementation notes.** TTL; сериализация при failover.

**Example sketch.**

```text
httpSession.setAttribute("cart", cart)
```

---

### Database Session State / Сохранение состояния сеанса в БД

**Problem.** Server memory не масштабируется или нужна durability сессии.

**Solution.** Сериализованный blob сессии в таблице по session id.

**When to use.** Кластер без shared memory; долгие сессии; recovery.

**When not.** Высокая частота записи сессии — нагрузка на БД.

**Collaborating patterns.** Server Session State.

**Implementation notes.** Периодический flush; очистка устаревших.

**Example sketch.**

```text
saveSession(id, blob) // INSERT/UPDATE session_store
```

---

## Часть II, глава 18 — Базовые типовые решения (Base Patterns)

### Gateway / Шлюз

**Problem.** Прямой доступ к внешней системе (БД, SOAP, messaging) размазан по коду.

**Solution.** Обёртка с понятным API, изолирующая foreign API.

**When to use.** Любой внешний ресурс; основа Table/Row Data Gateway.

**When not.** Замена domain model — Gateway это инфраструктура, не домен.

**Collaborating patterns.** Table Data Gateway, Row Data Gateway, Service Stub.

**Implementation notes.** Тестируйте через Service Stub.

**Example sketch.**

```text
class EmailGateway { send(to, body) { smtpClient... } }
```

---

### Mapper / Преобразователь

**Problem.** Два независимых типа представления одних данных (DB row ↔ domain object, DTO ↔ entity).

**Solution.** Отдельный класс перевода без бизнес-логики.

**When to use.** Data Mapper, DTO assembler, любой boundary translation.

**When not.** Логика домена в mapper — перенести в entity.

**Collaborating patterns.** Data Mapper, Embedded Value, Inheritance Mappers.

**Implementation notes.** Однонаправленные vs двунаправленные; thin mappers.

**Example sketch.**

```text
class PersonMapper extends Mapper {
  toDomain(row): Person
  toRow(person): Row
}
```

---

### Layer Supertype / Супертип слоя

**Problem.** Повторяющееся поведение всех объектов слоя (identity, notifications, lock hooks).

**Solution.** Базовый класс/интерфейс слоя с общими методами и политиками.

**When to use.** Domain Layer, Service Layer с единым identity/audit.

**When not.** Наследование мешает — composition (но PEAA эпоха чаще supertype).

**Collaborating patterns.** Implicit Lock, Domain Model, Service Layer.

**Implementation notes.** Не тянуть persistence в domain supertype при Data Mapper (осторожно с зависимостями).

**Example sketch.**

```text
abstract class DomainObject {
  id; registerWith(uow)
}
```

---

### Separated Interface / Отделённый интерфейс

**Problem.** Клиенты должны зависеть от интерфейса, но реализация тянет тяжёлые зависимости (compile cycle).

**Solution.** Интерфейс в пакете, который не зависит от реализации; impl в другом модуле.

**When to use.** Remote/local bisimulation; тестовые заглушки; plugin architectures.

**When not.** YAGNI для внутреннего кода без циклических зависимостей.

**Collaborating patterns.** Service Layer, Plugin, Remote Facade.

**Implementation notes.** Пакетная дисциплина (package dependency rule).

**Example sketch.**

```text
// api.jar
interface TaxService { compute(order): Money }
// impl.jar
class TaxServiceImpl implements TaxService
```

---

### Registry / Реестр

**Problem.** Глобально нужны well-known объекты (singleton services, UoW, connection).

**Solution.** Реестр как известная точка lookup (singleton или per-thread).

**When to use.** Ограниченно — тестируемость страдает; часто для UoW/Session в legacy apps.

**When not.** DI-контейнер заменяет Registry в современных apps.

**Collaborating patterns.** Unit of Work, Gateway, Service Stub.

**Implementation notes.** Singleton vs thread-local registry; избегать «бида» на Registry everywhere.

**Example sketch.**

```text
Registry.current().unitOfWork().commit()
```

---

### Value Object / Объект-значение

**Problem.** Примитивы не выражают domain concepts (диапазон дат, цвет, адрес).

**Solution.** Малый immutable объект; равенство по значениям полей, не по id.

**When to use.** Money, Address, DateRange; Embedded Value в БД.

**When not.** Сущность с жизненным циклом и id — entity.

**Collaborating patterns.** Embedded Value, Money, Special Case.

**Implementation notes.** Никаких setters; side-effect-free operations return new VO.

**Example sketch.**

```text
class DateRange {
  constructor(start, end) { assert start <= end }
  contains(d) { ... }
}
```

---

### Money / Деньги

**Problem.** float/double для денег — ошибки округления; валюта как afterthought.

**Solution.** Value Object: amount + currency; операции с согласованной валютой и rounding policy.

**When to use.** Любая финансовая доменная логика.

**When not.** Некритичные отображения — всё равно осторожно с float в домене.

**Collaborating patterns.** Value Object, Embedded Value.

**Implementation notes.** Не складывать USD и EUR без конверсии; используйте decimal.

**Example sketch.**

```text
class Money {
  amount: Decimal; currency: Currency
  add(other) { assert sameCurrency; return new Money(...) }
}
```

---

### Special Case / Частный случай

**Problem.** null checks размазаны; особые случаи (нет сотрудника, гостевой пользователь).

**Solution.** Подкласс или объект с безопасным поведением по умолчанию (Null Object pattern).

**When to use.** Альтернатива repeated null handling.

**When not.** Optional/Maybe в языке покрывает часть кейсов.

**Collaborating patterns.** Value Object, Domain Model.

**Implementation notes.** NullEmployee с no-op или default values.

**Example sketch.**

```text
class NullEmployee extends Employee {
  getName() = ""
  isNull() = true
}
```

---

### Plugin / Дополнительный модуль

**Problem.** Поведение должно подключаться в runtime (стратегия реализации), не жёстко в compile time.

**Solution.** Интерфейс + регистрация реализации при конфигурации (Separated Interface + factory).

**When to use.** ID generators, tax rules по региону, swappable adapters.

**When not.** Одна реализация навсегда.

**Collaborating patterns.** Factory, Registry, Separated Interface.

**Implementation notes.** Конфигурационный файл / DI wiring.

**Example sketch.**

```text
configure() { IdGenerator = plugin.load("com.acme.UuidGenerator") }
```

---

### Service Stub / Фиктивная служба

**Problem.** Внешняя служба недоступна, дорога или нестабильна в тестах.

**Solution.** Заменитель с тем же интерфейсом, возвращающий фиксированные или программируемые ответы.

**When to use.** Unit/integration tests; offline dev.

**When not.** Production path — только test doubles.

**Collaborating patterns.** Gateway, Separated Interface.

**Implementation notes.** Не commit stub в prod config.

**Example sketch.**

```text
class StubTaxService implements TaxService {
  compute(order) = new Money(0, "USD")
}
```

---

### Record Set / Множество записей

**Problem.** Табличные данные в памяти как first-class (курсоры, binding к UI).

**Solution.** In-memory табличная структура (ADO Recordset, DataSet) с именованными колонками и строками.

**When to use.** Table Module, .NET DataSet apps; reporting binding.

**When not.** Rich domain — объекты вместо rows.

**Collaborating patterns.** Table Module, Table Data Gateway.

**Implementation notes.** Отличие от DTO list — мутабельная табличная семантика и метаданные колонок.

**Example sketch.**

```text
rs = gateway.findAllPersons() // RecordSet
while (!rs.eof) { process(rs["name"]); rs.next() }
```

---

## Сводка: выбор паттернов (шпаргалка из PEAA)

| Вопрос | Ответ в духе PEAA |
|--------|-------------------|
| Структура доменной логики | Простая → Transaction Script; сложная → Domain Model; табличная среда → Table Module |
| API приложения | Service Layer |
| Web-архитектура | MVC |
| HTTP entry | Простой URL space → Page Controller; иначе → Front Controller |
| HTML | Маркеры в HTML → Template View; pipeline → Transform View; multi-skin → Two Step View |
| Персистентность | Простая → Gateway/Active Record; сложная → Data Mapper + UoW + Identity Map |
| Remote | Remote Facade + DTO |
| Длинные редактирования | Optimistic или Pessimistic Offline Lock; блокируйте aggregate → Coarse-Grained Lock |

---

## Паттерны вне PEAA (часто ищут рядом)

**Aggregate (агрегат)** и **Domain Event** — центральные идеи *Domain-Driven Design* (Eric Evans); в «Архитектуре корпоративных приложений» не выделены как отдельные именованные паттерны, хотя **Repository**, **Coarse-Grained Lock** и **Service Layer** хорошо стыкуются с границами агрегатов и транзакций.