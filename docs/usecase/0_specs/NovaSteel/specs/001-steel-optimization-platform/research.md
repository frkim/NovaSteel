# Phase 0 Research: AI-Powered Steel Production Optimization Platform

**Feature**: `001-steel-optimization-platform` | **Date**: 2026-06-23 | **Plan**: [plan.md](./plan.md)

This document resolves the open technical decisions for the implementation plan. The
feature spec carries **zero open `[NEEDS CLARIFICATION]`** markers (all four clarifications
were resolved in the 2026-06-23 session); the decisions below resolve *engineering* choices
left implicit by the spec and Technical Context. Each is recorded as **Decision /
Rationale / Alternatives considered**, with constraints from the constitution and the
`1_azure_services.md` scoped service set.

---

## R1 — Physics-informed furnace-lining RUL modelling (P1)

**Decision**: Build the remaining-useful-life (RUL) model in **Microsoft Fabric Data
Science** as a **hybrid physics-informed model**: a thermal/heat-balance feature layer
(derived from thermocouple temperature, heat flux, and energy-balance residuals around
the lining) feeds a gradient-boosted / survival-style degradation model, with a
physics-derived wear index as both a feature and a monotonic constraint. Train,
register, and version models with **MLflow inside Fabric Data Science**; serve via a
Fabric ML endpoint and a batch-scoring notebook on the Silver/Gold tables. Emit a
`Prediction` with time-to-failure, confidence, and the contributing thermal signals as
evidence (FR-002, FR-003).

**Rationale**: A pure black-box model cannot guarantee the ≥21-day lead time is grounded
in physical degradation; a pure first-principles model is brittle to sensor noise and
unmodeled effects. The hybrid approach gives explainable, physically-plausible evidence
(Constitution VI) while learning residual patterns from history. Keeping training and the
registry inside Fabric Data Science satisfies Constitution V (no Azure ML) and keeps
lineage in one platform (Constitution II). The degrading-furnace replay fixture validates
the ≥21-day warning deterministically (SC-003).

**Alternatives considered**:
- *Azure Machine Learning workspace* — **rejected**: explicitly excluded (Constitution V,
  CT-1); ML belongs in Fabric Data Science.
- *Pure deep-learning sequence model (LSTM/Transformer)* — rejected for the pilot: heavier
  data/ops burden, weaker physical explainability, and overkill for a single pilot furnace;
  may be revisited at scale.
- *Pure physics simulation (FEA thermal model)* — rejected: too brittle/slow for
  continuous scoring and not self-calibrating to real wear history.

---

## R2 — Energy-dispatch optimisation: MILP vs heuristic + solver (P2)

**Decision**: Model energy dispatch as a **Mixed-Integer Linear Program (MILP)**:
minimize Σ(energy cost + carbon penalty) over schedulable energy-intensive jobs subject
to production-deadline, capacity, and sequencing constraints, driven by the day-ahead
spot-price and grid-carbon curves. Implement with **Python + PuLP using the bundled CBC
solver** (pure-Python install, no native service), packaged in `workloads/p2_energy_dispatch`
and runnable in **both Azure Functions and Azure Container Apps**. Provide a **greedy
carbon/price-ranked heuristic as a deterministic fallback** for fast intra-day re-plans
and for when the MILP is infeasible (returns the best feasible schedule + the violated
constraint). Every plan is a `Recommendation`/`EnergyPlan` requiring human approval
(FR-008) and shows energy/ton, CO₂, and cost vs the unoptimized baseline (FR-007).

**Rationale**: The problem is naturally linear with integer on/off + slot assignment
decisions — a textbook MILP. CBC via PuLP is open-source, has no native dependency that
would block Functions/Container Apps deployment, and is adequate for the pilot's job
counts. The heuristic guarantees a sub-second answer for intra-day updates (FR-008 edge
case "updated market prices arrive intra-day") and a graceful, explainable result when the
MILP can't satisfy a deadline (FR-008 deadline-breach flag). No excluded service is
introduced (Constitution V).

**Alternatives considered**:
- *Commercial solver (Gurobi/CPLEX)* — rejected for the pilot: licensing cost/complexity;
  CBC suffices at pilot scale and stays dependency-light.
- *Heuristic only* — rejected: cannot prove the −14%/−22% targets are near-optimal or
  reason about coupled deadline constraints.
- *Azure Stream Analytics / Fabric-only scheduling* — rejected: not an optimization engine;
  Stream Analytics is excluded (Constitution V).

---

## R3 — Real-Time Intelligence hot path for sub-second furnace alerts

**Decision**: Furnace telemetry flows IoT Hub → Event Hubs → **Fabric Real-Time
Intelligence**: an **Eventstream** lands raw readings into an **Eventhouse (KQL
Database)** and, in parallel, **Fabric Activator** evaluates KQL alert rules
(threshold + short-window slope on thermocouple temp / heat flux) to fire sub-second
furnace alerts to the maintenance persona. The KQL Database mirrors to OneLake (Bronze)
for the batch/ML path. Degraded/missing/stale readings are detected by a freshness/quality
rule and surfaced as reduced-confidence/unavailable, never as current (FR-022,
Constitution VI).

**Rationale**: RTI embeds the ADX/Eventhouse engine and Activator natively inside Fabric,
giving sub-second KQL evaluation without introducing standalone Azure Data Explorer or
Stream Analytics (both excluded, Constitution V). One platform keeps lineage and
governance unified (Constitution II). The hot path (alerting) is decoupled from the cold
path (RUL training) so neither blocks the other.

**Alternatives considered**:
- *Standalone Azure Data Explorer* — rejected: excluded; RTI provides the same engine.
- *Azure Stream Analytics* — rejected: excluded; RTI Eventstreams/KQL cover it.
- *Custom Functions polling Event Hubs for alerting* — rejected: higher latency, more code,
  weaker than Activator's native rule engine.

---

## R4 — GenAI grounding/RAG over the procedure library (P4) — no standalone AI Search

**Decision**: Implement knowledge retrieval with **Microsoft Foundry IQ** as the grounding
layer over the procedure library, orchestrated by a **Foundry Agent Service** agent. The
capture pipeline is **Azure AI Speech (speech-to-text) → Language (structuring/PII) →
Document Intelligence (document parsing) → Foundry IQ index → Agent answer**, with
**mandatory citations** and **decline-on-no-grounding** (FR-013, FR-014, SC-008). All
generative output passes **Azure AI Content Safety** (Constitution VI). Answers and newly
structured procedures route through human review before becoming authoritative (FR-014).
**No standalone Azure AI Search resource is provisioned.**

**Rationale**: Foundry IQ already provides grounding/retrieval with citations; AI Search
is listed as "Later/optional" and is *not* in the scoped service set, so adding it would
violate Constitution V (and is the basis for removing `search.bicep`, CT-1). Keeping
retrieval inside Foundry unifies the AI plane, simplifies governance, and gives
citation-backed answers natively.

**Alternatives considered**:
- *Standalone Azure AI Search vector index* — rejected: excluded/optional (Constitution V,
  CT-1); Foundry IQ covers grounding.
- *Foundry models with no grounding (parametric answers)* — rejected: would fabricate and
  violate the cite-or-decline rule (Constitution VI, FR-014).

---

## R5 — OneLake medallion layout

**Decision**: Single **OneLake** lakehouse with a **medallion architecture**:
- **Bronze** — raw, append-only landing of IoT Hub/Event Hubs telemetry, market signals,
  and ingested interview/document artifacts, **preserving the `origin`/`sourceId`
  provenance marker** verbatim (Constitution IX).
- **Silver** — cleaned, conformed, deduplicated, quality-flagged entities (TelemetryReading,
  MarketSignal, Heat/Coil) partitioned by **`site`** (Constitution VII isolation) and time;
  freshness/quality columns computed here (FR-022).
- **Gold** — feature tables for ML, SPC aggregates, KPI marts (energy/ton, CO₂/ton,
  high-grade yield) computed against the **frozen per-site baseline** (see R8), and
  Power BI Direct Lake datasets.

Provenance, `site`, and `quality` columns propagate through every layer. Purview captures
lineage across the layers (Constitution II).

**Rationale**: Medallion is the canonical Fabric pattern and cleanly separates raw
fidelity (audit/provenance) from curated analytics (KPIs/ML). Per-site partitioning
enforces phased-rollout isolation at the storage layer. One lake keeps lineage unified.

**Alternatives considered**:
- *Direct-to-Gold (no Bronze)* — rejected: loses raw audit fidelity and replayability, and
  would make provenance/erasure handling harder (FR-024).
- *Separate lakes per pillar* — rejected: fragments lineage/governance; pillars share one
  data plane by design.

---

## R6 — Synthetic-origin provenance propagation (Constitution IX)

**Decision**: Add an **additive provenance marker** to the telemetry contract:
`Origin{Real,Synthetic}` (enum, default `Real`) **and** a `SourceId` string (e.g.
`sim:steel_factory_simulator@v1` or `ot:LU-historian`). It is carried in
`libs/NovaSteel.Contracts.TelemetryReading`, mirrored in `libs/novasteel_core`, added to
the golden fixtures, emitted by the simulator's IoT Hub device message, and **propagated
Bronze→Silver→Gold and into every Prediction and AuditRecord**. Gold KPI baselines and
dashboards **filter to `origin = Real`** (or label synthetic explicitly) so synthetic data
is **never presentable as real** and is **queryable wherever it lands** (Constitution IX).
The change is **additive/non-breaking** (new fields with defaults) — see CT-2.

**Rationale**: Constitution IX requires the marker preserved end-to-end and queryable at
every landing point; putting it *in the contract* is the only way it survives joins,
aggregations, KPI computation, and audit. A new enum + string is the minimal, schema-first
expression of this (Constitution VIII).

**Alternatives considered**:
- *Tag only at the simulator / IoT Hub message property* — rejected: lost at the first
  transform that doesn't copy message metadata; not queryable at Gold/audit.
- *Side provenance table joined by key* — rejected: fragile under aggregation, easy to drop,
  and weaker than an in-row, always-present column.
- *Boolean `isSynthetic` only* — rejected in favor of `Origin` enum + `SourceId` so the
  *specific* generator/source is auditable, not just true/false.

---

## R7 — Application / audit state store: Azure SQL vs PostgreSQL

**Decision**: Use **Azure SQL Database** (single, EU-pinned) as the application/workflow
and **immutable audit** store. Audit data lives in **append-only tables** (INSERT-only;
no UPDATE/DELETE grant to app identities; optionally **temporal/ledger tables** for
tamper-evidence), with the 10-year/5-year/erasable retention classes (NFR-008) enforced
by per-record-class, per-site retention policy. Workflow state (Prediction/Recommendation/
EnergyPlan lifecycle, HumanDecision) lives in normal transactional tables.

**Rationale**: Both Azure SQL and PostgreSQL Flexible Server are in-scope; the default-lean
choice (Constitution X / YAGNI) is Azure SQL because its **ledger / append-only temporal**
capability directly supports the immutable-audit requirement (Constitution II) with the
least custom code, integrates cleanly with Entra ID auth and Private Link, and is a single
managed PaaS with strong EU-region support. PostgreSQL is a valid alternative and can be
swapped without contract changes (audit schemas in `contracts/` are store-agnostic).

**Alternatives considered**:
- *Azure Database for PostgreSQL Flexible Server* — viable and in-scope; rejected as default
  only because Azure SQL ledger tables give tamper-evidence with less custom work. Keep as
  the documented alternative.
- *Store audit only in OneLake Delta* — rejected: Delta supports updates/deletes by design,
  so immutability/tamper-evidence is weaker than ledger tables; OneLake still holds the
  analytical copy and lineage, but the system-of-record audit lives in the relational store.
- *Cosmos DB* — rejected: not needed (no global-scale/multi-model requirement); adds
  complexity beyond YAGNI.

---

## R8 — KPI baseline computation (frozen trailing-12-month, normalized)

**Decision**: For each site, at onboarding, compute and **freeze** the pre-platform
baseline as the **trailing 12 calendar months** of production immediately preceding
go-live, **normalized for product mix and production volume** (energy and CO₂ as per-ton
per-product-grade; yield as per high-grade product line). The frozen baseline reference
period and normalization factors are stored as an immutable record in the audit trail
(Assumptions §; clarification 2026-06-23). All Gold KPI marts (SC-001/002/004) compute
improvement vs this frozen, per-site baseline and **exclude `origin = Synthetic`** data
from real-KPI reporting (Constitution IX).

**Rationale**: A full year absorbs seasonality; normalization ensures improvements reflect
platform impact, not product-mix shifts; freezing per site supports phased rollout and
auditability (Constitution II/VII). This directly encodes the resolved clarification.

**Alternatives considered**:
- *Rolling baseline* — rejected: moving target makes the −14%/−22%/+8% claims unverifiable.
- *Single global baseline across sites* — rejected: breaks per-site isolation and ignores
  site/product differences.

---

## R9 — EU data-residency enforcement (Constitution III)

**Decision**: Enforce residency as **policy-as-code**: a new `infrastructure/modules/policy.bicep`
assigns the built-in **"Allowed locations"** policy (and "Allowed locations for resource
groups") restricting deployments to **`swedencentral`, `westeurope`, `germanywestcentral`**
at subscription/resource-group scope, in **Deny** effect, so any non-EU resource fails
deployment. `main.bicep` already `@allowed`-restricts `location` to these three regions;
the policy makes residency enforced rather than convention.

**Rationale**: NFR-002/Constitution III require residency enforced by Azure Policy, not
developer discipline — violations must fail deployment, not reach production. SC-006 demands
zero non-EU instances.

**Alternatives considered**:
- *Rely on the `@allowed` param only* — rejected: a parameter is bypassable and doesn't
  cover resources that pick a region implicitly; policy is the constitutional requirement.
- *Manual review* — rejected: human vigilance is explicitly disallowed by Constitution III.

---

## R10 — One-way OT→IT ingestion & simulator authentication (Constitution IV, IX)

**Decision**: Ingestion is **cloud-direct via Azure IoT Hub** with **device→cloud
messaging only** — no cloud-to-device messages, direct methods, or desired-twin command
patterns are used or exposed, so no reverse path into OT can exist (Constitution IV). The
**steel-factory simulator** is the device side: it authenticates to IoT Hub via
**managed identity where supported and per-device SAS keys stored in Key Vault**, and
publishes telemetry on the **same ingestion path as real OT**, carrying the
`origin = Synthetic` / `sourceId` marker (Constitution IX). The simulator web UI supports
start/stop, sensor overview, and incident/failure injection, and ships deterministic
replayable failure cases (e.g. a degrading furnace) used by the Independent Tests.

**Rationale**: Cloud-direct IoT Hub with strictly device→cloud usage structurally enforces
the one-way boundary (no command channel implemented = none to exploit). Per-device keys in
Key Vault + managed identity keep secrets out of code (Additional Constraints). Putting the
simulator on the real ingestion path proves the synthetic-integrity guarantee end-to-end.

**Alternatives considered**:
- *IoT Edge / IoT Operations* — rejected: excluded (Constitution V); no plant-side edge in
  scope (NFR-004).
- *Simulator writes straight to Event Hubs/OneLake* — rejected: would bypass the real
  ingestion path and weaken the Constitution IX guarantee that synthetic data travels the
  same route as real OT.

---

## Summary of decisions

| ID | Topic | Decision (short) |
|----|-------|------------------|
| R1 | RUL model | Hybrid physics-informed model in Fabric Data Science + MLflow |
| R2 | Energy dispatch | MILP (PuLP/CBC) + greedy heuristic fallback, Functions/Container Apps |
| R3 | Hot path | RTI Eventstream → Eventhouse (KQL) + Activator, sub-second alerts |
| R4 | Knowledge RAG | Foundry IQ grounding + Agent; cite-or-decline; **no standalone AI Search** |
| R5 | Lake layout | OneLake medallion Bronze/Silver/Gold, per-site partitioning |
| R6 | Provenance | Additive `Origin{Real,Synthetic}` + `SourceId`, propagated end-to-end |
| R7 | State/audit store | Azure SQL (append-only/ledger audit); PostgreSQL is the documented alt |
| R8 | KPI baseline | Frozen trailing-12-month per site, normalized; exclude synthetic |
| R9 | EU residency | Azure Policy "Allowed locations" Deny (3 EU regions) |
| R10 | Ingestion/sim auth | Cloud-direct IoT Hub device→cloud only; sim via MI + KV per-device keys |

**All decisions stay within the `1_azure_services.md` scoped service set; the only
deviations recorded are CT-1 (remove the two excluded modules) and CT-2 (additive
provenance marker) in plan.md → Complexity Tracking.**
