# Phase 1 Data Model: AI-Powered Steel Production Optimization Platform

**Feature**: `001-steel-optimization-platform` | **Date**: 2026-06-23 | **Plan**: [plan.md](./plan.md)

Defines every spec **Key Entity** (spec.md §Key Entities) with fields, relationships,
state transitions, and the OneLake **medallion (Bronze/Silver/Gold)** mapping. Aligns with
the shared contracts in `libs/NovaSteel.Contracts` + `libs/novasteel_core`, the golden
fixtures in `libs/fixtures`, and the JSON Schemas in [`contracts/`](./contracts).

**Conventions**
- JSON is **camelCase** (matches `NovaSteelJson` + `novasteel_core` `to_camel`).
- `site ∈ {LU, DE, BE, ES}` is a **first-class scoping dimension on every entity**
  (Constitution VII per-site isolation, FR-023).
- **Provenance** (`origin ∈ {Real, Synthetic}` + `sourceId`) is carried on telemetry and
  **propagated into every derived entity** (Prediction, AuditRecord, Gold KPI) so synthetic
  data is queryable and never presentable as real (Constitution IX, CT-2).
- **Audit immutability**: `AuditRecord` is **append-only** (INSERT-only; no UPDATE/DELETE);
  retention 10 years (NFR-008). It is exempt from GDPR erasure (Art. 17(3)(b)); non-audit
  personal content (interview audio/transcripts) stays erasable (FR-024).

---

## Additive contract change (CT-2)

`TelemetryReading` gains two **additive, non-breaking** fields, mirrored everywhere:

| New field | Type | Default | Purpose |
|-----------|------|---------|---------|
| `origin` | enum `Origin{Real, Synthetic}` | `Real` | Synthetic-origin marker (Constitution IX) |
| `sourceId` | string | `""` (empty = unspecified real OT) | Specific producing source, e.g. `sim:steel_factory_simulator@v1`, `ot:LU-historian` |

Touch points: `libs/NovaSteel.Contracts/{TelemetryReading.cs, Enums.cs}`,
`libs/novasteel_core/novasteel_core/models.py`, `libs/fixtures/telemetry_reading.json`,
the Bronze/Silver/Gold schemas, and `Prediction`/`AuditRecord` provenance fields.

---

## Entities

### 1. Site / Plant
Production location; unit of phased onboarding and data scoping (FR-023, Constitution VII).

| Field | Type | Notes |
|-------|------|-------|
| `site` | enum `Site{LU,DE,BE,ES}` | Primary key (country code) |
| `displayName` | string | e.g. "Differdange, LU" |
| `onboardedAt` | dateTimeOffset? | Null until pillar go-live; gates per-site data visibility |
| `baselineFrozenAt` | dateTimeOffset? | When the trailing-12-month KPI baseline was frozen (R8) |
| `timezone` | string | IANA tz for scheduling/SPC windows |

**Relationships**: 1 Site → many Assets, Heats, Predictions, EnergyPlans, AuditRecords.

---

### 2. Furnace / Asset
A monitored equipment unit (blast furnace, rolling mill, utility) with telemetry + condition.

| Field | Type | Notes |
|-------|------|-------|
| `assetId` | string | e.g. `LU-BF1` (matches fixture) |
| `assetType` | enum `AssetType{Unknown,BlastFurnace,RollingMill,Utility}` | |
| `site` | enum `Site` | Scoping |
| `conditionState` | enum `{Normal,Watch,Degrading,AtRisk,OutOfService}` | Driven by P1 predictions |
| `liningInstalledAt` | dateTimeOffset? | Furnace-lining lifecycle anchor (RUL) |

**Relationships**: Asset 1→many TelemetryReading, 1→many Prediction.

---

### 3. TelemetryReading  *(contract: `telemetry-reading.schema.json`)*
Timestamped one-way OT/IoT sensor measurement (FR-018, Constitution IV).

| Field | Type | Notes |
|-------|------|-------|
| `assetId` | string | FK → Asset |
| `assetType` | enum `AssetType` | |
| `site` | enum `Site` | Scoping |
| `metric` | enum `Metric{Unknown,ThermocoupleTemp,HeatFlux,Vibration,Throughput,PowerDrawKw}` | |
| `value` | double | |
| `unit` | string | e.g. `C`, `kW` |
| `timestamp` | dateTimeOffset | Reading time (UTC) |
| `quality` | enum `Quality{Good,Suspect,Bad}` | Data-quality tag for auditability/FR-022 |
| `origin` | enum `Origin{Real,Synthetic}` | **CT-2** provenance (default `Real`) |
| `sourceId` | string | **CT-2** producing source id |

**Validation**: `value` finite; `timestamp` not in the future beyond clock skew; `quality`
≠ `Good` and freshness lag drive **reduced-confidence/unavailable** presentation (FR-022).

---

### 4. MarketSignal  *(contract: `market-signal.schema.json`)*
Day-ahead energy-market signal driving P2 (FR-005, FR-020).

| Field | Type | Notes |
|-------|------|-------|
| `market` | enum `Site` | National market (LU/DE/BE/ES) |
| `timestamp` | dateTimeOffset | Delivery hour |
| `spotPriceEurMwh` | double | Day-ahead spot price |
| `gridCarbonGramsPerKwh` | double | Grid carbon intensity |

---

### 5. Prediction  *(contract: `prediction.schema.json`)*
Model output (RUL failure-risk, quality outcome) with confidence + evidence + version
(FR-002/003, FR-009, Constitution VI).

| Field | Type | Notes |
|-------|------|-------|
| `predictionId` | string (uuid) | PK |
| `pillar` | enum `{Maintenance,Quality}` | Source pillar |
| `site` | enum `Site` | Scoping |
| `assetId` | string? | For maintenance |
| `heatId` | string? | For quality |
| `kind` | enum `{LiningFailureRisk,QualityOutcome,SpcDrift}` | |
| `timeToFailureDays` | double? | ≥21 expected for valid lining warning (SC-003) |
| `predictedAt` | dateTimeOffset | |
| `confidence` | double `[0,1]` | Uncertainty surfaced (Constitution VI) |
| `evidence` | array<EvidenceItem> | Contributing signals `{metric, value, weight, note}` |
| `modelVersion` | string | MLflow model/version (traceability, Constitution II) |
| `inputWindowRef` | string | Pointer to Silver/Gold feature snapshot used |
| `origin` | enum `Origin` | Propagated from inputs (synthetic if any synthetic input) |
| `status` | enum `{Raised,UnderReview,Confirmed,Rejected,Lapsed}` | State machine ↓ |

**State machine**: `Raised → UnderReview → (Confirmed | Rejected)`; time-sensitive
predictions with no decision → `Lapsed` (recorded as unactioned — Constitution I, edge case
"No human approval received"). Every transition writes an `AuditRecord`.

---

### 6. Recommendation  *(contract: `recommendation.schema.json`)*
Proposed action (maintenance, process adjustment, knowledge answer) with rationale +
expected impact (FR-004, FR-010, FR-013/014, Constitution I/VI).

| Field | Type | Notes |
|-------|------|-------|
| `recommendationId` | string (uuid) | PK |
| `pillar` | enum `{Maintenance,Quality,Knowledge}` | (Energy uses EnergyPlan) |
| `site` | enum `Site` | Scoping |
| `relatedPredictionId` | string? | FK → Prediction |
| `relatedHeatId` | string? | Quality |
| `summary` | string | Human-readable proposed action |
| `rationale` | string | Evidence/why (explainability) |
| `expectedImpact` | object | Pillar-specific (e.g. yield delta) |
| `citations` | array<Citation>? | **Required for Knowledge** (`{sourceId,title,locator}`); decline-on-empty (FR-014, SC-008) |
| `confidence` | double `[0,1]`? | |
| `contentSafetyPassed` | bool | GenAI outputs must pass Content Safety (Constitution VI) |
| `conflictsWith` | array<string>? | Cross-pillar conflict refs (FR-021) — surfaced, never auto-resolved |
| `status` | enum `{Proposed,UnderReview,Approved,Edited,Rejected,Lapsed}` | |

**Rule**: Knowledge recommendations with **no `citations`** MUST be `status=Rejected`/
declined, never presented as authoritative (FR-014, SC-008).

---

### 7. EnergyPlan  *(contract: `energy-plan.schema.json`)*
Proposed schedule of energy-intensive jobs vs spot price + grid carbon (FR-006/007/008, P2).

| Field | Type | Notes |
|-------|------|-------|
| `energyPlanId` | string (uuid) | PK |
| `site` | enum `Site` | Scoping |
| `planningHorizon` | object | `{from,to}` (day-ahead/intra-day) |
| `scheduledJobs` | array<ScheduledJob> | `{jobId, slotStart, slotEnd, deadline, energyMwh}` |
| `expectedEnergyPerTon` | double | vs baseline (FR-007) |
| `expectedCo2PerTon` | double | vs baseline (FR-007) |
| `expectedCostEur` | double | vs baseline (FR-007) |
| `baselineComparison` | object | `{baselineEnergyPerTon, baselineCo2PerTon, baselineCostEur}` (R8) |
| `deadlineBreaches` | array<string> | Jobs that would miss a committed deadline → flagged, not presented as compliant (FR-008) |
| `solver` | enum `{Milp,Heuristic}` | Which engine produced it (R2) |
| `origin` | enum `Origin` | Propagated |
| `status` | enum `{Proposed,UnderReview,Approved,Adjusted,Rejected,Lapsed}` | |

**State machine**: intra-day plans with no decision before horizon → `Lapsed`
(no action — Constitution I).

---

### 8. HumanDecision / Approval  *(contract: `human-decision.schema.json`)*
A reviewer confirming/editing/rejecting a Prediction/Recommendation/EnergyPlan
(FR-016, NFR-001, Constitution I).

| Field | Type | Notes |
|-------|------|-------|
| `decisionId` | string (uuid) | PK |
| `subjectType` | enum `{Prediction,Recommendation,EnergyPlan}` | |
| `subjectId` | string | FK → subject |
| `site` | enum `Site` | Scoping |
| `decision` | enum `{Confirm,Edit,Reject}` | |
| `reviewerId` | string | Entra identity (pseudonymized in audit where feasible — FR-024) |
| `reviewerRole` | enum `Role` | Persona authority (Constitution VII) |
| `rationale` | string | Why |
| `decidedAt` | dateTimeOffset | |
| `resultingWorkOrderId` | string? | If a work order was proposed (FR-004/019) |

**Rule**: No downstream action without a `HumanDecision` (SC-005 = 100%). Every decision
emits an `AuditRecord`.

---

### 9. WorkOrder
Maintenance/production task created in/synchronized with MES/ERP/EAM-CMMS after approval
(FR-004, FR-019). The platform **proposes**; existing systems remain systems of record.

| Field | Type | Notes |
|-------|------|-------|
| `workOrderId` | string | External system id |
| `site` | enum `Site` | |
| `sourceDecisionId` | string | FK → HumanDecision |
| `system` | enum `{MES,ERP,EAM_CMMS}` | Target system of record |
| `status` | enum `{Proposed,CreatedInSystem,Rejected}` | Platform never auto-executes |

---

### 10. Heat / Coil (Production Lot)
Traceable steel-production unit with process params + predicted/actual quality (FR-009/011).

| Field | Type | Notes |
|-------|------|-------|
| `heatId` | string | PK (heat or coil id) |
| `site` | enum `Site` | |
| `grade` | string | Automotive/high-grade product grade |
| `processParameters` | object | Heat/roll parameters |
| `predictedQuality` | object? | Link to Prediction (FR-009) |
| `actualQuality` | object? | Recorded outcome (FR-011) |
| `spcState` | enum `{InControl,Drifting,OutOfSpec}` | SPC (FR-009) |

---

### 11. Procedure / Knowledge Item  *(grounding source for P4)*
Structured, source-cited captured operator expertise in the searchable library (FR-012/013).

| Field | Type | Notes |
|-------|------|-------|
| `knowledgeItemId` | string | PK |
| `title` | string | |
| `body` | string | Structured procedure text |
| `sourceInterviewId` | string? | FK → OperatorInterview (provenance for citations) |
| `tags` | array<string> | Retrieval facets |
| `reviewStatus` | enum `{Draft,UnderReview,Authoritative,Rejected}` | Human-in-the-loop (FR-014) |
| `site` | enum `Site`? | Site-specific vs global |

---

### 12. OperatorInterview  *(personal data — GDPR)*
Recorded/transcribed knowledge-capture session (FR-012, FR-024).

| Field | Type | Notes |
|-------|------|-------|
| `interviewId` | string | PK |
| `operatorRef` | string | Pseudonymized subject ref |
| `site` | enum `Site` | |
| `audioUri` | string? | Blob URI — **erasable** non-audit personal content (FR-024) |
| `transcript` | string? | **Erasable** personal content |
| `capturedAt` | dateTimeOffset | |
| `retentionClass` | enum `{KnowledgeCapturePersonal}` | Erasable on request; audit refs stay (NFR-008) |
| `consentBasis` | string | Lawful GDPR basis (Assumptions) |

**GDPR**: access/correction/erasure actioned within 1 month (extendable to 3) (FR-024);
erasing audio/transcript does **not** erase the immutable `AuditRecord` (Art. 17(3)(b)).

---

### 13. AuditRecord  *(contract: `audit-record.schema.json`)*  — IMMUTABLE
Append-only traceability entry for every prediction, recommendation, and human decision
(FR-017, NFR-003, Constitution II).

| Field | Type | Notes |
|-------|------|-------|
| `auditId` | string (uuid) | PK |
| `subjectType` | enum `{Prediction,Recommendation,EnergyPlan,HumanDecision,WorkOrder,KnowledgeItem}` | |
| `subjectId` | string | FK |
| `site` | enum `Site` | Scoping |
| `action` | string | e.g. `PredictionRaised`, `DecisionConfirmed` |
| `inputsRef` | array<string> | Pointers to inputs/evidence used |
| `modelOrLogicVersion` | string | Model/solver/agent version |
| `output` | object | Snapshot of the produced output |
| `reviewerId` | string? | Pseudonymized where feasible (FR-024) |
| `rationale` | string? | |
| `timestamp` | dateTimeOffset | |
| `origin` | enum `Origin` | Provenance of underlying data (Constitution IX) |
| `retentionClass` | enum `{PredictionDecisionAudit,EnergyEts}` | 10y / 5y (NFR-008) |

**Constraints**: **INSERT-only** (no UPDATE/DELETE); tamper-evidence via ledger/temporal
tables (R7); retention configurable per record class **and per site** (NFR-008).

---

### 14. User / Role
Platform user mapped to a persona governing access + approval authority
(NFR-005, Constitution VII).

| Field | Type | Notes |
|-------|------|-------|
| `userId` | string | Entra ID object id |
| `role` | enum `Role{Operator,Maintenance,Energy,Quality,ExecutiveEsg,ComplianceDpo}` | Least-privilege persona |
| `siteScope` | array<Site> | Sites the user may access (per-site isolation) |

---

## Relationship overview

```text
Site 1──* Asset 1──* TelemetryReading
Site 1──* Heat/Coil
Asset/Heat ──* Prediction ──1 (Recommendation | WorkOrder via decision)
Prediction/Recommendation/EnergyPlan ──1 HumanDecision ──? WorkOrder
OperatorInterview 1──* KnowledgeItem ──* (cited by) Recommendation(Knowledge)
ALL of {Prediction, Recommendation, EnergyPlan, HumanDecision, WorkOrder, KnowledgeItem}
   ──* AuditRecord   (append-only, immutable)
MarketSignal ──* EnergyPlan
Provenance (origin, sourceId) flows: TelemetryReading → Silver → Gold/feature → Prediction → AuditRecord
```

---

## Medallion (Bronze / Silver / Gold) mapping

| Entity | Bronze (raw, append-only) | Silver (cleaned, conformed, per-`site`) | Gold (features / KPI marts) |
|--------|---------------------------|------------------------------------------|------------------------------|
| TelemetryReading | Raw IoT/EH landing, **origin/sourceId preserved verbatim** | Deduped, quality/freshness-flagged, partitioned by `site`+time | RUL/quality feature tables; hot-path KQL in RTI Eventhouse |
| MarketSignal | Raw market feed landing | Conformed per `market`/hour | Energy-dispatch input curves |
| Heat/Coil | Raw MES/ERP extracts | Conformed lots w/ process params | SPC aggregates, yield KPI mart |
| Prediction | — (system-generated) | Stored w/ evidence + modelVersion | Predicted-vs-actual yield tracking (FR-011) |
| EnergyPlan / Recommendation / HumanDecision | — | Workflow state (relational store, R7) | KPI attribution (energy/CO₂/yield vs frozen baseline, R8) |
| OperatorInterview | Raw audio in Blob (erasable) | Transcript + structured KnowledgeItems | Foundry IQ grounding index |
| AuditRecord | — | **Immutable relational store** (R7) + OneLake analytical copy | Compliance/lineage reporting (Purview) |
| KPI baselines (R8) | — | Frozen per-site baseline record (immutable) | KPI marts **exclude `origin=Synthetic`** from real KPIs |

**Provenance, `site`, and `quality` columns propagate through every layer.** Purview
captures sensor→feature→model→report lineage across Bronze→Silver→Gold (Constitution II).
