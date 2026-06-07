# 03 — Data & AI Design

**Project Ignition** — the three AI workloads, their data, models, metrics and
Responsible AI controls.

> All accuracy figures below are **targets** with the evaluation method that
> proves them — not guarantees. Demo uses **synthetic / anonymised** data so no
> real plant or personal data is exposed.

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
| **Serving** | Batch retrain in Azure ML; **edge inference** for low-latency, connectivity-resilient alerts |
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

**Goal (O4 enabler):** preserve retiring operators' expertise and raise
high-grade yield by spreading best-known methods.

| Aspect | Design |
| ------ | ------ |
| **Pattern** | Interview assistant (Azure OpenAI) → structured procedure library → **RAG** via Azure AI Search |
| **Data** | Operator interviews, SOPs, shift logs (anonymised); grounded retrieval only |
| **Model** | Azure OpenAI chat model with retrieval; citations to source procedures |
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

- **Azure Machine Learning** registry + pipelines; **Git + Azure DevOps/GitHub
  Actions** for CI/CD of models and infra.
- **Monitoring:** data drift, model quality, and alerting in Azure Monitor;
  scheduled retraining with approval gates.
- **Reproducibility:** versioned datasets (OneLake), environments, and lineage
  in **Microsoft Purview**.

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
