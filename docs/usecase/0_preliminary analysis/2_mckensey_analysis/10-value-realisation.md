# 10. 📈 Value Realisation

*Audience: CFO (19), COO (1), Head of Energy Management (7), Head of Sustainability /
ESG (11), Strategy Director (20).*

> ⚠️ **All figures are illustrative demo estimates** to frame the business case —
> **not a quote**. Confirm with NovaSteel actuals, an Azure Pricing Calculator run
> and an Azure assessment before any commitment. Currency: **EUR**. This expands
> [`../../First_Proposal/05-cost-estimate.md`](../../First_Proposal/05-cost-estimate.md).

---

## 10.1 Financial impact model

### Assumptions (challenge these first)

| # | Assumption | Value (illustrative) |
|---|-----------|----------------------|
| A1 | Annual production — in-scope site (at scale) | ~**1.0 Mt/year** |
| A1b | Annual production — pilot line | ~**0.3 Mt/year** |
| A2 | Production cost | ~**€500/t** |
| A3 | Energy share of cost | **35%** → ~€175/t |
| A4 | Energy reduction (O1) | **−14%** of energy cost |
| A5 | CO₂ price (EU ETS) | ~**€70/tCO₂** |
| A6 | CO₂ reduction (O2) | **−22%** |
| A7 | Furnace failure cost | ~**€8M** per event |
| A8 | Failure frequency (pilot line) | ~1 every **2–3 years** |
| A9 | High-grade yield uplift (O4) | **+8%** on premium tonnage |
| A10 | EU regions | Sweden Central / West Europe / Germany West Central |

### Cost — Azure run (annual, pilot)

| Category | Representative services | Indicative €/yr |
|----------|------------------------|-----------------|
| Data platform | Microsoft Fabric capacity, OneLake/ADLS | €120k–€220k |
| Ingestion | Azure IoT Hub, Event Hubs (cloud-direct) | €40k–€80k |
| AI/ML | Fabric Data Science compute, monitoring | €90k–€180k |
| GenAI | Microsoft Foundry — Azure OpenAI tokens, Foundry IQ | €30k–€90k |
| Apps & experience | Functions/Container Apps, Power BI | €20k–€50k |
| Security & governance | Defender, Purview, Key Vault, Monitor | €30k–€60k |
| Networking | VNet, private endpoints, egress | €10k–€30k |
| **Indicative annual run total** | | **≈ €340k–€710k** |

### Cost — Implementation (one-off)

| Item | Indicative € |
|------|--------------|
| Foundation (landing zone, data platform, ingestion) | €150k–€300k |
| Three AI workloads (build, MLOps, Responsible AI) | €250k–€500k |
| Experience, integration, enablement | €100k–€200k |
| Compliance (DPIA, AI Act file) & change mgmt | €60k–€120k |
| **Indicative implementation total** | **≈ €560k–€1.12M** |

### Benefit model (annual, at scale across the ~1.0 Mt site)

> The pilot proves the **percentages** on the ~0.3 Mt line first (≈⅓ of the figures);
> values below are the **at-scale** run-rate once rolled out.

| Lever | Calculation (illustrative) | Indicative €/yr |
|-------|----------------------------|-----------------|
| Energy savings (O1) | 1.0Mt × €175/t × 14% | **~€24.5M** |
| Avoided ETS penalty (O2) | tonnage × tCO₂/t × €70 × 22% | **€ several M** (site-specific) |
| Avoided furnace failure (O3) | €8M × (1 / 2.5 yr) | **~€3.2M/yr** expected |
| High-grade yield (O4) | premium tonnage × margin × 8% | **€ several M** |

> The dominant driver is **O1 energy**, because energy is 35% of a large cost base.
> Even under conservative haircuts, **energy + avoided-failure** alone dominate the
> cost base.

## 10.2 Energy savings analysis (−14% energy/ton)

- Proven by **A/B vs. the historical baseline**: €/ton and kWh/ton with and without
  optimisation, and **% production shifted** to low-price windows.
- Lever is **structural** (it attacks 35% of cost), so it compounds every year.
- Sensitivity: even at **<14%**, the benefit "shrinks but stays large"; the pilot
  proves the **real %** before scale.

## 10.3 CO₂ reduction impact (−22%, ETS avoidance)

- The **same** dispatch decision that saves energy also reduces carbon by scheduling
  flexible load in **lower-carbon** windows.
- Translates into **avoided ETS penalty** cost and a **verifiable** sustainability
  story (auditable lineage, read-only emissions reporting).
- Strengthens posture for **CBAM** and customer ESG requirements.

## 10.4 Production yield improvement (+8% high-grade yield)

- Credited only when **SPC / Cp/Cpk** proves **reduced variability** — not a shifted
  mean — with full traceability (heat/charge → coil).
- Converts existing premium tonnage from downgrade/scrap into saleable high-grade
  automotive steel.
- Treated conservatively: **prove via SPC before crediting**.

## 10.5 Return & KPI dashboard

### Return (illustrative)

| Metric | Conservative | Base | Optimistic |
|--------|--------------|------|------------|
| Year-1 net benefit | clearly positive | strongly positive | very strong |
| **Payback** | **< 12 months** | < 9 months | < 6 months |
| 3-yr ROI | high multiple | higher | highest |

> Because annual benefits (energy alone ~€24.5M illustrative) **vastly exceed** build
> (~€0.6–1.1M) plus run (~€0.3–0.7M/yr), **payback is well under a year** even after
> large conservative discounts. NPV/IRR to be computed with NovaSteel's discount rate.

### Sensitivity (what could change the answer)

| Driver | If lower than assumed | Mitigation |
|--------|----------------------|------------|
| Energy saving < 14% | Benefit shrinks but still large | Pilot proves real % before scale |
| Failure frequency lower | O3 benefit smaller | Treat O3 as **upside**, not base |
| Yield uplift < 8% | O4 smaller | Prove via SPC before crediting |
| Azure cost higher | Run cost up | Reservations, right-sizing, FinOps |

### KPI dashboard definition

| Objective | Target | Measurement |
|-----------|--------|-------------|
| Energy efficiency | −14% per ton | €/ton, kWh/ton vs. baseline A/B |
| CO₂ reduction | −22% per ton | tCO₂/ton, ETS reporting, carbon-aware scheduling % |
| Furnace reliability | 21-day warning | Alert lead-time distribution, averted €8M events |
| Quality consistency | +8% high-grade yield | SPC Cp/Cpk improvement, grade adherence |
| Knowledge capture | adoption / coverage | SME eval pass rate, yield correlation over time |
| Governance compliance | 100% traceability | Purview lineage, audit-log completeness, AI Act dossier |

> **Cost optimisation levers:** Fabric capacity right-sizing, **reservations /
> savings plans**, autoscale, dev/test shutdown, batch scheduling of training.

---

*Continue to → [11. Operating Model](11-operating-model.md)*
