---
title: "API Management Patterns"
skill: ["api", "governance"]
level: intermediate
source: "library/api-management-patterns.md"
embeddings:
  chunk_strategy: headings
  max_tokens: 2048
relations:
  parent: corpus/AGENT-INDEX.md
---

# API Management Patterns

## Источник (полный текст)

`library/api-management-patterns.md`

## Ядро для ИИ (Embedding Target)

> Дословный фрагмент из `library/api-management-patterns.md` (первые 120 строк, не более 24000 символов).

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


## Навигация

- [[corpus/AGENT-INDEX.md|Индекс агента]]
- [[library/INDEX.md|Библиотека (люди)]]
