<!--
SYNC IMPACT REPORT
==================
Version change: (none) → 1.0.0  (INITIAL RATIFICATION)
Bump rationale: First concrete constitution replacing the unfilled template; MAJOR
  baseline established at 1.0.0 per ratification request.

Modified principles: N/A (initial adoption)
Added principles:
  I.    Human-in-the-Loop (NON-NEGOTIABLE)
  II.   End-to-End Traceability (NON-NEGOTIABLE)
  III.  EU Data Residency (NON-NEGOTIABLE)
  IV.   One-Way OT→IT Boundary (NON-NEGOTIABLE)
  V.    Scoped, Unified Stack (NON-NEGOTIABLE)
  VI.   Explainability & Responsible AI (NON-NEGOTIABLE)
  VII.  Role-Based Access & Per-Site Isolation (NON-NEGOTIABLE)
  VIII. Contract-First, Test-First Engineering (NON-NEGOTIABLE)
  IX.   Synthetic-Data Integrity (NON-NEGOTIABLE)
  X.    Phased Delivery (guidance)
Added sections:
  - Additional Constraints
  - Governance (amendment policy, versioning policy, compliance review)

Removed sections: None (template placeholder sections replaced in place).

Templates requiring updates / alignment checks:
  ✅ .specify/templates/plan-template.md — "Constitution Check" gate present and
       generic ([Gates determined based on constitution file]); compatible. Plan
       authors MUST instantiate gates from Principles I–IX (X advisory).
  ✅ .specify/templates/spec-template.md — no constitution references; no change required.
  ✅ .specify/templates/tasks-template.md — no constitution references; no change required.
  ⚠ Agent context file — extensions.yml installs `agent-context`; refresh agent
       context (speckit.agent-context.update) so principle names propagate to the
       active agent guidance file after this amendment.

Authority / traceability sources:
  - specs/001-steel-optimization-platform/spec.md (FR-015..024, NFR-001..008)
  - docs/usecase/0_preliminary analysis/0_architecture.md
  - docs/usecase/0_preliminary analysis/1_azure_services.md (Final Decision — Scoped
      Service Set; Explicitly Excluded table → authority for Principle V)
  - docs/usecase/0_preliminary analysis/3_c4model.md

Deferred items / follow-up TODOs: None. No unresolved bracket tokens remain.
-->

# NovaSteel Platform Constitution

NovaSteel "Project Ignition" — an AI-powered steel-production optimization platform
delivering predictive maintenance, energy dispatch, quality optimization, and
knowledge capture across four EU sites. This constitution is the runtime governance
guide: every plan, pull request, and review is measured against it.

## Core Principles

### I. Human-in-the-Loop (NON-NEGOTIABLE)

The platform is decision-support only. It MUST NEVER directly actuate or control plant
equipment, under any pillar (maintenance, energy, quality, or knowledge). Every
prediction and recommendation MUST be presented to the authorized human role and
explicitly confirmed before any downstream action is taken. No autonomous-action mode
exists in scope. Time-sensitive recommendations that receive no approval MUST lapse
safely with no action and be recorded as unactioned. Cross-pillar conflicts MUST be
surfaced for human resolution, never auto-resolved.

**Rationale**: Steelmaking is a safety-critical industrial process; an erroneous
autonomous action can injure people or destroy a heat. Decision-support-only is the
foundational risk control and the basis for EU AI Act high-risk human-oversight
obligations. (Trace: NFR-001, FR-015, FR-016, FR-021; spec edge case "No human
approval received".)

### II. End-to-End Traceability (NON-NEGOTIABLE)

Every prediction, recommendation, and human decision MUST produce an immutable,
queryable audit record capturing: inputs/evidence used, model or logic version,
output, reviewer identity, timestamp, and rationale — sufficient for GDPR
accountability and EU AI Act record-keeping. Audit records are exempt from erasure
under the GDPR legal-obligation exception (Art. 17(3)(b)); non-audit personal content
(e.g., raw interview recordings and transcripts) MUST remain erasable. Personal data in
audit records MUST be minimized (e.g., pseudonymized reviewer identity where feasible).
Data lineage (sensor → feature → model → report) MUST be captured in Microsoft Purview.

**Rationale**: Regulatory defensibility and operational trust both require that any
output can be reconstructed and explained after the fact. Lineage and immutable audit
are the mechanism that makes accountability verifiable rather than asserted. (Trace:
NFR-003, FR-017, FR-024, NFR-008.)

### III. EU Data Residency (NON-NEGOTIABLE)

ALL data — telemetry, models, operator interviews, and audit logs — MUST be stored and
processed within EU regions (Sweden Central / West Europe / Germany West Central).
There MUST be zero data egress or processing outside the EU. Region pinning MUST be
enforced by Azure Policy, not by convention or developer discipline.

**Rationale**: NovaSteel operates under EU data-sovereignty expectations across four
member states; residency cannot depend on human vigilance and MUST be enforced as
policy-as-code so violations fail deployment rather than reaching production. (Trace:
NFR-002, SC-006.)

### IV. One-Way OT→IT Boundary (NON-NEGOTIABLE)

Plant telemetry flows one-way out of the operational-technology (OT) environment only.
NO control or command path back into OT/SCADA may exist in code, infrastructure, or
configuration. Ingestion is cloud-direct via Azure IoT Hub (no plant-side edge runtime
in scope). Any component that attempts, enables, or implies a reverse path into OT is a
constitution violation and MUST fail review.

**Rationale**: A unidirectional boundary keeps the corporate/cloud attack surface from
reaching equipment that controls molten metal. Enforcing it structurally — not just by
firewall rule — preserves plant safety and integrity. (Trace: NFR-004, FR-018; spec
edge case "OT boundary integrity".)

### V. Scoped, Unified Stack (NON-NEGOTIABLE)

The platform is concentrated in **Microsoft Fabric** (data + ML) and **Microsoft
Foundry** (AI), with a minimal **IoT + PaaS compute** footprint. ONLY the in-scope
services from `1_azure_services.md` "Final Decision — Scoped Service Set" may be
introduced: Microsoft Fabric (OneLake, Data Factory, Data Engineering, Data Science,
Real-Time Intelligence, Power BI); Microsoft Foundry (Agent Service, Foundry IQ, Azure
OpenAI / Foundry Models, AI Services incl. Content Safety); Azure IoT Hub + Event Hubs;
Azure Functions + Azure Container Apps; and the security/governance/ops set (Entra ID,
Key Vault, Azure Policy, Purview, Defender for Cloud, Azure Monitor / Application
Insights, VNet + Private Link, ADLS Gen2 / OneLake + Blob Storage). The following are
explicitly FORBIDDEN without a documented Complexity-Tracking justification: Azure
Machine Learning, Azure Databricks, Azure Data Factory (standalone), Azure IoT
Edge / IoT Operations, Azure IoT Central, standalone Azure Data Explorer, Azure Stream
Analytics, Azure Arc, AKS, Azure Virtual Machines, Azure DevOps / Azure Pipelines,
Azure Stack, and Azure Sphere.

**Rationale**: The goal is to solve NovaSteel's four challenges, not to showcase the
Azure catalog. One unified, governable platform minimizes cost, operational overhead,
and the audit/residency surface; every extra engine fragments governance and lineage.
(Trace: `1_azure_services.md` Final Decision + Explicitly Excluded table.)

### VI. Explainability & Responsible AI (NON-NEGOTIABLE)

Every prediction and recommendation MUST carry human-understandable evidence and
rationale sufficient for the reviewing role to decide, and MUST surface
uncertainty/confidence. GenAI answers MUST be grounded with citations and MUST decline
rather than fabricate when no source exists. All generative outputs MUST pass Azure AI
Content Safety. Degraded, missing, delayed, or stale telemetry MUST be flagged as
reduced-confidence or unavailable — and MUST NEVER be presented as current.

**Rationale**: A reviewer can only exercise meaningful human oversight (Principle I) if
the system shows its reasoning, its confidence, and the freshness of its inputs.
Grounded, safety-filtered, uncertainty-aware outputs are what make the decision-support
role trustworthy and Responsible-AI compliant. (Trace: NFR-006, FR-018, FR-019, FR-022;
spec edge cases "GenAI hallucination", "Missing/delayed telemetry".)

### VII. Role-Based Access & Per-Site Isolation (NON-NEGOTIABLE)

Access to data, predictions, recommendations, and approval actions MUST be restricted
by persona — operator, maintenance, energy, quality, executive/ESG, and compliance/DPO
— via Microsoft Entra ID, following least-privilege. Data and recommendations MUST be
scoped per site so that phased onboarding never cross-contaminates data between
onboarded and not-yet-onboarded sites.

**Rationale**: Different roles bear different responsibilities and liabilities, and a
four-site, four-country rollout proceeds incrementally; least-privilege plus strict
per-site isolation prevents both unauthorized access and data bleed during scale-out.
(Trace: NFR-005, NFR-007; spec edge case "Site/country onboarding mid-rollout".)

### VIII. Contract-First, Test-First Engineering (NON-NEGOTIABLE)

Shared data contracts (`libs/NovaSteel.Contracts`, `libs/novasteel_core`) are the
single source of truth for all telemetry, market, and decision payloads. Contract
changes MUST be validated against golden fixtures (`libs/fixtures`). Tests precede
implementation (TDD): contract tests, integration tests for agent decision logging, and
model evaluation/drift gates MUST exist and pass before a workload ships. Producers and
consumers MUST share one schema and one fixture set.

**Rationale**: Multiple agents and pillars exchange the same telemetry and decision
payloads; a single shared, test-first contract prevents silent schema drift across
producers and consumers and makes traceability (Principle II) enforceable at the data
layer. (Trace: NFR-003, FR-017; repository structure `libs/NovaSteel.Contracts`,
`libs/novasteel_core`, `libs/fixtures`.)

### IX. Synthetic-Data Integrity (NON-NEGOTIABLE)

ANY synthetic, simulated, or test telemetry source MUST emit data conforming to the
production contracts (`libs/NovaSteel.Contracts`) on the SAME ingestion path as real
OT, AND every synthetic reading MUST carry an unambiguous synthetic-origin marker that
is preserved end-to-end. Synthetic data MUST NEVER be presentable as real plant data in
storage, models, dashboards, KPI baselines, or the audit trail. Provenance (synthetic
vs. real) MUST be queryable wherever the data lands. Concrete synthetic-data generators
are defined in the implementation plan, not in this constitution.

**Rationale**: The demo and early phases rely on synthetic telemetry; if synthetic
readings can masquerade as real plant data, every downstream claim — KPI baselines,
model accuracy, audit records — becomes untrustworthy. A preserved provenance marker
keeps the proof honest. (Trace: NFR-003, FR-017, FR-022.)

### X. Phased Delivery (guidance)

Deliver value at one furnace/site before multi-line and four-country scale-out. Each
pillar (P1 maintenance → P2 energy → P3 quality → P4 knowledge) SHOULD be independently
shippable per spec priority. Prefer the simplest in-scope service that meets the need
(YAGNI); justify any addition in Complexity Tracking.

**Rationale**: Proving value at a single pilot site de-risks the program and funds
scale-out; independently shippable pillars and YAGNI keep scope honest. This principle
is advisory guidance, not a merge-blocking gate. (Trace: NFR-007, SC-009.)

## Additional Constraints

- **Cloud-native, EU-resident, greenfield** on managed PaaS (Azure Container Apps /
  Azure Functions); NO virtual machines.
- **Private access** to all PaaS via VNet + Private Link; secrets in Azure Key Vault
  using customer-managed keys (BYOK/CMK).
- **Infrastructure as Code** is Bicep (under `infrastructure/`); CI/CD is GitHub
  Actions — a single delivery stack (no Azure DevOps / Pipelines).
- **Observability** (Azure Monitor / Application Insights) is mandatory for all agents
  and for MLOps (drift detection and SLO monitoring).

## Governance

This constitution supersedes all other practices, conventions, and ad-hoc decisions.
Every plan, pull request, and review MUST verify compliance with Principles I–IX
(Principle X is advisory). A violation of any NON-NEGOTIABLE principle (I–IX) BLOCKS
merge. Any deviation requires an entry in the plan's **Complexity Tracking** section
that names the simpler in-scope alternative that was rejected and explains why. The
feature specification (`spec.md`, via its FR/NFR IDs) is the authority for requirement
traceability; where a principle and a downstream artifact appear to conflict, this
constitution and the cited spec requirement prevail.

**Amendment & versioning policy**: Amendments MUST be proposed as a change to this
file, documenting the rationale and the affected principles, and MUST update the
version below using semantic versioning:

- **MAJOR**: Backward-incompatible governance changes — removing or redefining a
  principle, or removing a NON-NEGOTIABLE constraint.
- **MINOR**: Adding a new principle or section, or materially expanding guidance.
- **PATCH**: Clarifications, wording, or typo fixes with no semantic change.

Each amendment MUST refresh the Sync Impact Report at the top of this file and check
the dependent templates (`plan-template.md`, `spec-template.md`, `tasks-template.md`)
and the agent context guidance for alignment, flagging — not silently skipping — any
that reference constitution principles.

**Compliance review**: Compliance is reviewed at every plan gate (Constitution Check,
pre-Phase-0 and post-Phase-1) and at every pull-request review. The reviewing role MUST
confirm Principles I–IX explicitly; unresolved NON-NEGOTIABLE violations are not
mergeable. This constitution is the runtime governance guide for all NovaSteel
development.

**Version**: 1.0.0 | **Ratified**: 2026-06-23 | **Last Amended**: 2026-06-23
