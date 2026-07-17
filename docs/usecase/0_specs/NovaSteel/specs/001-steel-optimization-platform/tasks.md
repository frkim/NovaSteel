---
description: "Task list for AI-Powered Steel Production Optimization Platform"
---

# Tasks: AI-Powered Steel Production Optimization Platform

**Feature**: `001-steel-optimization-platform` | **Branch**: `001-steel-optimization-platform`

**Input**: Design documents from `specs/001-steel-optimization-platform/`

**Prerequisites**: plan.md (required), spec.md (user stories P1–P4), research.md (R1–R10), data-model.md (14 entities + medallion), contracts/ (8 JSON Schemas), quickstart.md, `.specify/memory/constitution.md` (Principles I–IX NON-NEGOTIABLE, X advisory)

**Tests**: REQUIRED. Constitution VIII (Contract-First, Test-First) mandates contract tests, integration tests for agent decision logging, and model evaluation/drift gates authored and passing **before** each workload ships. Test/data-quality/eval-drift gate tasks therefore precede implementation within every story.

**Organization**: Tasks are grouped by user story (pillar) so each is an independently completable, demoable, and testable increment. P1 ships first (Constitution X / SC-009).

## Format: `[ID] [P?] [Story] Description`

- **[X]** prefix = already implemented and verified in this repo (see "Current State" below); not re-issued.
- **[P]**: Can run in parallel (different files / no dependency on incomplete tasks).
- **[Story]**: US1 (P1 maintenance), US2 (P2 energy), US3 (P3 quality), US4 (P4 knowledge). Setup / Foundational / Polish tasks carry no story label.
- Every task names a concrete repo path or Fabric/Foundry artifact target, and maps to FR/NFR/SC IDs where applicable.

## Current State (already completed — verified)

The shared foundation is implemented and verified: `dotnet build` 0 warnings; `dotnet test` 22 passed; `pytest` 14 passed; `az bicep build` exit 0. The following are marked **[X]** below and are **not** re-issued:

- **CT-1** — removed `machine-learning.bicep` + `search.bicep` and all wiring in `resources.bicep` / `rbac.bicep` / `README.md` (Constitution V). Verified: both module files absent.
- **CT-2** — additive provenance marker `Origin{Real,Synthetic}` + `SourceId` on `TelemetryReading` across `libs/NovaSteel.Contracts` (C#), `libs/novasteel_core` (Python), `libs/fixtures` (golden), with tests.
- **New entities/contracts** — `Prediction`, `Recommendation`, `EnergyPlan`, `HumanDecision`, `AuditRecord` in C# + Python + enums + golden fixtures, matching `contracts/*.schema.json`, with xUnit + pytest tests.
- **Infra** — `policy.bicep` (EU `allowedLocations` deny, Constitution III) and `app-state.bicep` (Azure SQL serverless audit/state store, Entra-only auth, opt-in) created and wired into `main.bicep`/`resources.bicep`; builds clean.
- **Simulator buildout** — `apps/steel_factory_simulator` (ASP.NET Core Razor app, deterministic `SensorReadingEngine` emitting 100% `Origin.Synthetic` + `SourceId`, device→cloud-only `IotHubTelemetrySink` rejecting non-synthetic telemetry and reading secrets via Key Vault + managed identity, degrading-furnace replay scenario), xUnit tests, Dockerfile, `.github/workflows/simulator.yml` (actions SHA-pinned), `NovaSteel.slnx` updated, `infrastructure/modules/container-app-simulator.bicep` + `resources.bicep` wiring, and corrected `iot-hub.bicep` device→cloud comments.

The **remaining** work below requires a live Azure / Fabric / Foundry environment and is the bulk of this plan.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Repository structure and build/test scaffolding shared by every workload.

- [X] T001 Monorepo structure (`infrastructure/`, `libs/`, `apps/`) established per plan.md Project Structure
- [X] T002 `libs/NovaSteel.Contracts/` (C# readonly records) + `libs/NovaSteel.Contracts.Tests/` (xUnit) + `NovaSteelJson` camelCase serializer scaffolded
- [X] T003 `libs/novasteel_core/` (pydantic v2 mirror, `to_camel` parity) scaffolded
- [X] T004 `libs/fixtures/` golden-fixture set established as the single source of truth (Constitution VIII)
- [X] T005 `NovaSteel.slnx` solution wired (contracts, tests, simulator)
- [ ] T006 [P] Create the four pillar workload directories with stub READMEs: `workloads/p1_predictive_maintenance/README.md`, `workloads/p2_energy_dispatch/README.md`, `workloads/p3_quality_control/README.md`, `workloads/p4_knowledge_capture/README.md`, plus the shared data-plane dir `platform/README.md`
- [ ] T007 [P] Add CI workflow `/.github/workflows/ci-libs.yml` (SHA-pinned actions) running `dotnet test libs/NovaSteel.Contracts.Tests` + `pytest libs/novasteel_core` on every PR (Constitution VIII gate in CI)
- [ ] T008 [P] Add `platform/requirements.txt` (PySpark/Fabric notebook deps, `pulp`, `mlflow`, pydantic) and `platform/.flake8`/`pyproject.toml` lint config shared by `workloads/` Python

**Checkpoint**: Repo skeleton for all four workloads + shared platform exists; library CI is green.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared data-and-AI plane (contracts, compliance, live infra, ingestion, medallion, audit store) that MUST be complete before ANY pillar can ship.

**⚠️ CRITICAL**: No user-story work can begin until this phase is complete.

### 2a. Compliance & contract gates — COMPLETED

- [X] T009 CT-1: deleted `infrastructure/modules/search.bicep` + removed `search` block/outputs/`names.search` from `resources.bicep` (Constitution V)
- [X] T010 CT-1: deleted `infrastructure/modules/machine-learning.bicep` + removed `machineLearning` block/outputs/`names.mlWorkspace`/`names.mlStorage` from `resources.bicep` (Constitution V)
- [X] T011 CT-1: removed `searchName`/`searchPrincipalId`/`mlPrincipalId` params, the `search` resource, and ML/search role assignments + unused role IDs from `infrastructure/modules/rbac.bicep`
- [X] T012 CT-1: removed `search.bicep` / `machine-learning.bicep` rows + `Microsoft.MachineLearningServices` RP line from `infrastructure/README.md`; verified `az bicep build --file infrastructure/main.bicep` clean
- [X] T013 CT-2: added `Origin{Real,Synthetic}` enum + `origin`/`sourceId` to `libs/NovaSteel.Contracts/{TelemetryReading.cs,Enums.cs}` and mirrored in `libs/novasteel_core/novasteel_core/models.py` (default `Real`/`""`) (Constitution IX)
- [X] T014 CT-2: updated `libs/fixtures/telemetry_reading.json` with `origin`/`sourceId`; golden-fixture round-trip passes in xUnit + pytest
- [X] T015 [P] Implemented `Prediction`, `Recommendation`, `EnergyPlan`, `HumanDecision`, `AuditRecord` in C# (`libs/NovaSteel.Contracts/*.cs`) + Python (`libs/novasteel_core`) + enums, matching `contracts/*.schema.json`
- [X] T016 [P] Added golden fixtures `libs/fixtures/{prediction,recommendation,energy_plan,human_decision,audit_record}.json` + xUnit/pytest parity tests
- [X] T017 [P] Created `infrastructure/modules/policy.bicep` (Azure Policy `allowedLocations` Deny → `swedencentral`/`westeurope`/`germanywestcentral`) wired into `main.bicep` (Constitution III, R9, NFR-002)
- [X] T018 [P] Created `infrastructure/modules/app-state.bicep` (Azure SQL serverless, Entra-only auth, append-only audit/state, opt-in) wired into `resources.bicep` (R7)
- [X] T019 Simulator buildout `apps/steel_factory_simulator/` (Razor UI, `SensorReadingEngine`, device→cloud-only `IotHubTelemetrySink`, degrading-furnace replay) + xUnit + Dockerfile + `container-app-simulator.bicep` wiring + corrected `iot-hub.bicep` comments (Constitution IV, IX, R10)

### 2b. Live platform provisioning — REMAINING

- [ ] T020 Deploy infrastructure at subscription scope: `az deployment sub create --location swedencentral --template-file infrastructure/main.bicep --parameters infrastructure/main.bicepparam`; capture outputs (`foundryEndpoint`, `keyVaultName`, `dataLakeName`, `fabricCapacityName`) (depends on T012/T017/T018)
- [ ] T021 [P] Provision-verify Fabric capacity + workspace + OneLake lakehouse from `infrastructure/modules/fabric.bicep` output; create `platform/onelake/lakehouse.config.json` recording workspace/lakehouse IDs (R5)
- [ ] T022 [P] Provision-verify Azure SQL audit/state DB; apply append-only schema migration `platform/audit/schema.sql` (ledger/temporal audit tables, no UPDATE/DELETE grant to app identity; workflow-state tables for Prediction/Recommendation/EnergyPlan/HumanDecision) (FR-017, NFR-003, NFR-008, Constitution II)
- [ ] T023 [P] Deploy Key Vault CMK/BYOK + Private Link baseline from `infrastructure/modules/keyvault.bicep`; store per-device IoT keys + service secrets; verify managed-identity access (Additional Constraints)

### 2c. Constitution acceptance gates on the live platform — REMAINING

- [ ] T024 Acceptance test: attempt `az deployment sub validate --location eastus ...` and assert it is **denied** by the `allowedLocations` policy → record evidence in `platform/compliance/eu-residency-evidence.md` (Constitution III, NFR-002, SC-006)
- [ ] T025 Acceptance test: assert IoT Hub is provisioned **device→cloud only** (no cloud-to-device / direct-method / desired-twin command surface) → record in `platform/compliance/one-way-ot-it-evidence.md` (Constitution IV, NFR-004)
- [ ] T025a Acceptance test (Human-in-the-Loop / no-actuation): assert that **no workload exposes any actuation, cloud-to-device, command, or MES/OT write-back path** — static scan of all workloads/services + an integration assertion that no code path can trigger a physical/operational action without a recorded `HumanDecision`; record evidence in `platform/compliance/no-actuation-evidence.md` (Constitution I, **FR-015**, NFR-001, SC-005)

### 2d. Shared ingestion hot path + medallion (blocks all stories) — REMAINING

- [ ] T026 Data-quality gate FIRST: author `platform/medallion/tests/test_provenance_propagation.py` asserting `origin`/`sourceId`/`site`/`quality` survive Bronze→Silver→Gold; runs red before T028–T031 exist (Constitution VIII/IX)
- [ ] T027 Configure hot path: IoT Hub → `infrastructure/modules/event-hubs.bicep` → Fabric **Eventstream** `platform/rti/eventstream-telemetry.json` landing readings into the RTI **Eventhouse (KQL DB)** `platform/rti/eventhouse.kql` (R3, FR-018)
- [ ] T028 Bronze landing notebook `platform/medallion/bronze_telemetry.py`: append-only raw IoT/Event Hubs telemetry into OneLake, **preserving `origin`/`sourceId` verbatim** (R5, Constitution IX)
- [ ] T029 Silver notebook `platform/medallion/silver_telemetry.py`: dedup, conform, compute freshness/`quality` flags, partition by `site`+time; flag missing/delayed/out-of-order as reduced-confidence/unavailable (FR-022, Constitution VI/VII)
- [ ] T030 Gold feature/KPI scaffolding `platform/medallion/gold_marts.py`: feature tables + KPI marts that **exclude `origin=Synthetic`** from real KPIs and label synthetic explicitly (R8, Constitution IX)
- [ ] T031 [P] Fabric Data Factory batch ingestion `platform/ingestion/df_mes_erp_eam.json` for MES/ERP/EAM-CMMS (read/propose only — systems of record stay authoritative); land Heat/Coil + work-order context to Bronze (FR-019, Assumptions)
- [ ] T032 [P] Bronze→Silver→Gold data-quality checks `platform/medallion/data_quality.py` (schema/range/null/freshness) wired as a gate; make T026 pass green (Constitution VIII, FR-022)
- [ ] T033 [P] Activator freshness/quality rule `platform/rti/activator-freshness.kql` firing reduced-confidence/unavailable signals on stale/missing telemetry (FR-022, Constitution VI)

### 2e. Shared governance & access foundation (minimum for any story) — REMAINING

- [ ] T034 Entra RBAC baseline + per-site isolation scaffolding `platform/governance/rbac.md` + Fabric workspace/row-level `site` security: persona roles (operator/maintenance/energy/quality/exec-ESG/compliance-DPO), `siteScope` enforcement so onboarded↔not-onboarded sites never bleed (NFR-005, FR-023, Constitution VII)
- [ ] T035 Purview lineage baseline `platform/governance/purview-baseline.md`: register OneLake + Azure SQL sources so sensor→feature→model→report lineage is captured from day one (Constitution II, NFR-003)
- [ ] T036 [P] Audit-write helper `platform/audit/audit_writer.py` (+ C# `libs/NovaSteel.Contracts` consumers) that appends an immutable `AuditRecord` (matching `audit-record.schema.json`) for every state transition, carrying `origin` provenance (FR-017, Constitution II/IX)
- [ ] T037 [P] KPI baseline computation `platform/kpi/freeze_baseline.py`: frozen trailing-12-month per-site baseline normalized for product mix/volume; store immutable baseline record + `baselineFrozenAt` (R8, SC-001/002/004, Constitution II/VII)

**Checkpoint**: Live EU-pinned platform deployed; synthetic telemetry flows the real IoT Hub path into Bronze→Silver→Gold with provenance preserved; audit store, RBAC, lineage, and KPI-baseline machinery are ready. Pillars can now begin (in parallel if staffed).

---

## Phase 3: User Story 1 - Predictive Furnace-Lining Maintenance (Priority: P1) 🎯 MVP

**Goal**: Continuously analyze furnace thermal signatures, predict furnace-lining RUL, and raise a ≥21-day advance warning with contributing evidence for human confirm/reject, recorded immutably — no equipment actuation. (FR-001..004, SC-003)

**Independent Test**: Replay the degrading-furnace scenario from the simulator → platform raises a `LiningFailureRisk` `Prediction` with `timeToFailureDays >= 21` at least 21 days before the scripted failure, with evidence + `modelVersion`, `origin=Synthetic` preserved; a `HumanDecision` is recorded and an immutable `AuditRecord` appended. (quickstart §4)

### Tests / gates for User Story 1 (author FIRST — Constitution VIII) ⚠️

- [ ] T038 [P] [US1] Contract test `workloads/p1_predictive_maintenance/tests/test_prediction_contract.py` validating emitted predictions against `contracts/prediction.schema.json` (evidence non-empty, confidence∈[0,1], modelVersion set) (FR-003, Constitution VI)
- [ ] T039 [P] [US1] Model evaluation/drift gate `workloads/p1_predictive_maintenance/tests/test_rul_eval_drift.py`: asserts ≥21-day lead on the labeled degrading-furnace fixture (SC-003) and registers a drift threshold (Constitution VIII)
- [ ] T040 [US1] P1 Independent integration test `workloads/p1_predictive_maintenance/tests/test_p1_independent.py` (xUnit `Category=P1Independent` + pytest) encoding the full quickstart §4 flow: replay → predict → confirm → audit; runs red before implementation (SC-003, FR-002/004/016/017)

### Implementation for User Story 1

- [ ] T041 [P] [US1] Physics-informed feature engineering notebook `workloads/p1_predictive_maintenance/physics_features.py` (Fabric Data Engineering): heat-flux, wear-rate, spectral, energy-balance residuals on Silver/Gold; emits Gold feature table with `site`/`origin` preserved (R1, FR-001)
- [ ] T042 [US1] RUL regression + "failure within 21 days" classifier `workloads/p1_predictive_maintenance/rul_train.py` in Fabric Data Science; MLflow register/version + endpoint + drift baseline (R1, FR-002) — depends on T041
- [ ] T043 [US1] Batch/endpoint scoring `workloads/p1_predictive_maintenance/run_rul_scoring.py`: emits a `Prediction` (kind `LiningFailureRisk`, `timeToFailureDays`, confidence, `evidence`, `modelVersion`, `inputWindowRef`, propagated `origin`) per `prediction.schema.json` — depends on T042
- [ ] T044 [US1] Sub-second warning surface: Activator rule `workloads/p1_predictive_maintenance/activator-lining-risk.kql` + Power BI tile showing the ≥21-day warning with contributing evidence to the maintenance persona (FR-002/003, R3, Constitution VI)
- [ ] T045 [US1] Human confirm/reject flow recording `HumanDecision` (`human-decision.schema.json`) → workflow-state store; supports proposing (never auto-creating) a `WorkOrder` to MES/EAM in `workloads/p1_predictive_maintenance/decision_service.py` (FR-004, NFR-001, Constitution I)
- [ ] T046 [US1] Wire every P1 transition (`Raised→UnderReview→Confirmed|Rejected|Lapsed`) through the shared `audit_writer` → immutable `AuditRecord` with inputs/modelVersion/rationale/`origin` (FR-017, SC-005, Constitution II)
- [ ] T047 [US1] No-degradation suppression: assert normal-bound telemetry raises no prediction (anti-alarm-fatigue) in `workloads/p1_predictive_maintenance/tests/test_no_false_alarm.py` (spec AS#4, edge case "alarm fatigue")
- [ ] T047a [US1] Sub-21-day lead-time escalation: when a degradation signal appears with **< 21 days** of lead time, raise an escalated high-priority warning (distinct from the standard ≥21-day path) and route it for expedited human review; encode in `workloads/p1_predictive_maintenance/tests/test_short_lead_escalation.py` (spec edge case "Prediction earlier or later than the 21-day target", FR-002)
- [ ] T048 [US1] Run the Independent Test (T040) end-to-end via the simulator degrading-furnace replay → make T038–T040 green (SC-003)

**Checkpoint**: P1 is independently demoable — replay → ≥21-day warning with evidence → recorded human decision → immutable audit, EU-resident, synthetic-tagged. **MVP deliverable.**

---

## Phase 4: User Story 2 - Energy Dispatch Optimization (Priority: P2)

**Goal**: Propose a human-approved energy-intensive job schedule that lowers €/ton and CO₂/ton vs the frozen baseline while respecting production deadlines, with full rationale and trade-offs. (FR-005..008, SC-001/002)

**Independent Test**: Given a day-ahead price curve, grid-carbon forecast, and pending jobs with deadlines → platform returns an `EnergyPlan` reducing modeled energy cost + CO₂ vs the unoptimized baseline, respecting deadlines (breaches flagged), with a recorded approval. (spec US2 Independent Test)

### Tests / gates for User Story 2 (author FIRST — Constitution VIII) ⚠️

- [ ] T049 [P] [US2] Contract test `workloads/p2_energy_dispatch/tests/test_energy_plan_contract.py` against `contracts/energy-plan.schema.json` (baselineComparison present, solver enum, deadlineBreaches modeled) (FR-007/008)
- [ ] T050 [P] [US2] Solver eval gate `workloads/p2_energy_dispatch/tests/test_solver_optimality.py`: MILP result beats unoptimized baseline on cost+CO₂ and the heuristic fallback returns a feasible schedule + violated constraint when infeasible (R2, SC-001/002)
- [ ] T051 [US2] Independent integration test `workloads/p2_energy_dispatch/tests/test_p2_independent.py`: price curve + carbon forecast + jobs → plan with savings + deadline-breach flag + recorded approval; runs red first (FR-008)

### Implementation for User Story 2

- [ ] T052 [P] [US2] MILP solver `workloads/p2_energy_dispatch/milp.py` (Python + PuLP/CBC): minimize Σ(energy cost + carbon penalty) s.t. deadline/capacity/sequencing constraints (R2, FR-006)
- [ ] T053 [P] [US2] Greedy carbon/price-ranked heuristic fallback `workloads/p2_energy_dispatch/heuristic.py` for sub-second intra-day re-plans + infeasible-MILP fallback (R2, FR-008 edge case)
- [ ] T054 [US2] Inputs adapter `workloads/p2_energy_dispatch/inputs.py`: consume RTI live signals + Fabric energy forecast + day-ahead spot price + grid carbon (`market-signal.schema.json`) per national market (FR-005/020) — depends on T031/T029
- [ ] T055 [US2] Constraint/safety guard `workloads/p2_energy_dispatch/guard.py`: enforce production deadlines + furnace limits; flag `deadlineBreaches`, never present a breaching plan as compliant; human-in-the-loop required (FR-008, NFR-001, Constitution I) — depends on T052/T053
- [ ] T056 [US2] Host as Azure Functions + Container Apps `workloads/p2_energy_dispatch/function_app/` emitting an `EnergyPlan` with `expectedEnergyPerTon`/`expectedCo2PerTon`/`expectedCostEur` + `baselineComparison` vs frozen baseline (FR-007, R8) — depends on T037/T054/T055
- [ ] T057 [US2] Publish plan + rationale to Power BI for energy-manager review; record approve/adjust/reject as `HumanDecision`; lapse-on-no-decision before horizon (`EnergyPlan.status=Lapsed`) (FR-008, Constitution I edge case)
- [ ] T058 [US2] Wire EnergyPlan transitions through `audit_writer` → immutable `AuditRecord` (assumptions used captured) (FR-017, SC-005, Constitution II)
- [ ] T059 [US2] Cross-pillar conflict surfacing `workloads/p2_energy_dispatch/conflicts.py`: populate `conflictsWith` when an energy slot collides with a P1 maintenance window or P3 quality constraint — surfaced for human arbitration, never auto-resolved (FR-021, Constitution I)
- [ ] T060 [US2] Run the Independent Test (T051) → make T049–T051 green; record KPI attribution toward SC-001 (−14% energy) / SC-002 (−22% CO₂)

**Checkpoint**: P2 is independently demoable alongside P1 — optimized, human-approved, deadline-aware energy plan with baseline-relative savings and audit.

---

## Phase 5: User Story 3 - Quality Prediction & Process Guidance (Priority: P3)

**Goal**: Predict quality outcomes for in-progress heats/coils, raise SPC drift alerts, and surface reviewable process-adjustment `Recommendation`s with rationale; link predicted-vs-actual per Heat/Coil. (FR-009..011, SC-004)

**Independent Test**: Feed process data for heats with known outcomes → platform predicts out-of-spec risk, raises SPC drift alerts, surfaces a reviewable recommendation with rationale, records the operator/engineer decision, and links predicted vs actual. (spec US3 Independent Test)

### Tests / gates for User Story 3 (author FIRST — Constitution VIII) ⚠️

- [ ] T061 [P] [US3] Contract test `workloads/p3_quality_control/tests/test_quality_contracts.py` against `contracts/prediction.schema.json` (kind `QualityOutcome`/`SpcDrift`) + `contracts/recommendation.schema.json` (rationale present) (FR-009/010)
- [ ] T062 [P] [US3] Model eval/drift gate `workloads/p3_quality_control/tests/test_quality_eval_drift.py`: predicts out-of-spec risk on labeled heats; SPC alert fires on injected drift (FR-009)
- [ ] T063 [US3] Independent integration test `workloads/p3_quality_control/tests/test_p3_independent.py`: heats with known outcomes → prediction + SPC alert + reviewable recommendation + recorded decision + predicted-vs-actual link; runs red first (SC-004)

### Implementation for User Story 3

- [ ] T064 [P] [US3] Quality feature build `workloads/p3_quality_control/quality_features.py` on Silver Heat/Coil (process params per grade), `site`/`origin` preserved (FR-009) — depends on T029/T031
- [ ] T065 [US3] Quality prediction model `workloads/p3_quality_control/quality_train.py` in Fabric Data Science; MLflow register/version + drift baseline (FR-009, R1-style) — depends on T064
- [ ] T066 [P] [US3] SPC engine `workloads/p3_quality_control/spc.py`: control-chart drift detection per grade → `Prediction` kind `SpcDrift`, sets Heat `spcState` (FR-009)
- [ ] T067 [US3] Recommendation service `workloads/p3_quality_control/recommend.py`: emit reviewable process-adjustment `Recommendation` with rationale + expected yield impact (FR-010, Constitution VI) — depends on T065/T066
- [ ] T068 [US3] Predicted-vs-actual linkage `workloads/p3_quality_control/link_outcomes.py`: associate `predictedQuality` with `actualQuality` per Heat/Coil for yield tracking + model-quality review (FR-011)
- [ ] T069 [US3] Human confirm/reject → `HumanDecision` linked to the affected Heat/Coil; wire transitions through `audit_writer` → immutable `AuditRecord` (FR-010, FR-017, SC-005, Constitution I/II)
- [ ] T070 [US3] Run the Independent Test (T063) → make T061–T063 green; record KPI attribution toward SC-004 (+8% high-grade yield)

**Checkpoint**: P3 independently demoable — quality prediction + SPC drift + reviewed recommendation + traceable predicted-vs-actual.

---

## Phase 6: User Story 4 - GenAI Operator Knowledge Capture & Retrieval (Priority: P4)

**Goal**: Capture retiring-operator interviews (speech-to-text), structure into a citation-backed procedure library, and answer operator questions via Foundry IQ grounding + Agent Service — always cited, Content-Safety-filtered, human-review-gated, declining when ungrounded. (FR-012..014, SC-007/008)

**Independent Test**: Record a sample interview → transcribed + structured into the library; ask an operational question → answer returns with citations and a human-review step; a question with no source is declined, not fabricated. (spec US4 Independent Test)

### Tests / gates for User Story 4 (author FIRST — Constitution VIII) ⚠️

- [ ] T071 [P] [US4] Contract test `workloads/p4_knowledge_capture/tests/test_knowledge_contract.py` against `contracts/recommendation.schema.json` for Knowledge: `citations[]` required, `contentSafetyPassed` true, decline-on-empty-citations → `status=Rejected` (FR-013/014, SC-008)
- [ ] T072 [P] [US4] Grounding eval gate `workloads/p4_knowledge_capture/tests/test_grounding_cite_or_decline.py`: cited answer when source exists; **declines** when no grounded source (no fabrication) (FR-014, SC-008)
- [ ] T073 [US4] Independent integration test `workloads/p4_knowledge_capture/tests/test_p4_independent.py`: interview → transcript → KnowledgeItem → cited answer + human-review gate; ungrounded question declined; runs red first (SC-007/008)

### Implementation for User Story 4

- [ ] T074 [P] [US4] Capture pipeline `workloads/p4_knowledge_capture/capture_pipeline.py`: Azure AI **Speech** (speech-to-text) → **Language** (structuring/PII) → **Document Intelligence** (parsing) → `OperatorInterview` (audio in erasable Blob) + structured `KnowledgeItem` to OneLake procedure library (FR-012, R4)
- [ ] T075 [US4] Foundry IQ grounding index `workloads/p4_knowledge_capture/foundry_iq_index.json` over the procedure library (no standalone AI Search — Constitution V, R4) — depends on T074
- [ ] T076 [US4] Foundry Agent Service answerer `workloads/p4_knowledge_capture/agent/` returning answers with **mandatory `citations[]`**; decline-on-no-source (FR-013/014, SC-008) — depends on T075
- [ ] T077 [US4] Content Safety gate `workloads/p4_knowledge_capture/agent/content_safety.py`: all generative output passes Azure AI Content Safety; set `contentSafetyPassed` (Constitution VI) — depends on T076
- [ ] T078 [US4] Human-review gate `workloads/p4_knowledge_capture/review.py`: reviewer approve/edit/reject before a `KnowledgeItem`/answer becomes `Authoritative`; `HumanDecision` + immutable `AuditRecord` (FR-014, Constitution I/II)
- [ ] T079 [P] [US4] Surface experience in **Teams + Copilot** `workloads/p4_knowledge_capture/experience/` (cited answers, decline behavior visible) (FR-013)
- [ ] T080 [P] [US4] GDPR erasure path `workloads/p4_knowledge_capture/gdpr_erasure.py`: erase raw interview audio/transcript on request within 1 month (extendable to 3) while preserving immutable audit (FR-024, NFR-008, Constitution II)
- [ ] T081 [US4] Run the Independent Test (T073) → make T071–T073 green (SC-007/008)

**Checkpoint**: All four pillars independently functional. P4 demoable — interview capture → cited, safety-filtered, human-reviewed answers; ungrounded questions declined.

---

## Phase 7: Polish & Cross-Cutting Governance / BI Hardening

**Purpose**: Production governance, observability, and executive BI that span all pillars (sequenced late per the plan).

- [ ] T082 Purview lineage completion `platform/governance/purview-lineage.md`: end-to-end sensor→feature→model→report lineage across all four workloads + KPI marts (Constitution II, NFR-003)
- [ ] T083 [P] Entra RBAC hardening per persona + per-site isolation review `platform/governance/rbac-hardening.md`: least-privilege validation across operator/maintenance/energy/quality/exec-ESG/compliance-DPO; assert onboarded↔not-onboarded site isolation (NFR-005/007, FR-023, Constitution VII)
- [ ] T084 [P] Key Vault BYOK/CMK hardening + secret-rotation review across all workloads `platform/governance/keyvault-cmk.md` (Additional Constraints)
- [ ] T085 [P] Enable Microsoft Defender for Cloud across the resource group `infrastructure/modules/defender.bicep` validation `platform/governance/defender.md`
- [ ] T086 [P] Azure Monitor / App Insights drift + SLO alerting `platform/observability/alerts.bicep` for every agent + MLflow drift (P1/P3 models, P2 solver) (Additional Constraints, Constitution VI)
- [ ] T087 Power BI Direct Lake dashboards `platform/bi/`: executive (ESG/KPI), engineering, and operations dashboards over Gold marts, synthetic excluded/labeled (R5/R8, SC-001/002/004, Constitution IX)
- [ ] T088 [P] KPI baseline verification `platform/kpi/verify_baseline.md`: confirm frozen trailing-12-month per-site baselines normalized per product mix/volume drive all SC-001/002/004 reporting (R8)
- [ ] T088a [P] EU-ETS emissions reporting output `platform/kpi/ets_report.py`: generate an EU-ETS-format emissions report from the auditable Gold emissions/energy marts (per-site, per-period), assigned the `EnergyEts` 5-year retention class; this is the FR-020 *reporting output* (distinct from the T054 market-feed ingestion and T090 retention) (FR-020, NFR-008)
- [ ] T089 Cross-pillar conflict-arbitration UX `platform/governance/conflict-arbitration.md`: unified human-arbitration surface for `conflictsWith` across P1/P2/P3 (FR-021, Constitution I)
- [ ] T090 [P] Immutable-audit tamper-evidence validation `platform/audit/tests/test_audit_immutable.py`: assert no UPDATE/DELETE on audit tables; 10y/5y retention classes + per-site config (FR-017, NFR-008, Constitution II)
- [ ] T091 [P] GDPR data-subject-rights runbook `platform/governance/gdpr-dsr.md`: access/correction/erasure within 1 month (extendable to 3); audit-exemption (Art. 17(3)(b)) documented (FR-024)
- [ ] T092 [P] Synthetic-integrity end-to-end audit `platform/compliance/synthetic-integrity.md`: prove `origin=Synthetic` is preserved and never presented as real in storage/models/dashboards/KPIs/audit (Constitution IX, SC checks)
- [ ] T093 Run full `quickstart.md` validation (build → run → deploy → P1 Independent Test) and record the "What done looks like" evidence table (Constitution I–IX, SC-003/005/006)
- [ ] T094 [P] Documentation pass `workloads/*/README.md` + `platform/README.md`: per-pillar run/deploy/test instructions and FR/NFR/SC traceability

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — T006–T008 are the only remaining items.
- **Foundational (Phase 2)**: 2a (T009–T019) DONE. 2b live provisioning (T020–T023) depends on the completed Bicep. 2c gates (T024–T025) depend on T020. 2d ingestion/medallion (T026–T033) depends on T020–T021. 2e governance/KPI (T034–T037) depends on T020–T022. **Foundational BLOCKS all user stories.**
- **User Stories (Phase 3–6)**: All depend on Foundational completion. Once done, P1→P2→P3→P4 may proceed in priority order, or in parallel if staffed.
- **Polish (Phase 7)**: Depends on the user stories whose data it governs/reports (T082, T087–T089 need pillars complete).

### User Story Dependencies

- **US1 (P1)**: After Foundational. No dependency on other stories. MVP.
- **US2 (P2)**: After Foundational. Consumes shared market/forecast inputs (T031); `conflictsWith` (T059) references P1/P3 but degrades gracefully if they are absent — independently testable.
- **US3 (P3)**: After Foundational. Independent; predicted-vs-actual is self-contained.
- **US4 (P4)**: After Foundational. Fully independent (Foundry plane).

### Within Each User Story

- Tests / data-quality / eval-drift gates (Constitution VIII) are authored and run **red FIRST**, before implementation.
- Features (training) before scoring; scoring before human-decision/audit wiring; audit wiring before the Independent Test closes the story.

### Parallel Opportunities

- Setup: T006–T008 in parallel.
- Foundational: T021/T022/T023 in parallel after T020; T031/T032/T033 in parallel; T034–T037 in parallel.
- Once Foundational completes, US1–US4 can run in parallel across teams.
- Within a story, all `[P]` test tasks run in parallel; `[P]` feature builds (e.g. T041, T052/T053, T064/T066, T074) run in parallel.

---

## Parallel Example: User Story 1

```bash
# Author all P1 gates first (must run red before implementation):
Task: "Contract test in workloads/p1_predictive_maintenance/tests/test_prediction_contract.py"   # T038
Task: "Eval/drift gate in workloads/p1_predictive_maintenance/tests/test_rul_eval_drift.py"       # T039

# Then parallel feature work:
Task: "Physics-informed features in workloads/p1_predictive_maintenance/physics_features.py"      # T041
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Finish Setup (T006–T008) + Foundational (T020–T037).
2. Complete Phase 3 (US1, T038–T048).
3. **STOP and VALIDATE**: run the degrading-furnace replay Independent Test → ≥21-day warning + recorded decision + immutable audit (SC-003/005).
4. Demo the MVP at the pilot furnace (Constitution X / SC-009).

### Incremental Delivery

Foundation → US1 (MVP) → US2 → US3 → US4, each independently tested and demoable, then Phase 7 governance/BI hardening. Each story adds value without breaking the previous ones.

### Constitution Gates Baked Into Acceptance

Human-in-the-loop decision recorded (I), immutable AuditRecord + Purview lineage (II), EU-residency policy enforced/denied non-EU (III), one-way OT→IT verified (IV), scoped stack / no excluded services (V), explainable evidence + grounded/cited + Content-Safety GenAI + freshness flags (VI), RBAC + per-site isolation (VII), test-first contracts/eval-drift gates (VIII), synthetic-origin preserved end-to-end (IX).

---

## Notes

- `[X]` = already implemented and verified (22 xUnit + 14 pytest passing; `az bicep build` clean).
- `[P]` = different files / no incomplete-task dependency.
- `platform/` is the shared data-and-governance plane (new); `workloads/p1..p4` are the pillar workloads (new); both extend the existing monorepo per plan.md.
- Verify each story's gate tests fail before implementing; commit after each task or logical group; stop at any checkpoint to validate a story independently.
