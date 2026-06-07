# 01 — Project Charter

**Project Ignition** — NovaSteel AI-Powered Steel Production Optimization Platform

---

## 1. Purpose & background

NovaSteel is a Luxembourg-based integrated steel producer operating blast
furnaces, basic-oxygen and electric-arc furnaces, and rolling mills across
Luxembourg, Germany, Belgium and Spain. The company faces rising energy and
carbon costs, unpredictable and catastrophic furnace-lining failures, quality
inconsistency in high-grade automotive steel, and the loss of tacit expertise as
skilled operators retire.

*Project Ignition* establishes an **Azure AI platform** to optimize energy,
predict equipment failures, improve quality, and capture operational expertise.

## 2. Objectives & success criteria

| # | Objective | KPI | Target | Baseline owner |
| - | --------- | --- | ------ | -------------- |
| O1 | Cut energy intensity | Energy per ton (kWh/t, €/t) | **−14%** | COO / Energy |
| O2 | Cut emissions | CO₂ per ton (tCO₂/t) | **−22%** | Head of Sustainability / ESG |
| O3 | Prevent furnace failures | Lead time of lining-failure alert | **≥ 21 days** | COO / Maintenance |
| O4 | Improve quality | High-grade yield; Cp/Cpk | **+8%** yield | Head of Quality |
| O5 | Capture knowledge | Procedures captured; assistant usage | Library live, adopted | COO / HR |

Success = pilot demonstrates O1, O3 and O4 on real data within target, with O2
modelled, and a compliant path to scale.

## 3. Scope

**In scope (pilot):** one furnace line and its rolling path; ingestion of
historian/OT telemetry; the three AI workloads (predictive maintenance, energy
optimization, knowledge capture); dashboards; security, governance and
compliance baseline.

**In scope (scale phase):** remaining lines across the four sites; full MLOps;
integration with maintenance (CMMS/ERP) and energy procurement.

**Out of scope:** replacing the historian/SCADA/MES systems; automated control
actions without human approval; changing metallurgical certification regimes;
HR decisions about staff.

## 4. Stakeholders aligned to target audience roles

| Role | Interest | What they need to approve |
| ---- | -------- | ------------------------- |
| **COO** | Operations, reliability, uptime | Operational excellence, avoided €8M failures |
| **Head of Manufacturing / VP Operations** | Cross-site performance | Repeatable operating model and scale readiness |
| **Plant Director / Site Manager** | Site-level continuity | Daily reliability and operator usability |
| **CTO / Head of IT/OT** | Technical feasibility and OT/IT safety | Integration with SCADA/PLC/historian and security controls |
| **Head of Maintenance / Reliability Engineering Lead** | Asset life and outage risk | 21-day warning quality and maintenance workflow fit |
| **Head of Quality** | Grade conformance, traceability | Yield & consistency without losing control ([03](03-data-and-ai-design.md)) |
| **Head of Energy Management** | Energy and dispatch economics | Proven optimization against price and carbon signals |
| **Head of Sustainability / ESG** | ETS exposure and reporting credibility | The −22% CO₂ narrative with auditable evidence ([07](07-presentation-deck.md)) |
| **Compliance Officer** | AI governance and auditability | Risk classification & controls ([06](06-security-compliance.md)) |
| **Data Protection Officer (DPO)** | GDPR legality and privacy controls | DPIA, minimization, retention and rights coverage ([06](06-security-compliance.md)) |
| **CFO** | Cost, ROI, risk | TCO, payback, sensitivity ([05](05-cost-estimate.md)) |
| Microsoft CSA (you) | Solution & enablement | Architecture, demo, enablement |
| Plant operators / metallurgists | Daily use | Trustworthy, human-in-the-loop tools |

## 5. Governance & decision gates

```text
G0 Mobilize ──► G1 Pilot design ──► G2 Pilot live ──► G3 Pilot review ──► G4 Scale decision
```

- **Steering committee:** COO (sponsor), Head of Manufacturing / VP Operations,
  CTO / Head of IT/OT, Head of Quality, Head of Energy Management, Head of
  Sustainability / ESG, Compliance Officer, Data Protection Officer (DPO), CFO,
  Microsoft CSA. Meets at each gate.
- **Working cadence:** 2-week iterations; demo every iteration.
- **Decision rights:** Steering approves gates and budget; Product Owner
  prioritizes the backlog; Architecture Review Board approves design changes.

## 6. High-level milestones

See **[04 — Implementation plan](04-implementation-plan.md)** for the detailed,
phased roadmap. Headline: **Mobilize → Foundation → Pilot → Review → Scale.**

## 7. Assumptions

- Historian/OT data is accessible and reasonably complete for the pilot line.
- A lawful basis and DPIA cover any personal data in knowledge capture.
- EU regions (West Europe / Germany West Central) are acceptable for residency.
- NovaSteel provides SMEs (metallurgist, energy manager, maintenance lead).

## 8. Risks (summary)

| Risk | Impact | Mitigation |
| ---- | ------ | ---------- |
| Data quality / gaps in historian | Model accuracy | Data assessment in Foundation phase; synthetic augmentation for demo |
| OT/IT security boundary | Plant safety | Respect Purdue model; one-way edge ingestion; Defender for IoT |
| Change resistance from operators | Adoption | Human-in-the-loop design; co-design with operators |
| Regulatory uncertainty (AI Act) | Compliance | Conservative risk classification; legal/DPO validation |
| Benefit overstatement | Credibility | Conservative estimates, proof via SPC and back-testing |

## 9. Deliverables

The documents in this `documentation/work/` folder, the six GitHub Agents in
`.github/agents/`, the pilot environment, and the executive deck & live demo.
