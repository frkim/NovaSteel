# Feature Specification: AI-Powered Steel Production Optimization Platform

**Feature Branch**: `001-steel-optimization-platform`

**Created**: 2026-06-22

**Status**: Draft

**Input**: User description: "Build an AI-driven production optimization platform for NovaSteel, a Luxembourg-based integrated steel producer operating blast furnaces and rolling mills across Luxembourg, Germany, Belgium and Spain. The platform must deliver predictive maintenance intelligence, an energy optimization engine, a quality control AI system, and a GenAI knowledge-capture system — with humans in the loop, full traceability for GDPR and the EU AI Act, EU data residency, a one-way OT/IT safety boundary, and a phased rollout."

## Overview

NovaSteel is an integrated steel producer running blast furnaces and rolling mills across four EU countries (Luxembourg, Germany, Belgium, Spain). The business faces five connected pressures: energy is ~35% of production cost with no real-time optimization; CO₂ emissions carry rising EU ETS penalty exposure; furnace-lining wear is unpredictable and each catastrophic failure costs ~€8M; high-grade steel for automotive customers suffers quality inconsistency; and retiring senior operators are taking irreplaceable know-how with them.

This feature defines an AI-driven production optimization platform that turns plant telemetry, production/maintenance records, and energy-market signals into **recommendations** that human teams review and approve before any action is taken. The platform never directly actuates plant equipment. It delivers four capability pillars — predictive maintenance, energy optimization, quality control, and knowledge capture — under cross-cutting constraints of human-in-the-loop control, end-to-end traceability, EU data residency, and a one-way OT→IT telemetry boundary, rolled out in phases from a single furnace to four-country scale.

## Clarifications

### Session 2026-06-23

- Q: What audit & retention schedule should the platform adopt (NFR-008 / FR-024)? → A: Predictions/recommendations/human-decision audit trail = 10 years; energy/ETS records = 5 years; operator-interview personal (non-audit) data retained only for the knowledge-capture purpose and erasable on request; all periods configurable per record class and per site (LU/DE/BE/ES).
- Q: How is the pre-platform baseline for the −14% energy / −22% CO₂ / +8% yield targets defined (SC-001/002/004)? → A: Trailing 12 calendar months immediately preceding go-live at each site, frozen per site at onboarding, normalized for product mix and production volume.
- Q: What is the measurable knowledge-capture target for Pillar 4 (SC-007)? → A: At least 80% of operators identified as retiring within the next 24 months are interviewed and structured into the procedure library, AND at least 70% of operator questions are answerable with a grounded, source-cited answer.
- Q: Within what timeframe must GDPR data-subject requests (access/correction/erasure) for operator-interview personal data be actioned (FR-024)? → A: GDPR statutory default — within 1 month of receipt, extendable to 3 months for complex/numerous requests, with the data subject informed of any extension and its reasons.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Predictive Furnace-Lining Maintenance (Priority: P1)

A Maintenance/Reliability Engineer needs advance warning of furnace-lining degradation so a controlled repair can be scheduled during planned downtime instead of suffering a catastrophic, unplanned ~€8M failure. The platform continuously analyzes furnace thermal signatures and related telemetry, predicts remaining useful life of the lining, and raises a prediction with at least 21 days of advance warning. The engineer reviews the prediction and its supporting evidence, confirms or rejects it, and — when confirmed — initiates a maintenance work order through existing systems.

**Why this priority**: This pillar protects against the single largest, most catastrophic financial loss event (€8M per furnace-lining failure) and directly delivers the headline "21-day advance warning" outcome. It can ship first because it is valuable on its own, even before energy, quality, or knowledge features exist.

**Independent Test**: Replay historical thermal/telemetry data from a furnace that experienced a past lining failure and confirm the platform raises a degradation prediction at least 21 days before the failure date, with supporting evidence presented for human review and a recorded confirm/reject decision.

**Acceptance Scenarios**:

1. **Given** a furnace whose lining is degrading, **When** the platform detects the degradation pattern in thermal signatures, **Then** it raises a failure-risk prediction with an estimated time-to-failure of at least 21 days and presents the contributing signals to the maintenance engineer.
2. **Given** a furnace-lining prediction awaiting review, **When** the maintenance engineer confirms it, **Then** the platform records the approval (who, when, rationale) and supports creation of a maintenance work order in the existing maintenance system; no equipment action is taken automatically.
3. **Given** a furnace-lining prediction awaiting review, **When** the maintenance engineer rejects it as a false alarm, **Then** the platform records the rejection and rationale and retains the case for model-quality review.
4. **Given** a furnace operating within normal thermal bounds, **When** telemetry shows no degradation pattern, **Then** the platform does not raise a failure prediction (avoiding alarm fatigue).

---

### User Story 2 - Energy Dispatch Optimization (Priority: P2)

An Energy Manager needs to schedule energy-intensive processes (e.g., heats, reheating, rolling campaigns) around fluctuating day-ahead electricity spot prices and grid carbon intensity, without violating production commitments. The platform proposes an optimized schedule that lowers energy cost and CO₂ emissions per ton; the Energy Manager (in coordination with operations) reviews the proposal, sees the expected cost/emissions/production trade-offs, and approves, adjusts, or rejects it before it is handed to operations.

**Why this priority**: Energy is ~35% of production cost and the largest recurring savings lever (target −14% energy/ton, −22% CO₂). It is high value and ongoing, but depends on having trustworthy production-schedule context, so it follows the maintenance pillar.

**Independent Test**: Provide a day-ahead price curve, grid carbon-intensity forecast, and a set of pending energy-intensive jobs with constraints, and confirm the platform returns a schedule recommendation that reduces modeled energy cost and CO₂ versus an unoptimized baseline while respecting stated production deadlines, with a human approval step recorded.

**Acceptance Scenarios**:

1. **Given** day-ahead spot prices, grid carbon-intensity forecasts, and pending production jobs with deadlines, **When** the Energy Manager requests an optimized plan, **Then** the platform proposes a schedule and shows expected energy consumption per ton, CO₂ emissions, and cost versus the unoptimized baseline.
2. **Given** a proposed energy schedule, **When** it would cause a production order to miss a committed deadline, **Then** the platform flags the conflict and does not present the option as compliant with production constraints.
3. **Given** a proposed energy schedule, **When** the Energy Manager approves it, **Then** the platform records the approval and the assumptions used, and makes the approved plan available to operations; the platform does not directly control plant equipment.
4. **Given** updated market prices arrive intra-day, **When** the inputs change materially, **Then** the platform can produce a revised recommendation for human review.

---

### User Story 3 - Quality Prediction & Process Guidance (Priority: P3)

A Quality Engineer / Metallurgist needs to raise the yield of high-grade steel destined for automotive customers. The platform predicts quality outcomes for in-progress heats/coils, applies statistical process control (SPC) to flag drift, and recommends process adjustments. The engineer reviews each recommendation with its rationale and confirms whether to apply it, improving first-pass yield while preserving full traceability of why each adjustment was made.

**Why this priority**: Improving high-grade yield by +8% protects premium automotive revenue and reduces scrap/rework, but it builds on the same telemetry and human-in-the-loop foundations as the earlier pillars, so it is sequenced third.

**Independent Test**: Feed process data for heats with known quality outcomes and confirm the platform predicts out-of-spec risk, raises SPC alerts on drift, and surfaces a reviewable process recommendation with rationale, with the operator/engineer decision recorded.

**Acceptance Scenarios**:

1. **Given** an in-progress heat trending toward an out-of-spec quality result, **When** the platform detects the drift via SPC, **Then** it alerts the quality engineer and recommends a corrective process adjustment with its supporting rationale.
2. **Given** a quality recommendation awaiting review, **When** the quality engineer or operator confirms it, **Then** the platform records the decision and links it to the affected heat/coil for traceability.
3. **Given** a completed heat, **When** its actual quality result is recorded, **Then** the platform associates predicted versus actual outcomes to support yield tracking and model-quality review.

---

### User Story 4 - GenAI Operator Knowledge Capture & Retrieval (Priority: P4)

A retiring Senior Operator's expertise must be captured before it is lost, and Shift Operators need fast, trustworthy answers to operational questions. The platform interviews operators (capturing spoken responses via speech-to-text), structures the expertise into a searchable, citation-backed procedure library, and answers operator questions by retrieving from that library — always citing sources and routing answers through human review so that incorrect or unsafe guidance is caught before it reaches the shop floor.

**Why this priority**: Knowledge capture mitigates a long-term workforce-attrition risk rather than an immediate production loss, so it is valuable but sequenced last; it also benefits from the platform's established review/traceability patterns.

**Independent Test**: Record a sample operator interview, confirm it is transcribed and structured into the procedure library, then ask an operational question and confirm the platform returns an answer with citations to source material and a human-review step before the answer is treated as authoritative.

**Acceptance Scenarios**:

1. **Given** a recorded interview with a retiring operator, **When** it is ingested, **Then** the platform transcribes the speech and structures the content into the searchable procedure library with attributable sources.
2. **Given** an operator question, **When** the platform answers from the procedure library, **Then** the answer includes citations to the underlying source material.
3. **Given** a generated answer or newly structured procedure, **When** it is presented, **Then** a qualified reviewer can approve, edit, or reject it before it becomes part of the authoritative library (human-in-the-loop review).
4. **Given** a question with no supporting source in the library, **When** the platform cannot ground an answer, **Then** it declines to answer rather than fabricating guidance.

---

### Edge Cases

- **Missing, delayed, or out-of-order telemetry**: How does the platform behave when a sensor drops out, a site link is interrupted, or telemetry arrives late/out of sequence? Predictions must clearly indicate degraded confidence or unavailability rather than silently using stale data.
- **Conflicting recommendations across pillars**: What happens when an energy-optimal schedule conflicts with a maintenance window or with a quality-driven process constraint? The platform must surface the conflict for human arbitration rather than auto-resolving.
- **No human approval received**: What happens to a time-sensitive recommendation (e.g., an intra-day energy plan) if no operator acts before it expires? It must lapse safely with no action taken and be recorded as unactioned.
- **False positives / alarm fatigue**: How are repeated low-value alerts suppressed without hiding genuine high-risk predictions?
- **Prediction earlier or later than the 21-day target**: How is a degradation signal that appears with less than 21 days of lead time handled and escalated?
- **GenAI hallucination / unsupported answer**: The knowledge assistant must refuse to answer when retrieval has no grounding, and must never present uncited guidance as authoritative.
- **Data subject rights & personal data in interviews**: Operator interview recordings contain personal data; how are access, correction, and erasure requests handled while preserving required audit records?
- **Site/country onboarding mid-rollout**: How does the platform behave when one site is live and others are not yet onboarded (phased rollout) without cross-contaminating data or recommendations?
- **OT boundary integrity**: What happens if a component attempts to send a command back toward plant OT systems? Such a path must not exist; only one-way telemetry egress from OT is permitted.

## Requirements *(mandatory)*

### Functional Requirements

**Predictive maintenance (Pillar 1)**

- **FR-001**: The platform MUST continuously analyze furnace thermal signatures and associated telemetry to detect furnace-lining degradation patterns.
- **FR-002**: The platform MUST predict furnace-lining failure risk with at least **21 days** of advance warning and present an estimated time-to-failure.
- **FR-003**: The platform MUST present the evidence/contributing signals behind each maintenance prediction so a human can understand why it was raised (explainability).
- **FR-004**: The platform MUST allow a maintenance/reliability engineer to confirm or reject each prediction, and MUST support creation of a maintenance work order in the existing maintenance system upon confirmation — without taking any automatic equipment action.

**Energy optimization (Pillar 2)**

- **FR-005**: The platform MUST ingest day-ahead electricity spot prices and grid carbon-intensity signals and use them to propose schedules for energy-intensive processes.
- **FR-006**: The platform MUST produce energy-dispatch recommendations that reduce energy consumption per ton and CO₂ emissions while respecting production commitments and operational constraints.
- **FR-007**: The platform MUST show, for each energy recommendation, the expected energy consumption per ton, CO₂ emissions, and cost compared with an unoptimized baseline.
- **FR-008**: The platform MUST require human (Energy Manager / operations) approval before an energy plan is handed to operations, and MUST flag any plan that would breach a committed production deadline.

**Quality control (Pillar 3)**

- **FR-009**: The platform MUST predict quality outcomes for in-progress production (heats/coils) and apply statistical process control (SPC) to detect process drift.
- **FR-010**: The platform MUST recommend process adjustments with supporting rationale and allow a quality engineer/operator to confirm or reject each recommendation.
- **FR-011**: The platform MUST associate predicted quality outcomes with actual recorded outcomes to support yield tracking and model-quality review.

**Knowledge capture (Pillar 4)**

- **FR-012**: The platform MUST capture operator interviews via speech-to-text and structure the resulting expertise into a searchable procedure library.
- **FR-013**: The platform MUST answer operator questions from the procedure library and MUST cite the source material supporting each answer.
- **FR-014**: The platform MUST route generated answers and newly structured procedures through human review before they become authoritative, and MUST decline to answer when no grounded source exists (no fabrication).

**Cross-cutting platform behavior**

- **FR-015**: The platform MUST operate as a recommendation/decision-support system only; it MUST NOT directly actuate or control plant equipment under any pillar.
- **FR-016**: The platform MUST present every prediction and recommendation to the appropriate human role for confirmation before any downstream action (human-in-the-loop).
- **FR-017**: The platform MUST record an immutable, queryable audit trail for every prediction, recommendation, and human approval/rejection decision, including who, what, when, the inputs/evidence used, and the rationale.
- **FR-018**: The platform MUST integrate with plant OT/IoT telemetry (furnace, mill, and utility sensors; SCADA; historian) across all four sites, with telemetry flowing one-way out of the plant only.
- **FR-019**: The platform MUST integrate with MES/ERP/EAM-CMMS systems to obtain production orders, heat schedules, and maintenance work orders, and to support work-order creation.
- **FR-020**: The platform MUST integrate with energy-market feeds (day-ahead spot prices and grid carbon intensity) and support EU ETS emissions reporting needs.
- **FR-021**: The platform MUST surface conflicts between recommendations from different pillars (e.g., energy schedule vs. maintenance window vs. quality constraint) for human resolution rather than auto-resolving them.
- **FR-022**: The platform MUST indicate degraded confidence or unavailability when input telemetry is missing, delayed, or out of order, rather than presenting predictions based on stale data as if current.
- **FR-023**: The platform MUST scope data and recommendations per site so that a phased rollout (one furnace/site → multi-line → four-country) does not cross-contaminate data between onboarded and not-yet-onboarded sites.
- **FR-024**: The platform MUST support data-subject rights (access, correction, erasure) for personal data contained in operator interviews and other records, while preserving the audit records required for regulatory compliance. Data-subject requests MUST be actioned within **1 month** of receipt, extendable to a maximum of **3 months** for complex or numerous requests, with the data subject informed of any extension and its reasons (GDPR Art. 12(3)). Where rights conflict with audit obligations, the immutable audit trail (FR-017) and end-to-end traceability (NFR-003) take precedence: audit records are exempt from erasure under the legal-obligation exception (GDPR Art. 17(3)(b)), while non-audit personal content (e.g., raw interview recordings and transcripts) MUST be erasable on request. The platform MUST minimize personal data held in audit records (e.g., pseudonymizing reviewer identity where feasible) and MUST inform the data subject when data is retained under this exception. The exact retention period for exempted audit records is governed by NFR-008.

### Non-Functional / Constraint Requirements

- **NFR-001 (Human-in-the-loop)**: No recommendation may result in a physical or operational action without explicit confirmation by an authorized human in the relevant role.
- **NFR-002 (EU data residency)**: All platform data — telemetry, models, interviews, and audit logs — MUST be stored and processed within the EU.
- **NFR-003 (Traceability / EU AI Act & GDPR)**: Every prediction, recommendation, and decision MUST be traceable end-to-end (inputs, model/logic version, output, reviewer, decision) to satisfy GDPR accountability and EU AI Act record-keeping obligations.
- **NFR-004 (OT/IT one-way boundary)**: The connection between plant OT and the platform MUST be one-way (telemetry egress from OT only); no control or command path back into OT systems may exist. The initial scope assumes cloud-direct ingestion with no plant-side edge runtime.
- **NFR-005 (Role-based access)**: Access to data, predictions, recommendations, and approval actions MUST be restricted by user role (operator, maintenance, energy, quality, executive/ESG, compliance/DPO).
- **NFR-006 (Explainability)**: Predictions and recommendations MUST be accompanied by human-understandable supporting evidence/rationale sufficient for the reviewing role to make an informed decision.
- **NFR-007 (Phased rollout)**: The platform MUST support incremental onboarding of furnaces, lines, sites, and countries without requiring a full four-country deployment to deliver value at a single pilot site.
- **NFR-008 (Audit retention)**: Audit and traceability records MUST be retained for the period required by applicable EU regulation, with the following confirmed baseline retention periods (clarified 2026-06-23; configurable per site to meet national requirements):
  - **Predictions, recommendations, and human decisions** (audit trail per FR-017): retained for **10 years** from creation, aligning with EU AI Act record-keeping for high-risk AI systems (minimum 6 months) extended to the longer retention typical of industrial safety/quality compliance.
  - **Energy/ETS-related records** (per FR-020): retained for a minimum of **5 years** to support EU ETS reporting and verification.
  - **Operator-interview personal data** (non-audit content): retained only for as long as needed for the knowledge-capture purpose, then erased on request per FR-024; any associated audit-trail entries are pseudonymized and retained under the 10-year audit period above.
  Retention periods MUST be configurable per record class and per site so they can be adjusted to national regulatory requirements (LU/DE/BE/ES).

### Key Entities *(include if feature involves data)*

- **Site / Plant**: A production location (Luxembourg, Germany, Belgium, Spain) containing furnaces, mills, and utilities; the unit of phased onboarding and data scoping.
- **Furnace / Asset**: A monitored piece of equipment (e.g., blast furnace, rolling mill) with telemetry streams and a lifecycle/condition state (e.g., lining wear).
- **Telemetry Reading**: A timestamped sensor measurement (temperature/thermal signature, pressure, vibration, throughput, energy use) sourced one-way from OT/IoT.
- **Prediction**: A model output (e.g., furnace-lining failure risk with time-to-failure, quality outcome) with confidence, contributing evidence, and the model/logic version that produced it.
- **Recommendation**: A proposed action (maintenance, energy schedule, process adjustment, knowledge answer) with rationale, expected impact, and constraints.
- **Human Decision / Approval**: A record of a reviewer confirming, editing, or rejecting a prediction/recommendation, including identity, timestamp, and rationale.
- **Work Order**: A maintenance or production task created in/synchronized with MES/ERP/EAM-CMMS following an approved recommendation.
- **Energy Plan**: A proposed schedule of energy-intensive jobs aligned to spot prices and grid carbon intensity, with expected energy/CO₂/cost outcomes.
- **Heat / Coil (Production Lot)**: A traceable unit of steel production with process parameters and predicted/actual quality outcomes.
- **Procedure / Knowledge Item**: A structured, source-cited piece of captured operator expertise in the searchable library.
- **Operator Interview**: A recorded/transcribed knowledge-capture session containing operator personal data subject to GDPR.
- **Audit Record**: An immutable traceability entry linking inputs, outputs, model/logic versions, and human decisions for compliance.
- **User / Role**: A platform user mapped to a persona (operator, maintenance, energy, quality, executive/ESG, compliance/DPO) governing access and approval authority.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Energy consumption per ton of steel is reduced by **14%** versus the pre-platform baseline at sites where the energy pillar is live.
- **SC-002**: CO₂ emissions are reduced by **22%** versus the pre-platform baseline at sites where the energy pillar is live, reducing EU ETS exposure.
- **SC-003**: Furnace-lining failures are predicted with at least **21 days** of advance warning, demonstrated on historical failure cases and in production for monitored furnaces.
- **SC-004**: High-grade (automotive) steel yield improves by **8%** versus the pre-platform baseline at sites where the quality pillar is live.
- **SC-005**: 100% of platform-driven actions are preceded by a recorded human approval, and 100% of predictions, recommendations, and decisions have a complete, queryable audit trail (human-in-the-loop and traceability fully enforced).
- **SC-006**: All platform data is stored and processed within the EU (zero instances of data residency outside the EU).
- **SC-007**: Operator expertise is captured and made retrievable before key operators retire, measured by two targets at each live site: at least **80%** of operators identified as retiring within the next 24 months are interviewed and their expertise structured into the procedure library, and at least **70%** of operator questions are answerable from the library with a grounded, source-cited answer (the remainder correctly declined per SC-008).
- **SC-008**: Knowledge-assistant answers presented to operators are source-cited 100% of the time, and the assistant declines (rather than fabricates) when no grounded source exists.
- **SC-009**: The platform delivers measurable value at a single pilot furnace/site before multi-line and four-country scale-out (phased rollout proven at each stage).

## Assumptions

- **Baseline definition**: The −14% energy, −22% CO₂, and +8% yield targets are measured against a documented pre-platform baseline defined as the **trailing 12 calendar months** of production immediately preceding go-live at each site (a full year to absorb seasonality). Comparisons are **normalized for product mix and production volume** (e.g., energy and CO₂ expressed per ton per product grade, yield expressed per high-grade product line) so improvements reflect platform impact rather than shifts in what was produced. The baseline reference period and normalization factors are frozen per site at onboarding and recorded in the audit trail for traceability.
- **Human-in-the-loop is mandatory in initial scope**: Even routine/low-risk recommendations require human confirmation; no autonomous-action mode is in scope for the initial rollout.
- **Cloud-direct ingestion, no edge runtime**: The initial scope assumes telemetry is sent directly to the cloud with no plant-side edge analytics/runtime; existing OT/SCADA/historian systems already collect the source sensor data.
- **Existing systems remain systems of record**: MES/ERP/EAM-CMMS remain authoritative for production orders, schedules, and work orders; the platform reads from and proposes to them rather than replacing them.
- **Energy-market and grid-carbon feeds are available** for the relevant national markets (LU/DE/BE/ES) with sufficient timeliness for day-ahead and intra-day decisions.
- **Operators consent to interview capture**, and personal data in interviews is processed under a lawful GDPR basis.
- **Connectivity is generally reliable but may be intermittent**; the platform must degrade gracefully rather than assume continuous telemetry.
- **"High-grade steel" refers to the automotive-grade product lines** whose quality consistency is the stated business concern; the specific grades/specifications that define the yield baseline are provided by NovaSteel quality engineering.
- **Phased rollout order** starts with one furnace/site (pilot), then expands to multiple lines, then to all four countries; the specific pilot site/furnace is selected by NovaSteel.

## Out of Scope (initial release)

- Direct/automated control or actuation of plant equipment (the platform recommends only).
- Plant-side edge analytics or edge runtime (cloud-direct ingestion only in initial scope).
- Any data flow or command path from the platform back into OT/SCADA systems (one-way telemetry egress only).
- Replacement of existing MES/ERP/EAM-CMMS or SCADA/historian systems.
- Non-EU data storage or processing.
