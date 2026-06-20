# Project Ignition — NovaSteel Demo Workspace

> **Purpose** — This folder contains the complete plan to build, cost, secure
> and present NovaSteel's **AI-powered steel production optimization platform**
> to a customer jury aligned to [10 — Target audience roles](10-target-audience-roles.md),
> including **COO, Head of Quality, Head of Sustainability / ESG,
> Compliance Officer, Data Protection Officer (DPO), and CFO**.
>
> All figures are **illustrative demo estimates** unless stated otherwise. They
> require a detailed Azure assessment before any commercial commitment.

## How this workspace is organised

| # | Document | Audience | What it answers |
| - | -------- | -------- | --------------- |
| 00 | [Executive summary](00-executive-summary.md) | Whole jury | Why, what, value — on one page |
| 01 | [Project charter](01-project-charter.md) | COO, sponsors | Scope, stakeholders, governance, KPIs |
| 02 | [Solution architecture](02-solution-architecture.md) | COO, architects | The Azure reference architecture |
| 02a | [Fabric + IoT architecture](02a-fabric-iot-architecture.md) | Architects, data teams | The Microsoft Fabric estate & IoT ingestion, by layer |
| 03 | [Data & AI design](03-data-and-ai-design.md) | Head of Quality, Head of Data Science / ML Lead | The three AI workloads & Responsible AI |
| 04 | [Implementation plan](04-implementation-plan.md) | COO, PMO | Phased roadmap, team, risks |
| 05 | [Cost estimate & ROI](05-cost-estimate.md) | CFO, Head of Energy Management, Head of Sustainability / ESG | TCO, benefits, ROI/NPV/payback |
| 06 | [Security & compliance](06-security-compliance.md) | Compliance Officer, Data Protection Officer (DPO) | GDPR, EU AI Act, Responsible AI |
| 07 | [Presentation deck](07-presentation-deck.md) | Head of Sustainability / ESG, all | Slide-by-slide narrative |
| 08 | [Demo script](08-demo-script.md) | Presenter | Live walkthrough |
| 09 | [GitHub Agents guide](09-github-agents.md) | Delivery team | How to use the agents that build this |
| 10 | [Target audience roles](10-target-audience-roles.md) | All authors | Canonical role taxonomy and priorities |

## The business case in one paragraph

NovaSteel is a Luxembourg-based integrated steel producer operating blast
furnaces and rolling mills across Luxembourg, Germany, Belgium and Spain. Energy
is 35% of production cost, CO₂ is under EU ETS pressure, furnace-lining failures
cost ~**€8M** each, high-grade automotive quality is inconsistent, and retiring
operators are taking tacit knowledge with them. *Project Ignition* deploys an
Azure AI platform that targets **−14% energy/ton**, **−22% CO₂**, **21-day**
furnace-failure warning, and **+8%** high-grade yield.

## The GitHub Agents that build it

The `.github/agents/` folder defines nine custom agents — one per discipline —
that produce and maintain the documents above. See
[09-github-agents.md](09-github-agents.md) for how to invoke them.

All agent prompts should use the canonical role names in
[10 — Target audience roles](10-target-audience-roles.md) and stay aligned with
the executive narrative in [07 — Presentation deck](07-presentation-deck.md).

| Agent | Owns | Primary target roles | Deck touchpoints |
| ----- | ---- | -------------------- | ---------------- |
| `solution-architect` | 02 Architecture | COO (1), Head of Manufacturing / VP Operations (2), Plant Director / Site Manager (3), CTO / Head of IT/OT (4) | Slides 4, 6, 14, 16 |
| `data-platform-engineer` | 02a Fabric + IoT | CTO / Head of IT/OT (4), CISO (8), Chief Data Officer (CDO) (12), OT Engineer / Automation Engineer (15) | Slides 6, 14, 15 |
| `azure-data-expert` | Cross-cutting 02/02a/03 (Fabric + IoT + Apps + AI) | CTO / Head of IT/OT (4), CISO (8), Chief Data Officer (CDO) (12), Head of Data Science / ML Lead (13), AI Architect / Digital Twin Architect (14), OT Engineer / Automation Engineer (15) | Slides 6, 14, 15 |
| `ai-ml-engineer` | 03 Data & AI | Head of Quality (6), Head of Energy Management (7), Head of Data Science / ML Lead (13) | Slides 7, 8, 9, 15 |
| `business-value-cfo` | 05 Cost & ROI | COO (1), Head of Energy Management (7), Head of Sustainability / ESG (11), CFO (19) | Slides 5, 12, 16 |
| `compliance-officer` | 06 Security & compliance | CISO (8), Compliance Officer (9), Data Protection Officer (DPO) (10) | Slides 13, 16 |
| `quality-engineer` | Quality sections of 01/03 | Head of Manufacturing / VP Operations (2), Plant Director / Site Manager (3), Head of Quality (6) | Slides 9, 10, 16 |
| `demo-implementation` | 08 Demo | COO (1), Head of Manufacturing / VP Operations (2), Head of Quality (6), Compliance Officer (9), Data Protection Officer (DPO) (10), Head of Sustainability / ESG (11), CFO (19) | Slide 15, proof claims on 5, 13, 16 |
| `presentation-storyteller` | 07 Deck | COO (1), Head of Manufacturing / VP Operations (2), Head of Quality (6), Head of Sustainability / ESG (11), Compliance Officer (9), Data Protection Officer (DPO) (10), CFO (19) | Slides 1–16 |

## Suggested reading order for the jury session

1. Start with **00 — Executive summary**.
2. Walk the **07 — Presentation deck** end to end.
3. Drill into **02 / 05 / 06** for the technical, financial and compliance deep
   dives as questions arise.
4. Run the **08 — Demo script** live.

## Mapping to the evaluation rubric

How this submission addresses the
[Azure Master Architect grading rubric](../0_Analysis/rating_grid.md):

| Rubric area | Where it is evidenced |
| ----------- | --------------------- |
| **Design** — architecture, modularity, scalability | [02 — Architecture](02-solution-architecture.md) (incl. §4a design patterns), [02a — Fabric + IoT](02a-fabric-iot-architecture.md) |
| **Design** — design patterns | [02 — §4a Architecture & design patterns](02-solution-architecture.md) |
| **Design** — security | [06 — Security & compliance](06-security-compliance.md), [02 — §4 WAF security](02-solution-architecture.md) |
| **Development** — application demo | [08 — Demo script](08-demo-script.md), `apps/steel_factory_simulator/` |
| **Development** — implementation completeness | [infrastructure/](../../../infrastructure/README.md) (Bicep), [04 — Implementation plan](04-implementation-plan.md) |
| **Monitoring** — logging & metrics | [02 — §4b Monitoring & observability](02-solution-architecture.md), [03 — §5 MLOps](03-data-and-ai-design.md) |
| **AI Integration** — AI tech & model selection/deployment | [03 — Data & AI design](03-data-and-ai-design.md) (incl. §9 model selection rationale) |
| **Agentic Behavior** — autonomy & orchestration | [03 — §8 Agentic behaviour & autonomy](03-data-and-ai-design.md) |
| **Agentic Behavior** — multi-agent coordination | [09 — GitHub Agents guide](09-github-agents.md) |
| **Additional Architecture** — performance & reliability | [02 — §4 WAF highlights](02-solution-architecture.md) |
| **Presentation & Documentation** — clarity & audience fit | [07 — Deck](07-presentation-deck.md), [10 — Target audience roles](10-target-audience-roles.md) |
