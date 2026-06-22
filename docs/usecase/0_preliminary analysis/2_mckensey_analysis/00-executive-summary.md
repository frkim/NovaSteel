# 0. 🧭 Executive Summary

**Project Ignition — NovaSteel AI-Powered Steel Production Optimisation Platform**

*Audience: COO (1), Head of Manufacturing / VP Operations (2), CFO (19), Head of
Sustainability / ESG (11), Strategy Director (20).*

---

## 0.1 Industrial context

NovaSteel is a Luxembourg-headquartered **integrated steel producer** operating
blast furnaces, basic-oxygen and electric-arc furnaces and rolling mills across
**Luxembourg, Germany, Belgium and Spain**. It serves demanding downstream
markets — notably **automotive** — that require consistent high-grade steel,
auditable quality certificates and a credible decarbonisation trajectory. The
company operates inside the EU regulatory perimeter: **GDPR**, the **EU AI Act**,
the **EU Emissions Trading System (ETS)** and sector-specific directives.

## 0.2 The client problem

Four structural forces are simultaneously eroding margin and resilience:

| Force | Why it hurts NovaSteel |
|-------|------------------------|
| **Energy intensity** | Energy is **~35% of production cost**, dispatched with **no real-time optimisation** against price or carbon. |
| **Carbon exposure** | CO₂ emissions carry rising **EU ETS** penalty risk and growing customer/ESG scrutiny. |
| **Catastrophic furnace failures** | Refractory-lining wear is **unpredictable**; a single failure costs **~€8M** per event. |
| **Quality variability** | Inconsistent high-grade steel jeopardises **automotive** contracts and yield. |
| **Knowledge erosion** | **Skilled operators are retiring** faster than their tacit expertise can be captured. |

These are not five separate problems — they share a single root cause: **plant data
exists but is not turned into timely, trustworthy decisions.**

## 0.3 The proposed solution

An **Azure AI production-optimisation platform** built on **Microsoft Fabric**
(data) and **Microsoft Foundry** (AI/agents), ingesting plant telemetry
**cloud-direct via Azure IoT Hub** (no plant-side edge runtime), and converting it
into **three decisions plus one safeguard**:

1. **Predict** furnace-lining degradation from thermal signatures using
   **physics-informed ML** → *21-day advance warning*.
2. **Optimise** energy-intensive steps around electricity **spot prices** and
   **grid carbon** with an autonomous-but-supervised dispatch agent → *lower
   energy & CO₂*.
3. **Capture** retiring operators' expertise with a **GenAI** assistant into a
   searchable, cited procedure library → *protect & spread best-known methods*.
4. **Tighten quality** with SPC-driven process recommendations (Cp/Cpk) →
   *higher high-grade yield* — **AI advises, metallurgists decide**.

The platform is **cloud-first, single-plane and EU-resident**: one governed data
copy (**OneLake** medallion lakehouse), one AI plane (**Foundry**), one ingestion
path (**IoT Hub + Event Hubs**), and one governance fabric (**Entra ID, Key Vault,
Azure Policy, Microsoft Purview, Defender, Azure Monitor**).

## 0.4 Expected value (targets)

| Outcome | Target | Illustrative annual value (at-scale ~1.0 Mt site) |
|---------|--------|---------------------------------------------------|
| ⚡ Energy per ton | **−14%** | **~€24.5M** (dominant lever) |
| 🌍 CO₂ emissions | **−22%** | **€ several M** ETS exposure avoided |
| 🔥 Furnace-lining failure warning | **≥ 21 days** | **~€3.2M/yr expected** avoided failures |
| ✅ High-grade yield | **+8%** | **€ several M** premium tonnage |
| 🧑‍🏭 Knowledge capture | Library live & adopted | Resilience; underpins yield |

**Spend (illustrative):** ~**€0.6–1.1M** to build, ~**€0.3–0.7M/yr** to run.
**Return:** because energy savings alone (~€24.5M illustrative) dwarf build + run
cost, **payback is well under 12 months** even after large conservative haircuts.

## 0.5 Recommendation & next steps

> **Recommendation:** Approve a **time-boxed pilot on one furnace line** to prove
> the 21-day warning, energy savings and yield uplift on **real data**, behind a
> compliant **DPIA / EU AI Act** baseline, with a **scale decision gate** at the
> end of the pilot.

**Immediate next steps (first ~8 weeks):**

1. **Mobilise (G0):** confirm scope, KPIs, baselines and the steering committee;
   start the **DPIA** and **EU AI Act** risk classification.
2. **Foundation (G1→G2):** deploy the landing zone, the Fabric/OneLake medallion
   lakehouse and cloud-direct IoT Hub ingestion; complete a historian data
   assessment.
3. **Pilot build (G2→G3):** deliver the three AI workloads on one line, dashboards
   and the operator experience; **back-test** the furnace alert on historical
   failures.
4. **Pilot review (G4):** measure against KPIs, refresh the TCO/ROI model, and
   take a **go / no-go** decision to scale across the four sites.

**Why now:** the levers compound (energy + carbon + reliability + quality + knowledge),
the technology is **GA and EU-resident**, and the pilot de-risks the investment
before any multi-site commitment.

---

*Continue to → [1. Industry Context & Strategic Drivers](01-industry-context.md)*
