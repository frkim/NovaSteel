<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
at specs/001-steel-optimization-platform/plan.md (with its Phase 1 design
artifacts: research.md, data-model.md, contracts/, quickstart.md).

## NovaSteel — Active Spec Kit Context

**Project**: NovaSteel "Project Ignition" — AI-Powered Steel Production Optimization
Platform. Decision-support only across four EU sites; four pillars (P1 predictive
maintenance → P2 energy dispatch → P3 quality optimization → P4 knowledge capture).

**Active feature**: `001-steel-optimization-platform`
(`specs/001-steel-optimization-platform/spec.md`).

**Constitution**: v2.0.0 (ratified 2026-06-23; last amended 2026-07-20) —
`.specify/memory/constitution.md`. Every plan, pull request, and review MUST verify
compliance. A violation of any NON-NEGOTIABLE principle (I–IX) BLOCKS merge; any
deviation requires a Complexity Tracking entry.

### NON-NEGOTIABLE principles (I–IX)
- **I. Human-in-the-Loop** — decision-support only; NEVER actuate/control plant
  equipment; every recommendation needs explicit human approval; unactioned
  recommendations lapse safely.
- **II. End-to-End Traceability** — immutable, queryable audit record (inputs, model
  version, output, reviewer, timestamp, rationale); lineage in Microsoft Purview;
  audit records exempt from GDPR erasure, raw personal content stays erasable.
- **III. EU Data Residency (EU-default with governed exceptions)** — EU regions (Sweden
  Central / West Europe / Germany West Central / France Central) are the enforced default
  (Azure Policy allowed-locations); a non-EU region is permitted ONLY as a documented,
  minimized, labelled, time-bounded last resort when a required service is unavailable in
  every EU region.
- **IV. One-Way OT→IT Boundary** — telemetry flows one-way out of OT; NO control/command
  path back into OT/SCADA; cloud-direct ingestion via Azure IoT Hub (no plant-side edge).
- **V. Scoped, Unified Stack** — only in-scope services (see tech stack below) may be
  introduced; listed services are FORBIDDEN without documented Complexity Tracking.
- **VI. Explainability & Responsible AI** — outputs carry evidence, rationale, and
  uncertainty; GenAI grounded with citations and declines rather than fabricates; all
  generative output passes Azure AI Content Safety; stale/missing telemetry flagged.
- **VII. Role-Based Access & Per-Site Isolation** — least-privilege by persona via
  Microsoft Entra ID; data/recommendations scoped per site (no cross-site bleed).
- **VIII. Contract-First, Test-First Engineering** — shared contracts
  (`libs/NovaSteel.Contracts`, `libs/novasteel_core`) are the single source of truth;
  golden fixtures (`libs/fixtures`); TDD — contract/integration/eval tests precede ship.
- **IX. Synthetic-Data Integrity** — synthetic telemetry conforms to production
  contracts on the same ingestion path, carries a preserved synthetic-origin marker, and
  is NEVER presentable as real plant data; provenance queryable wherever data lands.
- **X. Phased Delivery** (advisory) — prove value at one furnace/site before scale-out;
  pillars independently shippable; prefer simplest in-scope service (YAGNI).

### Scoped tech stack (Principle V)
- **Data + ML**: Microsoft Fabric (OneLake, Data Factory, Data Engineering, Data
  Science, Real-Time Intelligence, Power BI).
- **AI**: Microsoft Foundry (Agent Service, Foundry IQ, Azure OpenAI / Foundry Models,
  AI Services incl. Content Safety).
- **Ingestion**: Azure IoT Hub + Event Hubs (cloud-direct; no IoT Edge in scope).
- **Compute**: Azure Functions + Azure Container Apps (managed PaaS; NO virtual machines).
- **Security/Governance/Ops**: Entra ID, Key Vault (CMK/BYOK), Azure Policy, Purview,
  Defender for Cloud, Azure Monitor / Application Insights, VNet + Private Link,
  ADLS Gen2 / OneLake + Blob Storage.
- **IaC**: Bicep (under `infrastructure/`). **CI/CD**: GitHub Actions (no Azure DevOps).
- **Residency**: EU regions only, enforced as policy-as-code.
<!-- SPECKIT END -->
