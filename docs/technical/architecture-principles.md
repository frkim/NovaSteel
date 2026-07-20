# NovaSteel Platform — Architecture & Governance Principles

> **Purpose.** This page explains the **choices and reasoning** behind the NovaSteel
> "Project Ignition" platform principles in plain language. It is a companion to the
> authoritative, normative source — the **Constitution v2.0.0**
> ([`docs/usecase/0_specs/NovaSteel/.specify/memory/constitution.md`](../usecase/0_specs/NovaSteel/.specify/memory/constitution.md)).
> Where this page and the Constitution differ, **the Constitution prevails.**

NovaSteel is an **AI-powered steel-production optimization platform** delivering predictive
maintenance, energy dispatch, quality optimization, and knowledge capture across four EU
sites. It is **decision-support only**. Every plan, pull request, and review is measured
against the principles below.

- **Principles I–IX are NON-NEGOTIABLE** — a violation **blocks merge**.
- **Principle X is advisory** guidance.
- Any deviation from I–IX requires a **Complexity-Tracking** entry naming the simpler,
  in-scope alternative that was rejected and why.

---

## At a glance

| # | Principle | One-line rule | Primary driver |
|---|-----------|---------------|----------------|
| I | Human-in-the-Loop | Advise, never actuate; every recommendation needs human approval | Safety & EU AI Act oversight |
| II | End-to-End Traceability | Immutable audit record + Purview lineage for every decision | Regulatory defensibility & trust |
| III | EU Data Residency (EU-default, governed exceptions) | EU regions are the enforced default; non-EU only as a documented last resort | EU data sovereignty |
| IV | One-Way OT→IT Boundary | Telemetry flows out of OT only; no command path back to OT/SCADA | Plant safety & attack surface |
| V | Scoped, Unified Stack | Only the in-scope Fabric + Foundry + IoT/PaaS service set | Governability, cost, lineage |
| VI | Explainability & Responsible AI | Evidence, uncertainty, grounded GenAI, Content Safety | Trustworthy human oversight |
| VII | Role-Based Access & Per-Site Isolation | Least-privilege by persona; no cross-site data bleed | Least-privilege & phased rollout |
| VIII | Contract-First, Test-First | Shared contracts + golden fixtures; TDD before ship | Prevents schema drift |
| IX | Synthetic-Data Integrity | Synthetic data marked end-to-end; never shown as real | Honest KPIs & audit |
| X | Phased Delivery *(advisory)* | Prove value at one site first; YAGNI | De-risk the program |

---

## I. Human-in-the-Loop (NON-NEGOTIABLE)

**The rule.** The platform is **decision-support only**. It must never directly actuate or
control plant equipment under any pillar. Every prediction and recommendation must be
presented to the authorized human role and **explicitly confirmed** before any downstream
action. Time-sensitive recommendations that receive no approval **lapse safely** (no
action) and are recorded as unactioned. Cross-pillar conflicts are surfaced for human
resolution, never auto-resolved.

**Why this choice.** Steelmaking is safety-critical; an erroneous autonomous action can
injure people or destroy a heat. Decision-support-only is the foundational risk control
and the basis for **EU AI Act high-risk human-oversight** obligations. Keeping a human as
the actuator means accountability always lands on an authorized person.

**In practice.** No "auto-apply" mode exists. UI flows require an explicit approve/reject;
unactioned items expire and are logged (feeds Principle II).
*(Trace: NFR-001, FR-015, FR-016, FR-021.)*

---

## II. End-to-End Traceability (NON-NEGOTIABLE)

**The rule.** Every prediction, recommendation, and human decision produces an
**immutable, queryable audit record**: inputs/evidence, model or logic version, output,
reviewer identity, timestamp, and rationale. Data lineage (sensor → feature → model →
report) is captured in **Microsoft Purview**. Audit records are exempt from GDPR erasure
(Art. 17(3)(b) legal-obligation exception); non-audit personal content (e.g. raw interview
recordings/transcripts) **remains erasable**. Personal data in audit records is minimized
(e.g. pseudonymized reviewer identity).

**Why this choice.** Regulatory defensibility and operational trust both require that any
output can be **reconstructed and explained after the fact**. Immutable audit + lineage
make accountability *verifiable* rather than merely asserted.

**In practice.** Decisions are written to an append-only store; lineage is registered in
Purview; GDPR erasure logic distinguishes audit vs. raw personal content.
*(Trace: NFR-003, FR-017, FR-024, NFR-008.)*

---

## III. EU Data Residency — EU-Default with Governed Exceptions (NON-NEGOTIABLE)

**The rule.** EU regions (**Sweden Central / West Europe / Germany West Central / France
Central**) are the **default and enforced** location for **all** data — telemetry, models,
operator interviews, audit logs. EU residency is the default, **enforced by Azure Policy**
(allowed-locations), not by convention. A non-EU region is permitted **only as a last
resort** when a required service is genuinely unavailable in every EU region, and only via a
**documented, minimized, labelled, time-bounded exception** (Complexity Tracking).

**Why this choice.** NovaSteel operates under EU data-sovereignty expectations across four
member states, so EU residency stays the enforced default and cannot depend on human
vigilance. But some required managed services are region-constrained by the tenant/provider;
a narrow, documented, minimized last-resort exception keeps the programme deliverable
without turning residency into a silent, unmanaged compromise.

**In practice.** An allowed-locations Azure Policy is assigned at subscription scope
(`enforceEuResidencyPolicy`) and lists the EU regions. Region-constrained services are first
pinned to another **EU** region (e.g. IoT Hub → West Europe, since it is not available in
Sweden Central). Only where **no** EU region supports a required service (e.g. a managed
service whose tenant service location is non-EU) may a non-EU region be used, via a
documented policy exemption/`notScopes` exception tagged as a residency exception.
*(Trace: NFR-002, SC-006.)*

---

## IV. One-Way OT→IT Boundary (NON-NEGOTIABLE)

**The rule.** Plant telemetry flows **one way**, out of the operational-technology (OT)
environment into IT/cloud. **No** control or command path back into OT/SCADA may exist in
code, infrastructure, or configuration. Ingestion is **cloud-direct via Azure IoT Hub**,
with **no plant-side edge runtime** in scope. Any component that attempts, enables, or even
*implies* a reverse path is a violation and must fail review.

**Why this choice — the reasoning.**

1. **Safety is the primary driver.** The OT/SCADA layer (PLCs, furnace controllers)
   physically actuates a process handling molten metal at ~1,500 °C. If a compromised or
   buggy cloud/IT component could send commands *back* into OT, a software fault or an
   attacker could injure people or destroy a heat. A structurally unidirectional boundary
   means the corporate/cloud attack surface **cannot reach** the equipment that moves
   molten steel — the dangerous path does not exist to be exploited. This is the physical
   backing for **Principle I**: even the platform's recommendations can't auto-actuate,
   because there is no wire back to OT.

2. **Structurally, not by firewall rule.** The reverse path must **not exist by design**,
   not merely be "blocked." A firewall rule can be misconfigured, disabled, or bypassed;
   an absent architectural path cannot.

3. **Aligns with industrial-security best practice (Purdue / IEC 62443).** Data may egress
   *upward* from OT zones to enterprise/cloud, but control must never flow the other way
   across the IT/OT boundary. NovaSteel encodes that industry norm as a non-negotiable
   rule rather than leaving it to engineers' discipline.

4. **Why cloud-direct via IoT Hub, no IoT Edge.** A plant-side edge runtime is another
   managed component adjacent to OT that could host modules and, in principle, a command
   path. Excluding it keeps ingestion a **one-way pipe** (device → IoT Hub → cloud) with
   nothing plant-side to subvert — and keeps the footprint minimal (consistent with
   Principle V, which forbids IoT Edge/IoT Operations without justification).

5. **Governance & regulatory fit.** Keeping the AI strictly out of the actuation loop
   supports EU AI Act human-oversight, and a one-way flow means every action on the plant
   is a *human* action recorded in the audit trail (Principle II), not an opaque
   machine-to-machine command.

**In practice / watch-outs.** Any request to "send a setpoint/command to the plant," a
write-back to SCADA, or an on-prem IoT Edge module is a **constitution violation** and must
be rejected or escalated via Complexity Tracking.
*(Trace: NFR-004, FR-018; spec edge case "OT boundary integrity".)*

---

## V. Scoped, Unified Stack (NON-NEGOTIABLE)

**The rule.** The platform is concentrated in **Microsoft Fabric** (data + ML) and
**Microsoft Foundry** (AI), with a minimal **IoT + PaaS compute** footprint. Only the
in-scope services (see below) may be introduced. Explicitly **forbidden** without a
documented Complexity-Tracking justification: Azure Machine Learning, Azure Databricks,
standalone Azure Data Factory, Azure IoT Edge / IoT Operations, Azure IoT Central,
standalone Azure Data Explorer, Azure Stream Analytics, Azure Arc, **AKS**, **Azure Virtual
Machines**, Azure DevOps / Pipelines, Azure Stack, Azure Sphere.

**Why this choice.** The goal is to solve NovaSteel's four challenges, **not to showcase
the Azure catalog**. One unified, governable platform minimizes cost, operational
overhead, and the audit/residency surface. Every extra engine fragments governance and
lineage (weakening Principles II and III).

**In-scope service set.**
- **Data + ML:** Microsoft Fabric — OneLake, Data Factory, Data Engineering, Data Science,
  Real-Time Intelligence, Power BI.
- **AI:** Microsoft Foundry — Agent Service, Foundry IQ, Azure OpenAI / Foundry Models,
  AI Services incl. Content Safety.
- **Ingestion:** Azure IoT Hub + Event Hubs (cloud-direct; no IoT Edge).
- **Compute:** Azure Functions + Azure Container Apps (managed PaaS; **no VMs**).
- **Security / Governance / Ops:** Entra ID, Key Vault (CMK/BYOK), Azure Policy, Purview,
  Defender for Cloud, Azure Monitor / Application Insights, VNet + Private Link,
  ADLS Gen2 / OneLake + Blob Storage.
- **IaC:** Bicep (`infrastructure/`). **CI/CD:** GitHub Actions (no Azure DevOps).

*(Trace: `1_azure_services.md` Final Decision + Explicitly Excluded table.)*

---

## VI. Explainability & Responsible AI (NON-NEGOTIABLE)

**The rule.** Every prediction and recommendation carries human-understandable **evidence
and rationale** sufficient for the reviewing role to decide, and surfaces
**uncertainty/confidence**. GenAI answers are **grounded with citations** and **decline
rather than fabricate** when no source exists. All generative output passes **Azure AI
Content Safety**. Degraded, missing, delayed, or stale telemetry is flagged as
reduced-confidence or unavailable — and **never** presented as current.

**Why this choice.** A reviewer can only exercise meaningful human oversight (Principle I)
if the system shows its reasoning, its confidence, and the freshness of its inputs.
Grounded, safety-filtered, uncertainty-aware outputs are what make the decision-support
role trustworthy and Responsible-AI compliant.

**In practice.** Predictions ship with evidence + confidence; RAG answers cite sources or
abstain; a Content Safety gate wraps generative output; stale telemetry is badged.
*(Trace: NFR-006, FR-018, FR-019, FR-022.)*

---

## VII. Role-Based Access & Per-Site Isolation (NON-NEGOTIABLE)

**The rule.** Access to data, predictions, recommendations, and approval actions is
restricted by **persona** — operator, maintenance, energy, quality, executive/ESG,
compliance/DPO — via **Microsoft Entra ID**, following least-privilege. Data and
recommendations are **scoped per site** so phased onboarding never cross-contaminates data
between onboarded and not-yet-onboarded sites.

**Why this choice.** Different roles bear different responsibilities and liabilities, and a
four-site, four-country rollout proceeds incrementally. Least-privilege plus strict
per-site isolation prevents both unauthorized access and data bleed during scale-out.

**In practice.** Entra groups/roles per persona; workspace and data scoping per site;
onboarding a new site does not expose it to (or from) existing sites.
*(Trace: NFR-005, NFR-007; spec edge case "Site/country onboarding mid-rollout".)*

---

## VIII. Contract-First, Test-First Engineering (NON-NEGOTIABLE)

**The rule.** Shared data contracts (`libs/NovaSteel.Contracts`, `libs/novasteel_core`)
are the **single source of truth** for all telemetry, market, and decision payloads.
Contract changes are validated against **golden fixtures** (`libs/fixtures`). Tests precede
implementation (**TDD**): contract tests, integration tests for agent decision logging, and
model evaluation/drift gates must exist and pass before a workload ships. Producers and
consumers share one schema and one fixture set.

**Why this choice.** Multiple agents and pillars exchange the same payloads; a single
shared, test-first contract prevents **silent schema drift** across producers and consumers
and makes traceability (Principle II) enforceable at the data layer.

**In practice.** Build/test the contracts before consumers; new fields go through the
contract + fixtures first.
*(Trace: NFR-003, FR-017.)*

---

## IX. Synthetic-Data Integrity (NON-NEGOTIABLE)

**The rule.** Any synthetic, simulated, or test telemetry source emits data conforming to
the **production contracts** on the **same ingestion path** as real OT, and every synthetic
reading carries an **unambiguous synthetic-origin marker** preserved end-to-end. Synthetic
data is **never** presentable as real plant data in storage, models, dashboards, KPI
baselines, or the audit trail. Provenance (synthetic vs. real) is queryable wherever the
data lands.

**Why this choice.** The demo and early phases rely on synthetic telemetry. If synthetic
readings can masquerade as real, every downstream claim — KPI baselines, model accuracy,
audit records — becomes untrustworthy. A preserved provenance marker keeps the proof
honest.

**In practice.** The steel-factory simulator stamps each reading with an origin marker
(`Origin.Synthetic`) that flows through ingestion, storage, and the UI; charts and tables
display origin so synthetic data is never mistaken for real.
*(Trace: NFR-003, FR-017, FR-022.)*

---

## X. Phased Delivery (advisory)

**The guidance.** Deliver value at **one furnace/site** before multi-line and four-country
scale-out. Each pillar (**P1** maintenance → **P2** energy → **P3** quality → **P4**
knowledge) should be **independently shippable** per spec priority. Prefer the simplest
in-scope service that meets the need (**YAGNI**); justify any addition in Complexity
Tracking.

**Why this choice.** Proving value at a single pilot site de-risks the program and funds
scale-out; independently shippable pillars and YAGNI keep scope honest. This principle is
advisory guidance, **not** a merge-blocking gate.
*(Trace: NFR-007, SC-009.)*

---

## Governance

- This constitution **supersedes** all other practices, conventions, and ad-hoc decisions.
- Every plan, PR, and review must **explicitly verify** Principles I–IX (X is advisory).
- A violation of any NON-NEGOTIABLE principle (I–IX) **blocks merge**. Any deviation
  requires a **Complexity-Tracking** entry naming the simpler in-scope alternative rejected
  and why.
- The feature specification (`spec.md`, via its FR/NFR IDs) is the authority for
  requirement traceability; where a principle and a downstream artifact conflict, the
  Constitution and the cited spec requirement prevail.

**Amendment & versioning (semantic versioning):**

| Bump | When |
|------|------|
| **MAJOR** | Backward-incompatible governance change — removing/redefining a principle, or removing a NON-NEGOTIABLE constraint |
| **MINOR** | Adding a new principle/section, or materially expanding guidance |
| **PATCH** | Clarifications, wording, or typo fixes with no semantic change |

Each amendment refreshes the Constitution's Sync Impact Report and checks dependent
templates and agent-context guidance for alignment.

---

**Source of truth:** Constitution **v2.0.0** — Ratified 2026-06-23 · Last Amended 2026-07-20
· [`docs/usecase/0_specs/NovaSteel/.specify/memory/constitution.md`](../usecase/0_specs/NovaSteel/.specify/memory/constitution.md).
This page is explanatory; if it drifts from the Constitution, update it or open an
amendment.
