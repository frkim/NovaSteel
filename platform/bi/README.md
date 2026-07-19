# NovaSteel Power BI — Direct Lake semantic model & dashboards (Phase 7, Constitution VI/VII)

Design spec for the executive/engineering/operations reporting layer. Built as a **Direct Lake**
semantic model over the Gold **real** marts only (synthetic marts are excluded — Constitution IX),
with **per-site row-level security** (Constitution VII). This is a build spec (Power BI authoring
is portal/Tabular-Editor work); the underlying Gold tables it binds to are already produced by the
medallion + pillar notebooks.

## Source tables (Gold, OneLake Direct Lake)
| Table | Grain | Key columns |
|---|---|---|
| `gold_kpi_real` | site × metric | site, metric, avg_value, good_ratio, stale_count |
| `gold_kpi_baseline` | site | site, energy_mwh_per_ton, co2_kg_per_ton, cost_eur_per_ton, high_grade_yield (frozen) |
| `gold_furnace_features` | asset × window | AssetId, Site, ThermocoupleTemp, HeatFlux, Vibration |
| `p1_predictions` | prediction | prediction_id, site, kind, confidence, status, payload_json |
| `p2_energy_plans` | plan | energy_plan_id, site, status, expected_energy_per_ton, baseline_energy_per_ton, expected_co2_per_ton |
| `p3_quality_predictions` | heat | prediction_id, heat_id, site, kind, confidence, status |
| `p3_spc_drift` | drift | prediction_id, heat_id, site, payload_json |
| `gold_market_signals` | site × ts | market, timestamp, spot_price_eur_mwh, grid_carbon_grams_per_kwh |

## Core measures (DAX sketch)
- **Energy saving %** = `DIVIDE([Baseline Energy/ton] - [Expected Energy/ton], [Baseline Energy/ton])`
- **CO2 saving %** = `DIVIDE([Baseline CO2/ton] - [Expected CO2/ton], [Baseline CO2/ton])`
- **High-grade yield** = `DIVIDE(COUNTROWS(FILTER(p3, [predictedHighGrade])), COUNTROWS(p3))`
- **Open recommendations** = `CALCULATE(COUNTROWS(...), status = "Proposed")`
- **KPI vs frozen baseline** = current per-ton ÷ `gold_kpi_baseline` (the stable reference).

## Dashboards
1. **Executive / ESG** — energy/ton, CO2/ton, cost/ton, high-grade yield vs the **frozen KPI
   baseline**; EU-ETS verified tCO2 roll-up (from `platform/governance/eu_ets.py`); target gauges
   SC-001 (−14%), SC-002 (−22%), SC-004 (+8%).
2. **Engineering** — P1 RUL lead-time distribution & predictions; P3 SPC control charts (from
   `p3_spc_drift` + `gold_quality_features`).
3. **Operations** — P2 energy plans awaiting approval; the recommendation review queue (Proposed
   items across pillars); telemetry freshness.

## Row-level security (per-site isolation — Constitution VII)
- Define one RLS role per site (`RLS_LU`, `RLS_DE`, `RLS_BE`, `RLS_ES`) with filter
  `[site] = "<SITE>"` on every table.
- Map the per-persona/per-site Entra security groups (§2 of the governance runbook) to these roles.
- Cross-site bleed is impossible: no user sees another site's rows.

## Build steps (portal)
1. Create a Direct Lake semantic model on the `onelake_novasteel` lakehouse; add the tables above.
2. Add the measures; mark `gold_kpi_baseline` as the reference table (do not aggregate).
3. Define the RLS roles + map Entra groups.
4. Build the three report pages; publish to a workspace app with per-site audiences.
5. Point KPI cards at the measures vs the frozen baseline.

## Deployed status (live)
> Remaining manual/portal steps for BI are consolidated in [`MANUAL_STEPS.md`](../../MANUAL_STEPS.md) (§3 labels, §4 report visuals).

- ✅ **Semantic model** "NovaSteel" (Direct Lake) deployed via `deploy_powerbi_model.py`
  (`platform/bi/semantic_model/`): `p2_energy_plans` + `p3_quality_predictions` tables, DAX
  measures, and per-site RLS roles `RLS_LU/DE/BE/ES`.
- ✅ **Frozen KPI baseline** `gold_kpi_baseline` materialized (4 sites) — the executive reference.
- ✅ **Report scaffold** "NovaSteel Executive" deployed (`platform/bi/report/`), bound to the model
  with an "Executive / ESG" page.
- ⚙️ **Report visuals** — authoring the cards/charts on the pages is **Power BI Desktop / portal**
  design work (open the deployed report, drag the measures). The model + RLS + reference table are
  all in place.
- ⚙️ **Sensitivity labels** — configuring the MIP label taxonomy and applying labels is a
  **tenant-admin** action; endorsement (Promote/Certify) likewise needs authorized-certifier setup.
