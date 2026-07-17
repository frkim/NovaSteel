# Implementation Plan: AI-Powered Steel Production Optimization Platform

**Branch**: `001-steel-optimization-platform` | **Date**: 2026-06-23 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-steel-optimization-platform/spec.md`

**Constitution**: NovaSteel Platform Constitution v1.0.0 (`.specify/memory/constitution.md`)

## Summary

NovaSteel "Project Ignition" is a cloud-native, EU-resident, event-driven data-and-AI
platform that turns plant telemetry, production/maintenance records, and energy-market
signals into **human-reviewed recommendations** across four capability pillars —
predictive maintenance (P1), energy-dispatch optimization (P2), quality control (P3),
and GenAI knowledge capture (P4). The platform is **decision-support only**: it never
actuates plant equipment (FR-015, Constitution I).

The technical approach concentrates the solution in **Microsoft Fabric** (OneLake
medallion lake, Data Engineering/Spark, Data Science/MLflow, Real-Time Intelligence,
Power BI Direct Lake) for the data-and-ML plane and **Microsoft Foundry** (Agent
Service, Foundry IQ grounding, Azure OpenAI/Foundry Models, AI Services: Speech,
Language, Document Intelligence, Content Safety) for the AI plane, fed by a minimal
**Azure IoT Hub + Event Hubs** cloud-direct ingestion path and a small **Azure
Functions + Container Apps** compute footprint. Telemetry flows one-way OT→IT
(Constitution IV); all data stays in EU regions enforced by Azure Policy (Constitution
III); every prediction, recommendation, and human decision produces an immutable audit
record with Purview lineage (Constitution II); shared contracts in `libs/` with golden
fixtures are the test-first single source of truth (Constitution VIII); and a
first-class **steel-factory simulator** Container App provides synthetic telemetry
carrying a preserved synthetic-origin marker on the same ingestion path as real OT
(Constitution IX).

Delivery is phased per spec priority, P1 first: prove the ≥21-day furnace-lining
warning at a single pilot furnace before multi-line and four-country scale-out
(SC-003, SC-009, Constitution X).

## Technical Context

**Language/Version**:
- Python 3.13 — Microsoft Fabric Spark notebooks (data engineering, Data Science RUL/quality
  models), the energy-dispatch solver and Functions, and `libs/novasteel_core` (the Python
  mirror of the shared contracts).
- C# / .NET 10 (`net10.0`) — `libs/NovaSteel.Contracts` (+ `.Tests`), platform services, and the
  `apps/steel_factory_simulator` Container App (C# / Razor).
- KQL — Fabric Real-Time Intelligence (Eventhouse / KQL Database, Activator rules) on the
  sub-second furnace hot path.
- Bicep — all infrastructure under `infrastructure/` (subscription-scope `main.bicep` →
  `resources.bicep` → `modules/*`).

**Primary Dependencies**:
- Microsoft Fabric (OneLake, Data Factory, Data Engineering/Spark, Data Science + MLflow
  registry/endpoints/drift, Real-Time Intelligence Eventstreams/KQL/Activator, Power BI
  Direct Lake).
- Microsoft Foundry (Agent Service, Foundry IQ grounding/RAG, Azure OpenAI / Foundry
  Models, AI Services: Speech, Language, Document Intelligence, Content Safety).
- Azure IoT Hub + Event Hubs (cloud-direct ingestion, no edge runtime).
- Azure Functions + Azure Container Apps (Energy-Dispatch Agent + Simulator).
- Energy-dispatch solver library (Python MILP/heuristic — solver selection resolved in
  research.md), pydantic v2 (`novasteel_core`), xUnit + pytest test stacks.
- Governance/ops: Entra ID, Key Vault (CMK/BYOK), Azure Policy, Purview, Defender for
  Cloud, Azure Monitor / Application Insights, VNet + Private Link, ADLS Gen2 / OneLake +
  Blob. CI/CD: GitHub Actions.

**Storage**:
- **OneLake medallion lake** (Bronze/Silver/Gold Delta) is the primary data plane;
  ADLS Gen2 / Blob for raw landing and large binary artifacts (interview audio).
- **Fabric Real-Time Intelligence Eventhouse (KQL)** for the hot-path time series.
- **Application/audit state store** for workflow state, human-decision records, and
  immutable audit metadata: a single relational store — **Azure SQL Database** vs
  **Azure Database for PostgreSQL Flexible Server** (both in-scope). research.md selects
  one with rationale (default lean: Azure SQL, append-only audit tables). MLflow model
  registry lives inside Fabric Data Science.

**Testing**:
- pytest (`libs/novasteel_core`, Fabric notebooks logic, energy solver).
- xUnit (`libs/NovaSteel.Contracts.Tests`, .NET services, simulator).
- Golden-fixture contract tests shared by C# + Python (`libs/fixtures`).
- Fabric data-quality checks (Bronze→Silver→Gold validation), model
  evaluation/drift gates (Constitution VIII), and integration tests for agent decision
  logging (audit-record completeness).
- Replayable, deterministic failure fixtures from the simulator drive the spec
  Independent Tests (e.g. degrading-furnace replay → ≥21-day RUL warning).

**Target Platform**:
- Azure **EU regions only** — Sweden Central / West Europe / Germany West Central
  (NFR-002, Constitution III), pinned by Azure Policy.
- Private access to all PaaS via **VNet + Private Link**; secrets in Key Vault with
  customer-managed keys (BYOK/CMK). Managed PaaS only — **no virtual machines**.

**Project Type**: **Multi-workload monorepo.** Four independently shippable pillar
workloads share one OneLake data plane, the Foundry AI layer, the shared `libs/`
contracts, and a common governance/observability plane. The steel-factory simulator is
a first-class deployable Container App (the device side of IoT Hub).

**Performance Goals**:
- ≥ **21-day** furnace-lining failure advance warning (SC-003, FR-002).
- **−14%** energy/ton (SC-001), **−22%** CO₂ (SC-002), **+8%** high-grade yield (SC-004),
  each vs a frozen trailing-12-month per-site baseline normalized for product mix and
  volume.
- **Sub-second** furnace alerting on the RTI hot path (Eventstream→KQL→Activator).
- GenAI answers **100%** source-cited or declined (SC-008); ≥70% of operator questions
  answerable, ≥80% of retiring operators interviewed (SC-007).

**Constraints**:
- Decision-support only — no equipment actuation under any pillar (FR-015, Constitution I).
- One-way OT→IT — no reverse command path may exist (NFR-004, Constitution IV).
- EU residency, zero egress, policy-enforced (NFR-002, Constitution III).
- Immutable audit + Purview lineage for every prediction/recommendation/decision
  (FR-017, NFR-003, Constitution II).
- Degraded/missing/stale telemetry MUST be flagged, never presented as current
  (FR-022, Constitution VI).
- Synthetic telemetry carries a preserved synthetic-origin marker end-to-end and is
  never presentable as real (Constitution IX).
- Retention: predictions/recommendations/decisions audit = 10 years; energy/ETS = 5
  years; operator-interview personal (non-audit) content erasable on request; all
  configurable per record class and per site (NFR-008, FR-024).

**Scale/Scope**:
- 4 sites (LU/DE/BE/ES); blast furnaces, rolling mills, utilities.
- External feeds: day-ahead electricity spot price + grid carbon intensity per national
  market.
- MES/ERP/EAM-CMMS and SCADA/historian remain **systems of record** — the platform reads
  and proposes, never replaces.
- Phased rollout: one pilot furnace/site → multi-line → four countries, with strict
  per-site data isolation (FR-023, Constitution VII).

## Constitution Check

*GATE: evaluated pre-Phase-0 (initial) and re-evaluated post-Phase-1 (design). Principles
I–IX are NON-NEGOTIABLE merge-blocking gates; X is advisory.*

### Initial evaluation (pre-Phase-0)

| # | Principle | Verdict | How the design satisfies it |
|---|-----------|---------|------------------------------|
| I | Human-in-the-Loop | **PASS** | No actuation path anywhere; every Prediction/Recommendation entity transitions only via a recorded `HumanDecision`. Work orders are *proposed* to MES/EAM, never auto-executed. Time-sensitive plans lapse to `Unactioned` (data-model state machine). |
| II | End-to-End Traceability | **PASS** | Immutable `AuditRecord` entity (append-only, 10-yr retention) links inputs/evidence, model/logic version, output, reviewer, timestamp, rationale. Purview captures sensor→feature→model→report lineage; audit tables are append-only with no UPDATE/DELETE grant. |
| III | EU Data Residency | **PASS** | `main.bicep` restricts `location` to `swedencentral`/`westeurope`/`germanywestcentral`; research.md adds an Azure Policy `allowedLocations` deny assignment so non-EU regions fail deployment. All stores (OneLake, KQL, SQL, Blob) are EU-pinned. |
| IV | One-Way OT→IT Boundary | **PASS** | Ingestion is cloud-direct IoT Hub → Event Hubs → Fabric; no module, function, or simulator path writes back toward OT/SCADA. IoT Hub is configured device→cloud only (no cloud-to-device/direct-method usage). |
| V | Scoped, Unified Stack | **PASS** | Only the `1_azure_services.md` "Final Decision — Scoped Service Set" is used. The two out-of-scope modules (`machine-learning.bicep` = Azure ML, `search.bicep` = AI Search) have been **removed (CT-1 COMPLETE)**, including all wiring in `resources.bicep`/`rbac.bicep`/`README.md`; `az bicep build` is clean. No other excluded service is introduced. |
| VI | Explainability & Responsible AI | **PASS** | `Prediction`/`Recommendation` carry confidence + contributing-evidence fields; GenAI answers grounded via Foundry IQ with mandatory citations and decline-on-no-source; all generative output passes Content Safety; telemetry `Quality` + freshness flags drive reduced-confidence presentation. |
| VII | RBAC & Per-Site Isolation | **PASS** | Entra ID least-privilege per persona (operator/maintenance/energy/quality/exec-ESG/compliance-DPO); `Site` is a first-class scoping dimension on every entity; per-site row/workspace isolation prevents onboarded↔not-onboarded bleed. |
| VIII | Contract-First, Test-First | **PASS** | `libs/NovaSteel.Contracts` + `libs/novasteel_core` are the single source of truth, validated against `libs/fixtures` golden files by both xUnit and pytest. TDD: contract, integration (agent decision logging), and model eval/drift tests precede ship. |
| IX | Synthetic-Data Integrity | **PASS (with additive contract change)** | The simulator emits contract-conformant telemetry on the SAME IoT Hub path as real OT. Requires an additive provenance marker (`Origin{Real,Synthetic}` + `SourceId`) on `TelemetryReading`, propagated Bronze→Silver→Gold and into every Prediction/AuditRecord, so synthetic data is queryable and never presentable as real — see Complexity Tracking CT-2 (additive, non-breaking). |

**Initial gate result: PASS** — proceed to Phase 0. Two tracked actions (CT-1 removal of
excluded modules, CT-2 additive provenance marker) are recorded in Complexity Tracking;
neither introduces an excluded service or weakens a principle.

### Post-Design re-evaluation (post-Phase-1)

Re-checked after research.md, data-model.md, contracts/, and quickstart.md were
produced:

| # | Principle | Verdict | Post-design confirmation |
|---|-----------|---------|---------------------------|
| I | Human-in-the-Loop | **PASS** | data-model state machines (`Prediction`→`HumanDecision`, `Recommendation`/`EnergyPlan`→approve/adjust/reject/lapse) encode mandatory human gates; contracts carry no actuation verb. |
| II | End-to-End Traceability | **PASS** | `audit-record.schema.json` is append-only with full lineage fields; data-model marks audit immutability and 10-yr retention; Purview lineage documented in research.md. |
| III | EU Data Residency | **PASS** | research.md "EU residency enforcement" decision = Azure Policy `allowedLocations`; no store outside EU. |
| IV | One-Way OT→IT | **PASS** | contracts model only device→cloud messages; no reverse/command contract exists. |
| V | Scoped, Unified Stack | **PASS** | CT-1 removal task is sequenced first in Phase 2 notes; research.md "no standalone AI Search" and "ML in Fabric Data Science" decisions confirm scope. |
| VI | Explainability & Responsible AI | **PASS** | `prediction.schema.json`/`recommendation.schema.json` require `confidence`, `evidence`, `modelVersion`; knowledge answers require `citations[]`; freshness/quality flags modeled. |
| VII | RBAC & Per-Site Isolation | **PASS** | every schema carries `site`; data-model documents per-site isolation + persona roles. |
| VIII | Contract-First, Test-First | **PASS** | contracts/ aligns 1:1 with `libs/` + `libs/fixtures`; quickstart runs dotnet + pytest golden-fixture tests first. |
| IX | Synthetic-Data Integrity | **PASS** | every telemetry/derived schema includes `origin` + `sourceId`; quickstart's P1 replay uses synthetic-marked data that stays queryable as synthetic. |

**Post-design gate result: PASS** — no new violations introduced by the design. Complexity
Tracking remains limited to CT-1 (compliance cleanup) and CT-2 (additive contract change).

## Project Structure

### Documentation (this feature)

```text
specs/001-steel-optimization-platform/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output — technical decisions
├── data-model.md        # Phase 1 output — entities + medallion mapping
├── quickstart.md        # Phase 1 output — build/run/deploy/validate guide
├── contracts/           # Phase 1 output — JSON Schemas for payloads & interfaces
│   ├── telemetry-reading.schema.json
│   ├── market-signal.schema.json
│   ├── simulator-device-message.schema.json
│   ├── prediction.schema.json
│   ├── recommendation.schema.json
│   ├── energy-plan.schema.json
│   ├── human-decision.schema.json
│   └── audit-record.schema.json
├── checklists/          # Pre-existing
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created by /speckit.plan)
```

### Source Code (repository root) — monorepo tree to EXTEND

This feature **extends the existing monorepo**; it does not introduce a parallel tree.
Existing paths are marked `(exists)`; new paths are marked `(new)`.

```text
infrastructure/                         (exists) — Bicep IaC, subscription scope
├── main.bicep                          (exists) main → resources.bicep
├── main.bicepparam                     (exists)
├── resources.bicep                     (exists) MODIFY — remove search + machineLearning blocks (CT-1)
├── README.md                           (exists) MODIFY — drop search/ML rows + RP line (CT-1)
└── modules/
    ├── container-apps.bicep            (exists) — hosts Energy-Dispatch Agent + Simulator
    ├── container-registry.bicep        (exists)
    ├── defender.bicep                  (exists)
    ├── event-hubs.bicep                (exists)
    ├── fabric.bicep                    (exists) — OneLake + RTI + Data Science capacity
    ├── foundry.bicep                   (exists) — Agent Service + IQ + AI Services + Content Safety
    ├── functions.bicep                 (exists) — Energy-Dispatch Functions
    ├── identity.bicep                  (exists)
    ├── iot-hub.bicep                   (exists) — cloud-direct ingestion (device→cloud only)
    ├── keyvault.bicep                  (exists) — CMK/BYOK + per-device keys
    ├── monitoring.bicep                (exists) — Azure Monitor / App Insights
    ├── purview.bicep                   (exists) — lineage
    ├── rbac.bicep                      (exists) MODIFY — remove search/ML params + role assignments (CT-1)
    ├── storage.bicep                   (exists) — ADLS Gen2 / OneLake landing + Blob
    ├── machine-learning.bicep          (exists) DELETE — Azure ML excluded (CT-1)
    ├── search.bicep                    (exists) DELETE — AI Search excluded (CT-1)
    ├── policy.bicep                    (new)    — Azure Policy EU allowedLocations (Constitution III)
    └── app-state.bicep                 (new)    — Azure SQL app/audit state store (research.md)

libs/                                   (exists) — shared contracts (single source of truth)
├── NovaSteel.Contracts/               (exists) C# readonly record structs
│   ├── TelemetryReading.cs            (exists) MODIFY — add Origin + SourceId (CT-2)
│   ├── MarketSignal.cs                (exists)
│   ├── Enums.cs                       (exists) MODIFY — add Origin{Real,Synthetic} enum (CT-2)
│   ├── NovaSteelJson.cs               (exists)
│   ├── Transport.cs                   (exists) — ITelemetrySink/Source, InMemoryTelemetryChannel
│   ├── Prediction.cs                  (new)
│   ├── Recommendation.cs             (new)
│   ├── EnergyPlan.cs                  (new)
│   ├── HumanDecision.cs              (new)
│   └── AuditRecord.cs                (new)
├── NovaSteel.Contracts.Tests/         (exists) xUnit — extend golden-fixture coverage
├── novasteel_core/                    (exists) Python pydantic mirror
│   └── novasteel_core/models.py       (exists) MODIFY — add origin/source_id + new models (CT-2)
└── fixtures/                          (exists) golden contract fixtures (C# + Python)
    ├── telemetry_reading.json         (exists) MODIFY — add origin/sourceId (CT-2)
    ├── market_signal.json             (exists)
    ├── prediction.json                (new)
    ├── recommendation.json            (new)
    ├── energy_plan.json               (new)
    ├── human_decision.json            (new)
    └── audit_record.json              (new)

apps/                                   (exists)
└── steel_factory_simulator/           (exists, README only) BUILD — first-class Container App
    ├── README.md                      (exists)
    ├── src/                            (new)  C# / Razor web UI + sensor engine
    │   ├── Sensors/                    (new)  furnace/mill/utility synthetic generators
    │   ├── Ingestion/                  (new)  IoT Hub device client (managed identity / KV per-device keys)
    │   ├── Web/                        (new)  start/stop, sensor overview, incident/failure injection
    │   └── Replay/                     (new)  deterministic replayable failure cases (degrading furnace)
    ├── tests/                          (new)  xUnit — contract conformance vs libs/fixtures
    └── Dockerfile                      (new)

workloads/                              (new) — four pillar workloads (Fabric notebooks + agents)
├── p1_predictive_maintenance/         (new)  physics-informed furnace-lining RUL (Fabric Data Science)
├── p2_energy_dispatch/                (new)  MILP/heuristic solver (Functions/Container Apps)
├── p3_quality_control/                (new)  quality prediction + SPC (Fabric Data Science)
└── p4_knowledge_capture/              (new)  Speech→Language→Doc Intel→Foundry IQ→Agent

.github/workflows/                      (exists) — GitHub Actions CI/CD (build/test/deploy)
```

**Structure Decision**: **Multi-workload monorepo.** The four pillars are independently
shippable workloads under `workloads/` that share the OneLake data plane, the Foundry AI
layer, the `libs/` contracts + `libs/fixtures` golden set, and the
governance/observability plane wired in `infrastructure/`. The steel-factory simulator
is a first-class deployable Container App (the IoT Hub device side). All new code extends
the existing `infrastructure/`, `libs/`, and `apps/` directories — no parallel tree is
introduced. P1 ships first (Constitution X / SC-009).

## Complexity Tracking

> Records (a) the compliance cleanup mandated by Constitution V and (b) the additive
> contract change mandated by Constitution IX. Neither introduces an excluded service nor
> weakens a NON-NEGOTIABLE principle; both reduce or preserve complexity.

| ID | Item | Why needed | Simpler alternative rejected because |
|----|------|------------|--------------------------------------|
| CT-1 | **Remove `machine-learning.bicep` (Azure ML) and `search.bicep` (Azure AI Search)** from infrastructure, including all wiring in `resources.bicep`, `rbac.bicep`, and `infrastructure/README.md` | Both are on the `1_azure_services.md` **Explicitly Excluded** list (Constitution V). ML lives inside **Microsoft Fabric Data Science**; grounding/RAG is provided by **Foundry IQ**. Leaving them deployed introduces forbidden services, fragments governance/lineage, and adds cost. | "Leave them deployed but unused" rejected: an excluded service present in IaC is itself a Constitution V violation and a maintenance/audit liability; "keep AI Search as optional RAG" rejected because Foundry IQ already covers grounding (AI Search is "Later/optional", not in the scoped set). |
| CT-2 | **Additive provenance marker** on `TelemetryReading`: `Origin{Real,Synthetic}` enum + `SourceId` string, propagated end-to-end (contracts, fixtures, Bronze→Silver→Gold, Prediction/AuditRecord) | Constitution IX requires every synthetic reading to carry an unambiguous, preserved synthetic-origin marker queryable wherever data lands, so the simulator's data can never masquerade as real. | "Tag synthetic data only at the simulator / in a side table" rejected: provenance must be preserved *end-to-end* and queryable at every landing point; a non-contract side channel breaks under joins/aggregations and at the Gold/KPI/audit layer. The change is **additive and non-breaking** (new fields with defaults), so it does not justify a new pattern or service. |

### CT-1 — ordered removal task (must yield a clean `az bicep build`)

This sequence is the authoritative cleanup checklist for the implementation/tasks phase
(verified against the current files):

1. `infrastructure/resources.bicep`: delete the `search` module block (~lines 137–145)
   and the `machineLearning` module block (~lines 157–169).
2. `infrastructure/resources.bicep`: delete the `names.search` entry (~line 45) and the
   now-unused `names.mlWorkspace` / `names.mlStorage` entries (~lines 39, 47) if no longer
   referenced.
3. `infrastructure/resources.bicep`: delete outputs `searchName` (~line 235) and
   `machineLearningWorkspaceName` (~line 238).
4. `infrastructure/resources.bicep`: in the `rbac` module params, remove `searchName`,
   `mlPrincipalId`, and `searchPrincipalId` (~lines 212, 214, 217).
5. `infrastructure/modules/rbac.bicep`: remove params `searchName`, `searchPrincipalId`,
   `mlPrincipalId`; remove the `search` existing resource; remove role-assignment
   resources `mlStorage`, `searchStorageReader`, `mlKv`, `searchOpenAi`,
   `foundrySearchReader`, `foundrySearchContributor`, `mlAcr`; drop the now-unused
   `searchIndexDataReader`, `searchServiceContributor`, and (if unused) `storageBlobDataReader`
   role IDs from the `roles` map.
6. `infrastructure/README.md`: remove the `search.bicep` and `machine-learning.bicep`
   table rows and the `Microsoft.MachineLearningServices` resource-provider line.
7. Delete the files `infrastructure/modules/search.bicep` and
   `infrastructure/modules/machine-learning.bicep`.
8. Verify: `az bicep build --file infrastructure/main.bicep` (and lint) must succeed with
   no unresolved references; `az deployment sub validate` against `main.bicepparam` must
   pass.

## Phase notes

### Phase 0 — Research (output: research.md)

Resolved technical decisions (each as Decision / Rationale / Alternatives considered):
physics-informed RUL modelling in Fabric Data Science; energy-dispatch MILP vs heuristic
+ solver choice runnable in Functions/Container Apps; RTI hot-path design for sub-second
alerts + Activator; Foundry IQ grounding/RAG over the procedure library (why no standalone
AI Search); OneLake medallion layout; synthetic-origin provenance propagation pattern;
app/audit state store (Azure SQL vs PostgreSQL); KPI baseline computation (frozen
trailing-12-month, normalized); EU residency enforcement via Azure Policy. **All
NEEDS CLARIFICATION resolved — none remain** (the spec carries zero open clarifications;
the Technical Context above has no unresolved markers).

### Phase 1 — Design & Contracts (outputs: data-model.md, contracts/, quickstart.md)

- **data-model.md** defines all spec Key Entities (Site, Furnace/Asset, TelemetryReading
  with provenance, Prediction, Recommendation, HumanDecision/Approval, WorkOrder,
  EnergyPlan, Heat/Coil, Procedure/KnowledgeItem, OperatorInterview, AuditRecord,
  User/Role) with fields, relationships, state machines, and Bronze/Silver/Gold mapping;
  notes the additive provenance change (CT-2) and audit-record immutability.
- **contracts/** holds JSON Schemas aligned 1:1 with `libs/NovaSteel.Contracts` +
  `libs/fixtures` (now including the provenance marker): telemetry, market signal,
  simulator→IoT Hub device message, prediction, recommendation, energy-plan,
  human-decision, audit-record.
- **quickstart.md** documents building `libs/` (dotnet + pytest), running the simulator
  locally against the in-memory transport, deploying infrastructure
  (`az deployment sub create` with `main.bicep` + `main.bicepparam`), and running the P1
  furnace-RUL Independent Test (replay a degrading furnace → ≥21-day warning).
- Agent context (`.github/copilot-instructions.md`, between the SPECKIT markers) updated
  to point at this plan.

### Phase 2 — Tasks (NOT produced here)

`/speckit.tasks` will generate `tasks.md`. The CT-1 removal sequence above is sequenced
**first** (compliance gate), followed by CT-2 contract changes + fixtures, then P1→P4
workload tasks per spec priority.
