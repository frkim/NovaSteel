# 03 — Data & AI Design

**Project Ignition** — the three AI workloads, their data, models, metrics and
Responsible AI controls.

> All accuracy figures below are **targets** with the evaluation method that
> proves them — not guarantees. Demo uses **synthetic / anonymised** data so no
> real plant or personal data is exposed.

**Primary target roles:** Head of Maintenance / Reliability Engineering Lead (5),
Head of Quality (6), Head of Energy Management (7),
Head of Data Science / ML Lead (13), AI Architect / Digital Twin Architect (14),
Shift Supervisors / Senior Operators (18).

---

## 1. Workload A — Furnace-lining degradation (predictive maintenance)

**Goal (O3):** alert **≥ 21 days** before a refractory lining failure
(~€8M per averted event).

| Aspect | Design |
| ------ | ------ |
| **Problem framing** | Remaining-Useful-Life (RUL) regression + binary "failure within 21 days" alert, with uncertainty bounds |
| **Data sources** | Thermal signatures (pyrometers/IR), vibration, off-gas chemistry, campaign age, heat history, refractory batch |
| **Features** | Physics-informed: heat-flux estimates, wear-rate proxies, thermal gradients; plus rolling statistics & spectral features |
| **Model** | Hybrid: first-principles heat-transfer features feeding gradient-boosted / temporal models; survival analysis for time-to-event |
| **Serving** | Batch retrain in **Fabric Data Science**; **Fabric ML endpoint** scored on live Real-Time Intelligence (KQL) features for low-latency cloud alerting |
| **Metrics** | Alert **precision/recall at 21-day horizon**, lead-time MAE weighted toward early warning, false-alarm rate |
| **Proof** | Back-test on historical failures; track lead-time distribution |

## 2. Workload B — Energy-dispatch optimization

**Goal (O1/O2):** **−14%** energy/ton and **−22%** CO₂ by scheduling
energy-intensive steps around electricity spot prices and grid carbon.

| Aspect | Design |
| ------ | ------ |
| **Problem framing** | Constrained scheduling / optimization over a rolling horizon |
| **Inputs** | Process energy demand, production constraints & deadlines, day-ahead **spot prices**, **grid carbon intensity** |
| **Approach** | Forecast demand (ML) → optimize schedule (MILP / heuristic) → recommend, operator confirms |
| **Serving** | Azure Functions / Container Apps; recommendations to dashboards & operators |
| **Metrics** | €/ton and kWh/ton vs. baseline; tCO₂/ton; % production shifted to low-price/low-carbon windows |
| **Proof** | A/B vs. historical baseline; counterfactual cost & carbon |

## 3. Workload C — GenAI knowledge capture

**Goal (O5; enables O4):** preserve retiring operators' expertise and raise
high-grade yield by spreading best-known methods.

| Aspect | Design |
| ------ | ------ |
| **Pattern** | Interview assistant (Azure OpenAI) → structured procedure library → **RAG** via Foundry IQ |
| **Data** | Operator interviews, SOPs, shift logs (anonymised); grounded retrieval only |
| **Model** | Azure OpenAI / Foundry model with retrieval; citations to source procedures |
| **Serving** | Teams + Copilot experience for operators and metallurgists |
| **Metrics** | Groundedness, relevance, answer-with-citation rate, human review pass rate, adoption/usage |
| **Proof** | Human SME evaluation set; track yield correlation over time |

## 4. Quality linkage (with the Quality Engineer agent)

The platform improves **O4 — +8% high-grade yield** not by automating decisions
but by tightening the process:

- Surface **process-parameter recommendations** (tap temperature, chemistry,
  cooling/rolling) from Gold-layer features.
- Use **SPC** and capability indices (**Cp/Cpk**) to show reduced variability,
  not just a shifted mean.
- Maintain **full traceability** (heat/charge → coil) and digital quality
  certificates aligned to customer expectations (e.g. IATF 16949, EN 10204 3.1).
- **AI advises, metallurgists decide.**

## 5. MLOps

- **Microsoft Fabric Data Science** — MLflow experiments, model registry and
  endpoints inside Fabric; **Git + GitHub Actions / Azure DevOps** for CI/CD of
  promotion logic and infra.
- **Monitoring:** data drift, model quality, and alerting via **Azure Monitor**;
  scheduled retraining with approval gates.
- **Reproducibility:** versioned datasets (OneLake), pinned Spark environments,
  and lineage in **Microsoft Purview**.

## 6. Responsible AI controls

| Principle | Control |
| --------- | ------- |
| Reliability & safety | Human-in-the-loop for any safety/emissions/personnel action; uncertainty shown with every prediction |
| Privacy & security | EU residency; anonymised/synthetic data for demo; lawful basis + DPIA for interviews |
| Transparency | Model cards, data sheets, RAG citations; explainability on RUL drivers |
| Fairness & robustness | Bias/robustness checks on knowledge assistant; back-testing on diverse failure modes |
| Accountability | Named owners per workload; audit logs; AI Act risk file ([06](06-security-compliance.md)) |

## 7. Demo data plan

- Generate **synthetic furnace telemetry** with injected degradation patterns to
  demonstrate the 21-day alert live.
- Use **public/illustrative spot-price & carbon series** for energy optimization.
- Use a **synthetic SOP corpus** for the knowledge assistant.
- Clearly label all demo data as synthetic.

## 8. Agentic behaviour & autonomy

Workload B is implemented as an **autonomous optimization agent**, not a static
report. It runs a closed **sense → reason → act (recommend) → learn** loop on a
rolling horizon:

1. **Sense** — pull live process demand, production constraints, day-ahead spot
   prices and grid-carbon intensity.
2. **Reason** — forecast demand (ML), then solve the constrained schedule
   (MILP / heuristic) to minimise cost and carbon within deadlines.
3. **Act (with a human gate)** — emit a ranked schedule recommendation; an
   operator **confirms** before anything changes. *Autonomy is bounded:* the
   agent never writes to control systems directly.
4. **Learn** — outcomes feed back as counterfactual A/B evidence to improve the
   next horizon.

A lightweight **furnace-triage agent** complements it: when the RUL model raises
a 21-day alert, the agent assembles the drivers, suggested inspection window and
the relevant procedures (via the knowledge assistant) into one actionable card.

**Multi-agent coordination (delivery side).** The solution is *authored and
maintained* by a coordinated team of nine specialist GitHub Agents under an
`orchestrator` that decomposes a request, hands off to the right specialist, and
integrates the results — a documented **handoff / reflection** pattern. See
[09 — GitHub Agents guide](09-github-agents.md).

## 9. Model selection & deployment rationale

| Workload | Chosen approach | Why this choice | Deployment |
| -------- | --------------- | --------------- | ---------- |
| A — RUL | Physics-informed features + gradient-boosted / survival models | Interpretable, data-efficient, gives uncertainty + lead-time | Batch retrain in **Fabric Data Science**; **Fabric ML endpoint** on live RTI features for low-latency cloud alerts |
| B — Dispatch | Demand forecast (ML) + MILP/heuristic optimiser | Hard constraints & deadlines need an optimiser, not just a predictor | Azure Functions / Container Apps, event-triggered |
| C — Assistant | **GPT-5** on Microsoft Foundry + RAG via Foundry IQ | Strong reasoning with grounded, cited answers; EU-resident | Foundry endpoint; `text-embedding-3-large` for vectors |

> Models are versioned in the **Fabric Data Science** model registry (MLflow),
> promoted through gated CI/CD, and monitored for drift and quality (see
> [02 — §4b Monitoring](02-solution-architecture.md) and §5 MLOps above).
