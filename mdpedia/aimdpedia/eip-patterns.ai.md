---
title: "Enterprise Integration Patterns (EIP)"
source: "library/eip-patterns.md"
---

## TL;DR (Core Vector)

См. полный каталог: `library/eip-patterns.md`.

## Ядро для ИИ (Embedding Target)

# Enterprise Integration Patterns (EIP)

Reference extracted from *Enterprise Integration Patterns* (Hohpe & Woolf, 2004) / Russian edition «Шаблоны интеграции корпоративных приложений» (2007).

**Source:** `books-md/Шаблоны интеграции корпоративных приложений.md` — Appendix A (problem statements), chapters 2–11 (solutions), Appendix B (categories and pictograms).

**Total:** 65 patterns in **8 categories** (4 integration styles + 7 messaging pattern groups; Integration Styles are architectural alternatives, not messaging-specific).

---

## 1. Integration Styles (Стили интеграции)

Architectural approaches to application integration (Chapter 2). Only **Messaging** is the basis for the patterns below.

### File Transfer

| Field | Content |
|-------|---------|
| **Icon** | — |
| **Problem** | How do you integrate and exchange data between multiple applications? |
| **Solution** | One application writes data to a shared file store; others read it. Agree on file location, naming, format (often XML), locking, and refresh frequency. Minimal coupling via the file contract only. |
| **Example** | Nightly export of orders from ERP to a CSV/XML drop folder consumed by the warehouse system. |

### Shared Database

| Field | Content |
|-------|---------|
| **Icon** | — |
| **Problem** | How do you integrate and exchange data between multiple applications? |
| **Solution** | All applications read and write the same database schema designed to satisfy every consumer. Strong consistency, but tight coupling and fragile shared schema evolution. |
| **Example** | CRM and billing both updating a single `customers` table in Oracle. |

### Remote Procedure Invocation

| Field | Content |
|-------|---------|
| **Icon** | — |
| **Problem** | How do you integrate and exchange data between multiple applications? |
| **Solution** | Expose operations as remotely callable procedures (RPC, RMI, SOAP, REST with RPC style). Synchronous, tightly coupled, requires both ends to be available. |
| **Example** | Order service calls `Inventory.reserve(sku, qty)` over HTTP/SOAP. |

### Messaging

| Field | Content |
|-------|---------|
| **Icon** | — |
| **Problem** | How do you integrate and exchange data between multiple applications? |
| **Solution** | Connect applications through message channels in a messaging system. Senders and receivers are decoupled in time and location; asynchronous, buffered, often transactional delivery. Foundation for all EIP patterns in sections 2–8. |
| **Example** | Order placed event published to a queue; fulfillment, billing, and notification subscribe without the order UI waiting. |

---

## 2. Messaging Systems (Системы обмена сообщениями)

Root patterns for message-based integration (Chapter 3).

### Message Channel

| Field | Content |
|-------|---------|
| **Icon** | — |
| **Problem** | How do you connect two applications using messaging? |
| **Solution** | Connect applications with a **Message Channel**: a logical path through the messaging system from sender to receiver. One channel per type of information; channels are designed up front and hide physical transport details. |
| **Example** | Dedicated `NEW_ORDER` queue between web shop and order processing. |

```mermaid
flowchart LR
  A[Application A] -->|send| CH[Message Channel]
  CH -->|receive| B[Application B]
```

### Message

| Field | Content |
|-------|---------|
| **Icon** | — |
| **Problem** | How do you exchange data between two applications connected by a Message Channel? |
| **Solution** | Package data in a **Message** (header + body) so it can be routed, stored, and transformed independently of the sending application. |
| **Example** | JSON order payload with headers for `MessageId` and `Timestamp`. |

### Pipes and Filters

| Field | Content |
|-------|---------|
| **Icon** | — |
| **Problem** | How do you perform complex processing on a message while maintaining independence and flexibility? |
| **Solution** | Chain **Filters** (processing steps), each connected by channels. A filter reads from one channel, transforms, writes to another. Reorder or replace filters without changing endpoints. |
| **Example** | Validate → enrich tax → persist — three filters on separate channels. |

```mermaid
flowchart LR
  IN[Input Channel] --> F1[Filter 1]
  F1 --> F2[Filter 2]
  F2 --> F3[Filter 3]
  F3 --> OUT[Output Channel]
```

### Message Router

| Field | Content |
|-------|---------|
| **Icon** | — |
| **Problem** | How do you route a message to different processing steps depending on conditions? |
| **Solution** | Insert a **Message Router** that consumes from an input channel and sends to one or more output channels based on rules (content, headers, load, etc.). Generalizes conditional branching in a pipe-and-filter architecture. |
| **Example** | Router sends EU orders to `VAT_PROCESSING`, US orders to `DOMESTIC_SHIPPING`. |

### Message Translator

| Field | Content |
|-------|---------|
| **Icon** | — |
| **Problem** | How do you exchange messages between applications that use different data formats? |
| **Solution** | Place a **Message Translator** between endpoints to convert message structure and semantics from source to target format (including transport-level bridging). |
| **Example** | EDI X12 purchase order → internal canonical JSON at the boundary. |

### Message Endpoint

| Field | Content |
|-------|---------|
| **Icon** | — |

