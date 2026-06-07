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
| 06 | [Security & compliance](06-security-compliance.md) | Compliance Officer, DPO | GDPR, EU AI Act, Responsible AI |
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

The `.github/agents/` folder defines six custom agents — one per discipline —
that produce and maintain the documents above. See
[09-github-agents.md](09-github-agents.md) for how to invoke them.

| Agent | Owns | Primary jury persona |
| ----- | ---- | -------------------- |
| `solution-architect` | 02 Architecture | COO |
| `ai-ml-engineer` | 03 Data & AI | Head of Data Science / ML Lead |
| `business-value-cfo` | 05 Cost & ROI | CFO |
| `compliance-officer` | 06 Security & compliance | Compliance Officer + DPO |
| `quality-engineer` | Quality sections of 01/03 | Head of Quality |
| `presentation-storyteller` | 07 Deck, 08 Demo | Head of Sustainability / ESG |

## Suggested reading order for the jury session

1. Start with **00 — Executive summary**.
2. Walk the **07 — Presentation deck** end to end.
3. Drill into **02 / 05 / 06** for the technical, financial and compliance deep
   dives as questions arise.
4. Run the **08 — Demo script** live.
