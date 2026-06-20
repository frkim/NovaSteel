# 05 — Cost Estimate & ROI

**Project Ignition** — illustrative TCO, benefits and return for CFO (19),
Head of Energy Management (7), and Head of Sustainability / ESG (11).

> ⚠️ **All figures are illustrative demo estimates** to frame the business case.
> They are **not a quote** and require a detailed Azure assessment (Azure Pricing
> Calculator + an Azure Migrate/assessment) before any commitment. Currency: EUR.

---

## 1. Assumptions (challenge these first)

| # | Assumption | Value (illustrative) |
| - | ---------- | -------------------- |
| A1 | Annual production — in-scope site (at scale) | ~1.0 Mt/year |
| A1b | Annual production — pilot line (Phase 2) | ~0.3 Mt/year |
| A2 | Production cost | ~€500 /t |
| A3 | Energy share of cost | 35% → ~€175 /t |
| A4 | Energy reduction (O1) | −14% of energy cost |
| A5 | CO₂ price (EU ETS) | ~€70 /tCO₂ |
| A6 | CO₂ reduction (O2) | −22% |
| A7 | Furnace failure cost | ~€8M per event |
| A8 | Failure frequency (pilot line) | ~1 every 2–3 years |
| A9 | High-grade yield uplift (O4) | +8% on premium tonnage |
| A10 | EU regions, consumption pricing | Sweden Central / West Europe / Germany West Central |

> Replace each value with NovaSteel's actuals during the design workshop.

## 2. Azure run cost (annual, pilot) — illustrative

| Category | Representative services | Indicative €/yr |
| -------- | ----------------------- | --------------- |
| Data platform | Microsoft Fabric capacity, OneLake/ADLS | €120k–€220k |
| Ingestion & edge | IoT Hub/Operations, Event Hubs, Arc | €40k–€80k |
| AI/ML | Azure ML compute (train/serve), monitoring | €90k–€180k |
| GenAI | Azure OpenAI tokens, AI Search | €30k–€90k |
| Apps & experience | Functions/Container Apps, Power BI | €20k–€50k |
| Security & governance | Defender, Purview, Key Vault, Monitor | €30k–€60k |
| Networking | VNet, private endpoints, egress | €10k–€30k |
| **Indicative annual run total** | | **≈ €340k–€710k** |

> Optimization levers: Fabric capacity right-sizing, **reservations / savings
> plans**, autoscale, dev/test shutdown, batch scheduling of training.

## 3. Implementation (one-off) — illustrative

| Item | Indicative € |
| ---- | ------------ |
| Foundation (landing zone, data platform, edge) | €150k–€300k |
| Three AI workloads (build, MLOps, Responsible AI) | €250k–€500k |
| Experience, integration, enablement | €100k–€200k |
| Compliance (DPIA, AI Act file) & change mgmt | €60k–€120k |
| **Indicative implementation total** | **≈ €560k–€1.12M** |

## 4. Benefit model (annual, at scale across the ~1.0 Mt in-scope site) — illustrative

> **Pilot vs scale.** The pilot proves the **percentages** on the ~0.3 Mt pilot
> line first (≈⅓ of the figures below); the values here are the **at-scale**
> annual run-rate once rolled out across the in-scope site.

| Lever | Calculation (illustrative) | Indicative €/yr |
| ----- | -------------------------- | --------------- |
| Energy savings (O1) | 1.0Mt × €175/t × 14% | **~€24.5M** |
| Avoided ETS penalty (O2) | tonnage × tCO₂/t × €70 × 22% | **€ several M** (site-specific) |
| Avoided furnace failure (O3) | €8M × (1 / 2.5 yr) | **~€3.2M/yr expected** |
| High-grade yield (O4) | premium tonnage × margin × 8% | **€ several M** |

> Even under conservative haircuts, the **energy and avoided-failure** levers
> alone dominate the cost base. The dominant driver is **O1 energy**, because
> energy is 35% of a large cost base.

## 5. Return (illustrative)

| Metric | Conservative | Base | Optimistic |
| ------ | ------------ | ---- | ---------- |
| Year-1 net benefit | clearly positive | strongly positive | very strong |
| **Payback** | < 12 months | < 9 months | < 6 months |
| 3-yr ROI | high multiple | higher | highest |

Because annual benefits (energy alone ~€24.5M illustrative) vastly exceed
build (~€0.6–1.1M) plus run (~€0.3–0.7M/yr), **payback is well under a year**
even after large conservative discounts. NPV/IRR should be computed with
NovaSteel's discount rate during the workshop.

## 6. Sensitivity (what could change the answer)

| Driver | If lower than assumed | Mitigation |
| ------ | --------------------- | ---------- |
| Energy saving < 14% | Benefit shrinks but still large | Pilot proves real % before scale |
| Failure frequency lower | O3 benefit smaller | Treat O3 as upside, not base |
| Yield uplift < 8% | O4 smaller | Prove via SPC before crediting |
| Azure cost higher | Run cost up | Reservations, right-sizing, FinOps |

## 7. Role summary (one slide)

- **Spend:** ~€0.6–1.1M to build, ~€0.3–0.7M/yr to run (illustrative).
- **Return:** energy −14% and avoided €8M failures drive **sub-12-month payback**.
- **De-risked:** time-boxed pilot proves the percentages on real data before any
  multi-site scale commitment.
- **Conditions:** figures are illustrative; confirm with a detailed Azure
  assessment and NovaSteel actuals.
