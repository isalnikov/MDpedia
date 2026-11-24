# API Management Patterns

Patterns distilled from *Continuous API Management: Making the Right Decisions in an Evolving Landscape* (Medjaoui, Wilde, Mitra, Amundsen — O'Reilly). Focus: **governance, product thinking, lifecycle, and scaling API systems** — not integration messaging (EIP) or low-level HTTP recipes.

**Core premise:** Managing APIs is managing **decisions** under complexity (volume, scale, standards, teams, technology). One API can be run as a product; **many APIs** require a **system** with evolving governance.

---

## 1. Mental models

### 1.1 API three-part model

| Part | What it is | Change cost (when published) |
|------|------------|------------------------------|
| **Interface model** | Abstract behavior: protocols, messages, terminology | Highest — ripples through docs, code, clients |
| **Implementation** | Runtime code and data behind the interface | Medium |
| **Deployed instance** | Running endpoints consumers call | Medium (ops) |
| **Support resources** | Portals, samples, tooling (DX, not the contract) | Lowest — change independently when possible |

**Pattern — Classify every change:** Before a release, label the change as interface / implementation / instance / support. Interface changes need versioning, communication, and stronger governance; support resources can iterate faster.

### 1.2 Single API vs API system

- **Single API:** Product lifecycle, ten pillars, continuous improvement, team duties per stage.
- **API system:** Ecosystem of interdependent APIs — add **eight system aspects**, platform principles, shared vocabulary, and governance that **evolves** (directives → principles → collected practices).

**Pattern — Dual lens:** For each initiative, ask both: “How does this API succeed as a product?” and “How does this affect the API system?”

### 1.3 Governance definition

**Governance (руководство)** = shaping **how decisions are made and executed** — not necessarily central control. Ask: *Which decisions need governance?* and *Where should that happen?*

---

## 2. Ten pillars of API work

Pillars are **decision domains** that support the API product. Weight them by strategy; they need not be equally funded.

| # | Pillar | Govern for… |
|---|--------|-------------|
| 1 | **Strategy** | Goal aligned to org strategy; tactics that reinforce the right pillars; metrics; when to pivot or retire |
| 2 | **Design** | Interface model: terminology, style, interaction, errors, consistency with system |
| 3 | **Documentation** | Reference (“tell”) + guided learning (“teach”); explorer tools; portal |
| 4 | **Development** | Languages, frameworks, coupling design to delivery |
| 5 | **Testing** | Contract, security, performance, interoperability |
| 6 | **Deployment** | Instances, environments, release paths |
| 7 | **Security** | Often centralize Type-2 (irreversible) decisions |
| 8 | **Monitoring** | Data for strategy, SLA, and system visibility |
| 9 | **Discovery** | Findability: catalog, registry, marketing, internal evangelism |
| 10 | **Change management** | Cost and safety of change — keystone for continuous evolution |

**Pattern — Strategy-to-pillar investment map:** For each API goal (platform growth, monetize assets, harvest innovation), explicitly list which pillars get extra investment (e.g. external DX → design, documentation, discovery).

**Pattern — Pillar-weight review:** On lifecycle stage transitions (especially publication → payoff), reassess pillar spend; at system scale, map pillars to **system aspects** (see §7).

---

## 3. API as product (AaaP)

### 3.1 Product thinking triad

1. **Design thinking** — Know *who* (JTBD / “jobs to be done”) and *which problems* matter to the business, not only IT convenience.
2. **Onboarding** — Prove value quickly (docs, samples, support).
3. **Developer experience (DX)** — Sum of interactions: interface, docs, portal, support, ops signals.

**Pattern — Bezos mandate (internal = external bar):** Design and operate internal APIs as if they could be externalized — improves safety and reuse when opening the boundary.

**Pattern — Problem–business fit gate:** Do not fund APIs that only solve familiar IT chores with weak links to business OKR; require articulation of business outcome and measures.

### 3.2 Design investment gradient

Match design process depth to stakes: competitive external API → full discovery/prototype/user testing; trusted internal API → lighter loop (prototype → client app → refine).

**Pattern — Machine-readable interface:** Prefer OpenAPI (HTTP), protobuf (gRPC), etc., to link design → docs → mocks → CI.

### 3.3 Documentation dual mode

| Mode | Purpose | Typical artifacts |
|------|---------|-------------------|
| **Tell, don’t teach** | Reference facts | Error codes, schemas, generated spec |
| **Teach, don’t tell** | Task-oriented learning | Tutorials, journeys, sample apps |

**Pattern — Interactive learn loop:** API explorer with guided actions shortens feedback vs “read docs then write code.”

---

## 4. Product lifecycle (five stages)

```
Creation → Publication → Payoff → Maintenance → Retirement
```

| Stage | Character | Governance emphasis |
|-------|-------------|------------------------|
| **Creation** | Not in prod; cheap to change interface | Lock hardest-to-change parts (interface model); avoid opportunity cost of delay — “good today” vs “perfect tomorrow”; team formation |
| **Publication** | Deployed + announced; value still potential | Deploy, docs, discovery events; controlled experimentation on clients |
| **Payoff** | Usage meets strategic intent; value realized | OKR/KPI focus; change management + reliable ops (DevOps) |
| **Maintenance** | Usage flat/declining; preserve revenue | Minimal risk changes; may re-publish or new major version to recover |
| **Retirement** | Decommission strategy | Product manager–led sunsetting, migration, communication |

**Pattern — Creation gate:** Define minimum diligence before lifecycle starts (e.g. strategic goal approved, or “four people for three months”) — balance decentralization vs waste.

**Pattern — Publication trigger catalog:** Pick explicit switch events (prod deploy, portal live, registry entry, email announcement) and **usage metrics** (registered devs, call volume, doc views) before aggressive interface experiments.

**Pattern — Payoff definition per API:** Payoff is not universal — e.g. 10k paid calls/month vs “online banking uses this API once.” Revisit when business strategy shifts.

**Pattern — Lifecycle-aware change appetite:** Publication allows more interface risk than maintenance; maintenance favors stability over growth experiments.

---

## 5. Continuous improvement and release lifecycle

**Release lifecycle** = how an idea becomes a supported change; it chains all ten pillars.

**Change types and coupling:**

- Interface model changes → synchronize docs, implementations, client expectations.
- Implementation/instance can sometimes move independently.
- Support resources → fastest iteration.

**Pattern — Continuous small releases:** Cheaper change enables learning; invest in change management pillar so you don’t need “rocket launch” upfront design.

**Pattern — Consistent interface expressions:** One conceptual interface model expressed in spec, code, and docs; drift creates costly change.

**Pattern — Versioning discipline:** Treat interface versioning as a first-class governance topic (pillar 10 + design).

---

## 6. Decision governance patterns

### 6.1 When to centralize vs decentralize

Optimize each decision on:

| Factor | Centralize when… | Decentralize when… |
|--------|------------------|-------------------|
| **Optimization scope** | System-wide consistency, irreversible harm (Type-2), cross-API UX | Local context dominates quality |
| **Information** | Accurate system-wide data only at center | Local teams have best facts |
| **Talent** | Few strong decision-makers; high stakes | Enough skilled deciders per team |
| **Coordination cost** | Decision frequency overloads one group | Speed and autonomy matter more |

**Bezos decision types:** Type-1 reversible → decentralize more; Type-2 hard to reverse (e.g. security posture) → centralize.

**Pattern — Style guide vs team freedom:** Centralize *constraints* (terms, patterns) when users consume many APIs; allow local optimization inside the guardrails.

### 6.2 Six elements of a decision

Split governance per element, not only “who owns the whole decision”:

1. **Ideation** — Who must notice a decision exists?
2. **Option search** — Who defines the menu (especially for “choose from list”)?
3. **Choice** — Who picks?
4. **Approval** — Who can block?
5. **Application** — Who implements?
6. **Verification** — Who tests outcomes?

**Pattern — Menu governance:** Centralize **option search** (approved stacks, spec formats); decentralize **choice** within menu — typical in automated governance.

**Pattern — Idea regeneration:** Combat habit (always Java, always one DB) with deliberate ideation for decisions that affect system health.

### 6.3 Three reference governance schemes

| Scheme | Center of gravity | Tradeoff |
|--------|-------------------|----------|
| **Interface supervision** | Central interface design; decentralized build/deploy | Strong UX consistency; bottleneck risk; design–implementation gap |
| **Automated governance** | Central standards + automated compliance | Scale and speed; high platform investment; rigidity risk |
| **Collaborative governance** | Central goals & measurement; decentralized delivery | Needs talent everywhere; outcome-based culling of failing APIs |

**Pattern — Match scheme to maturity:** Early small program → directives/checklists; growing system → principles + automation; mature ecosystem → collaborative “shared brain” + transparent scorecards.

### 6.4 Governance evolution (organization scale)

| Scale | Governance style |
|-------|------------------|
| Small / new teams | Detailed procedures (“how to name URLs”) |
| Growing | **Principles** with rationale (e.g. cite RFCs, heuristics) |
| Large / distributed | **Harvest practices** from strong teams; recommend, don’t only dictate |

**Pattern — Practices lifecycle:** Tag guidance as experimental → established → declining → legacy; avoid locking diversity paths you’ll need later.

### 6.5 Defer commitment (evolving landscape)

In large systems, delay binding decisions until the **last responsible moment** — when further delay eliminates a valuable alternative (Lean / Poppendieck).

**Pattern — Shape-change radar:** When system **shape** changes (new sites, acquisitions, tech families), revisit pillar × aspect hotspots (strategy: variety/volume/velocity; design: visibility vs family consistency).

---

## 7. Eight aspects of an API system

Levers for long-term evolution (not a maturity ladder — multidimensional):

| Aspect | Manage… |
|--------|---------|
| **Variety** | Allowed diversity of styles/platforms; avoid infinite “shades of API” |
| **Vocabulary** | Shared terms and message patterns (e.g. Problem Details RFC 7807) |
| **Volume** | More APIs, traffic, teams — prioritize winners, retire noise, scale platforms |
| **Velocity** | Rate and *count* of changes — fast path for safe small changes; gates for big |
| **Vulnerability** | Security and failure blast radius |
| **Visibility** | Observe how APIs are built and run |
| **Versioning** | System-wide versioning rules and compatibility |
| **Volatility** | Services change at different speeds — tools and client responsibility |

**Pattern — Carrot not stick for languages:** Encourage reuse by making shared vocabularies + tooling attractive; avoid top-down bans unless necessary.

**Pattern — Express the system through APIs:** Metadata, health, catalog, policy — expose via APIs to automate at scale (“everything you need to say about an API, express through an API”).

**Pattern — Pillars × aspects matrix:** When scaling, use the book’s Table 10.1 style matrix in workshops: which pillar is stressed by which aspect *right now*.

---

## 8. Team and responsibility patterns

Eleven **duties** (map to roles as needed; one person may cover several):

**Business-facing (OKR):**

- API product manager — *what* and lifecycle ownership
- API designer — interface model and DX
- API technical writer — tell + teach artifacts
- API evangelist — internal adoption and feedback
- Developer relations (DevRel) — external adoption (when applicable)

**Technical (KPI / delivery):**

- Lead API engineer — coordinates how
- API architect — cross-API constraints, NFRs
- Frontend / portal developer — developer-facing surfaces
- Backend developer — implementation fidelity
- QA — approval testing, security, scale tests
- DevOps — deploy, monitor, release hygiene

**Pattern — Stage-primary duties:**

| Stage | Primary | Secondary (examples) |
|-------|---------|----------------------|
| Creation | PM, designer, lead engineer | Architect, backend for prototype |
| Publication | PM, tech writer, DevOps | Evangelist, portal dev |
| Payoff | DevOps, PM (change prioritization) | Continued discovery/docs refresh |
| Maintenance | DevOps, DevRel/evangelist, architect (system drift) | Minimal feature crew |
| Retirement | PM (sunset strategy) | DevOps teardown, comms |

**Pattern — Squad composition, not role inflation:** Start with overlapping generalists; specialize as variety and volume grow (chapter 1 scaling arc).

**Pattern — Matrix membership:** Shared designers, architects, or guilds across API squads (Spotify-style tribes/squads/guilds) without forcing 1:1 duty-to-FTE.

---

## 9. Measurement patterns

- **OKR** — Outcomes (business); best on payoff stage and product direction.
- **KPI** — Operational indicators (reliability, usage, quality); feed monitoring pillar and system visibility.

**Pattern — Hubbard-style measurement design:** What decision does this metric drive? Is perfect precision worth the cost? Where can observation lie? Pick tooling that runs beside the API in production.

**Pattern — System-scale KPI shift:** Early APIs: reliability and adoption; at hundreds of APIs: system health (variety, duplication, time-to-publish, policy compliance).

---

## 10. Strategy and landscape decision catalog

**Actionable prompts** (from pillar “key decisions” and system growth chapters):

| Topic | Decision |
|-------|----------|
| Strategy | Who sets goal/tactic — local vs centralized approval? |
| Strategy | Standardized impact reporting vs per-team metrics? |
| Strategy | Who may change or kill a goal for a live API? |
| Design | Central style guide vs local interface optimization? |
| Design | Mandatory spec format for sharing and CI? |
| Documentation | Central portal vs federated; quality gates in CI? |
| Discovery | Single registry contract; required metadata fields? |
| Change | Compatibility rules; deprecation clocks; consumer notification |
| System growth | Principles/protocols/patterns instead of one tech stack everywhere |
| System growth | Invest in automation when manual governance hits volume wall |

**Pattern — Tactic follows environment shift:** When org strategy, competition, or regulation changes, strategy pillar leads; change-management capacity limits how fast you can pivot.

**Pattern — Good enough publish:** On creation stage, optimize the interface model most; don’t miss business window — align with publication payoff metrics.

**Pattern — Safe vs bold release classes:** At high velocity, define fast lanes (non-breaking, docs, support) vs slow lanes (interface model, security, cross-API vocabulary).

---

## 11. Anti-patterns (from the book’s warnings)

- **Ungoverned decisions** — Quality collapses as headcount grows.
- **Over-centralization at scale** — Bottleneck, frustration, wrong local choices delayed.
- **Under-centralization for Type-2** — Security and incompatible styles across APIs.
- **Monolithic process document** — Fails when technology variety is a strength.
- **Frozen preferences** — “Only REST/only JSON forever” blocks evolving user needs.
- **Data-table APIs without JTBD** — Technically fine, strategically weak.
- **Ignoring support resources** — Same pillar weight as interface for external DX.
- **Same lifecycle rules for one API and the whole system** — Misses aspect-driven governance.

---

## 12. Quick reference: related frameworks

| Framework | Use |
|-----------|-----|
| Ten pillars | Work breakdown and governance conversations per API |
| Product lifecycle (5) | Funding, risk, and team focus over time |
| Release lifecycle | Continuous improvement mechanics |
| Six decision elements | Fine-grained centralize/decentralize |
| Eight system aspects | Portfolio evolution and platform investment |
| AaaP + DX + JTBD | Why an API exists and for whom |

---

## Source

Based on Russian edition text in `books-md/nepreriv_razvit.md` (*Непрерывное развитие API*, O'Reilly / Питер, 2020), translating and restructuring the authors' models for pattern-oriented reuse.