# NovaSteel — Remaining manual / admin-gated steps (handoff)

Single source of truth for the work that is **not** autonomously automatable from the
subscription — each item is gated by a **tenant admin**, a **portal/design** action, an
**org-policy/preference**, or **real-system data**. Everything else is deployed and live
(pillars P1–P4, medallion, simulator + Personas page, Content Safety wiring, alerts, RBAC,
Power BI semantic model + KPI baseline + report scaffold, ML models trained/registered).

For each item: **why it's gated**, **who** can do it, and the **exact steps**.

---

## 1. CI/CD OIDC federation + enable the scheduled cron
- **Why gated**: the workflows (`.github/workflows/ci.yml`, `scheduled-batch.yml`) authenticate to
  Azure with **GitHub OIDC** (no keys). That needs an **App Registration + federated credential**
  and repo secrets — and per the user's preference we avoid creating App Registrations/PATs
  autonomously.
- **Who**: a directory admin (or the user) + GitHub repo admin.
- **Steps**:
  1. Create (or reuse) an Entra app + **federated credential** for the repo:
     `subject: repo:frkim/NovaSteel:ref:refs/heads/main` (and one per environment/branch as needed),
     `issuer: https://token.actions.githubusercontent.com`, `audience: api://AzureADTokenExchange`.
  2. Grant that identity the needed Azure roles (Contributor on `rg-novasteel-dev`, Fabric admin,
     Storage/OneLake data roles).
  3. Set repo secrets: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`
     (e.g. `gh secret set AZURE_CLIENT_ID -b <appId>`).
  4. Enable the cron: uncomment the `schedule:` block in `.github/workflows/scheduled-batch.yml`.
- **Status**: workflows written and valid; secrets + cron are the remaining manual steps.

## 2. Microsoft Purview
- **Why gated**: account-backed Purview **cannot be provisioned in this tenant** — West Europe is
  residency-rejected (`39002`) and Sweden Central is denied (`21010`) by the management-group
  **"MCAPSGov Deny Policies"** on Purview's managed resources. See governance README §1/§11.
- **Who**: a tenant / management-group admin.
- **Options**:
  - Enable **unified Microsoft Purview (purview.microsoft.com)** — tenant-managed, no
    per-subscription managed resources; pick an **EU Data Map region** (e.g. Sweden Central).
  - OR grant a **policy exemption** for the `managed-rg-pview-*` resource group against the
    MCAPS deny policy, then run `python platform/scripts/register_purview_sources.py --apply`.
- **EU-resident alternative already in place**: Fabric OneLake catalog lineage + the immutable
  audit trail (`novasteel_core.audit`).

## 3. Fabric endorsement + sensitivity labels
- **Why gated**: **Certify** needs authorized-certifier setup (tenant setting); **sensitivity
  labels** need the **MIP label taxonomy** configured at tenant level. Neither is deployable via
  the subscription.
- **Who**: Fabric/Power BI tenant admin + Microsoft Purview Information Protection admin.
- **Steps**:
  1. Configure the sensitivity-label taxonomy (add a **Synthetic** label) in Purview Information
     Protection; enable labels for Fabric.
  2. Apply the **Synthetic** label to `gold_kpi_synthetic` (Constitution IX).
  3. Endorse the semantic model / gold marts (**Promoted** or **Certified**).

## 4. Power BI report visuals
- **Why gated**: authoring cards/charts is **Power BI Desktop / portal** design work.
- **Who**: a BI developer.
- **Steps**: open the deployed **"NovaSteel Executive"** report (scaffold in `platform/bi/report/`,
  bound to the Direct Lake model), add visuals for the DAX measures (Energy/CO₂ saving %,
  High-grade yield, Open plans) vs `gold_kpi_baseline`, then build the Engineering + Operations
  pages. Model, RLS, measures and the frozen baseline are all deployed.

## 5. Alert on-call routing
- **Status**: alerts deployed and the action group emails `frkim@microsoft.com`.
- **Remaining**: route the action group to the real **on-call** channel (Teams/PagerDuty/webhook)
  and confirm severities. Update via `monitoring-alerts.bicep` `alertEmail` + action-group receivers.

## 6. Production-data integration (pilot readiness)
- **Why gated**: needs **real source systems** and **labelled data**.
- **Steps**:
  1. Wire `gold_energy_jobs` from **MES/ERP** and `actual_high_grade` from **lab QA**
     (today synthetic; Data Factory pipeline scaffold in `platform/ingestion/df_mes_erp_eam.json`).
  2. **Wire the registered MLflow models** (`novasteel-p1-rul`, `novasteel-p3-quality`) into P1/P3
     inference (they currently use the physics/rules estimators; models are registered in Fabric).
  3. Retrain on real labels (`platform/scripts/train_models_live.py`) and recompute the KPI
     baseline on real production.

## 7. VNet + Private Link (deferred)
- Intentionally deferred to keep simple dev access. See the network-hardening discussion; move to
  full Private Link + VPN/Bastion + App Gateway for the production/pilot environment.

---
### Already live (no action needed)
Pillars P1–P4 (tested + live-validated), medallion ingestion, simulator (+ Personas page,
Content Safety env, tariff/quality telemetry), Foundry explainers, Azure Monitor alerts, Entra
RBAC (24 groups + roles), Power BI semantic model + RLS + KPI baseline + report scaffold, ML
models trained/registered. Tests: Python 83 + .NET 23 green. Fabric F2 + Paused; EU-residency
policy enforced.
