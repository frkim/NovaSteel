# NovaSteel Governance, BI & Observability Runbook (Phase 7)

Operational runbook for the platform's governance, business-intelligence and observability
hardening. Every item maps to a constitutional principle and, where code/infra exists, to the
file that implements it. Nothing here actuates plant equipment — the platform is
decision-support only (Constitution I).

## 1. End-to-end lineage — EU-resident (Constitution II + III)
- **What**: sensor → Bronze → Silver → Gold feature → model prediction → recommendation →
  human decision → report, captured as an immutable, queryable lineage graph.
- **Residency constraint**: an **account-backed** Microsoft Purview Data Map
  (`Microsoft.Purview/accounts`) **cannot be provisioned in this tenant**, verified live:
  - West Europe → rejected (`39002`): not in the tenant's allowed Purview *service* locations.
  - Sweden Central (an allowed EU service location) → rejected (`21010`): the **"MCAPSGov Deny
    Policies"** management-group assignment denies Purview's auto-created managed resources
    (managed storage / Event Hub). This is a corporate governance guardrail above the subscription
    and is not modifiable from here.
  Deploying it therefore isn't possible; a US region would also violate Principle III. The
  `purview.bicep` module + `register_purview_sources.py` remain for tenants without these blocks.
- **Microsoft Purview (unified SaaS, purview.microsoft.com)** — the tenant-managed experience that
  does **not** create per-subscription managed resources — is the only Purview path here; enabling
  it is a **tenant-admin portal** action (M365 governance), not an ARM/API deploy.
- **EU-resident lineage delivered instead** (all within the Sweden Central / West Europe footprint):
  1. **Fabric OneLake data hub / catalog** — item-to-item lineage across the workspace
     (Eventhouse → shortcut → Bronze → Silver → Gold → semantic model) is captured natively and
     stays EU-resident, with no managed resources and no policy conflict.
  2. **Immutable audit trail** in code (`libs/novasteel_core/novasteel_core/audit.py`): every
     prediction/recommendation/decision carries inputs, model version, reviewer, timestamp and
     rationale (Constitution II), append-only.
  3. Fabric **sensitivity labels + endorsement** for classification (portal/tenant-configured).
- Tag `gold_kpi_synthetic` with the **Synthetic** classification so provenance is queryable
  wherever data lands (Constitution IX).

## 2. Role-based access & per-site isolation (Constitution VII)
- **Personas → least-privilege roles** via Microsoft Entra ID: Operator, Maintenance, Energy,
  Quality, ExecutiveEsg, ComplianceDpo (`ReviewerRole` in `novasteel_core.models`).
- **Per-site isolation**: data and recommendations are scoped by `site` (LU/DE/BE/ES). Models
  never mix sites — proven by `test_per_site_isolation` (P3 and KPI baseline tests) and enforced
  in every workload by filtering on `site`.
- **Runbook**:
  1. Create one Entra security group per persona per site (e.g. `ns-quality-DE`).
  2. Grant Fabric workspace/item roles and Power BI RLS roles to those groups only.
  3. Apply row-level security on the Gold marts keyed on `site`.
- **RBAC infra**: `infrastructure/modules/rbac.bicep`, `identity.bicep`.

## 3. Key management — BYOK/CMK (Constitution III)
- **Infra**: `infrastructure/modules/keyvault.bicep` (customer-managed keys). Data stores
  (ADLS/OneLake, SQL audit store) use CMK; keys never leave the EU tenant.
- **Runbook**: rotate keys per policy; verify Key Vault soft-delete + purge protection are on;
  monitor expiry (see the `azure-compliance` Key Vault expiration check).

## 4. Threat protection — Microsoft Defender for Cloud
- **Infra**: `infrastructure/modules/defender.bicep`.
- **Runbook**: keep Defender plans enabled for Storage, KeyVault, Containers; triage findings via
  the `azure-diagnostics` workflow. Remediate before pilot go-live.

## 5. Executive BI — Power BI Direct Lake (Constitution VI/VII)
- **Datasets**: Direct Lake semantic model over the Gold **real** marts only
  (`gold_kpi_real`, `gold_furnace_features`, `p1_predictions`, `p2_energy_plans`,
  `p3_quality_predictions`). Synthetic marts are excluded from executive reporting.
- **Dashboards**:
  - **Executive/ESG**: energy/ton, CO2/ton, cost/ton and high-grade yield vs the **frozen KPI
    baseline** (§6), with EU-ETS emissions roll-up.
  - **Engineering**: P1 RUL predictions & lead-time, P3 SPC control charts.
  - **Operations**: P2 energy plans awaiting approval; recommendation review queue.
- **RLS**: every report enforces per-site row-level security (§2).

## 6. KPI baseline (frozen, normalized) — SC baseline
- **Code**: `platform/kpi/kpi_baseline.py` (+ `kpi_notebook.py`, tests in `platform/kpi/tests`).
- **Definition**: trailing-12-month, per-ton-normalized baseline per site, **frozen** with its
  window and as-of date so improvement is always measured against a stable reference.
- **Runbook**: run `compute_frozen_baseline(spark, as_of)` once per baseline period; persist to
  `gold_kpi_baseline`; point Power BI KPI cards at it. Improvement % via
  `improvement_vs_baseline`. Targets: P2 −14% energy / −22% CO2 (SC-001/002), P3 +8% yield
  (SC-004), P1 ≥21-day RUL lead time (SC-003).
- **EU-ETS report**: `platform/governance/eu_ets.py::compute_ets_report` — verified annual tCO2
  per installation; only Real+verified records count, synthetic excluded (Constitution IX).

## 6b. Power BI Direct Lake (build spec)
- **Spec**: `platform/bi/README.md` — Direct Lake semantic model over the Gold real marts, core
  DAX measures, the three dashboards (Exec/ESG, Engineering, Operations) and per-site RLS roles.

## 6c. ML uplift (Fabric Data Science, MLflow)
- **P1**: `workloads/p1_predictive_maintenance/train_rul.py` — RUL regressor trained on Gold
  furnace features, logged/registered to MLflow (uplift over the physics-linear estimator).
- **P3**: `workloads/p3_quality/train_quality.py` — high-grade classifier on Gold quality features.
- Both are decision-support; models promote to Production only after human review of logged metrics.

## 7. GDPR erasure runbook (Constitution II)
- **Principle**: audit records are **exempt** from erasure (legal/traceability); raw personal
  content (e.g., operator interview transcripts in P4) **is** erasable.
- **Code**: `platform/governance/gdpr.py::erase_subject` — removes raw personal content, retains
  derived/de-identified content, and appends an append-only erasure audit (never deletes history).
  P4 capture (`workloads/p4_knowledge_capture/capture.py`) separates the erasable raw transcript
  from the de-identified `KnowledgeItem` at ingestion.
- **Runbook**:
  1. Locate personal data via Purview classification search.
  2. Call `erase_subject(subject_id, store, audit_log)` — raw personal content erased, derived
     knowledge + audit trail retained.
  3. The erasure itself is an audit entry (append-only) — never delete audit history.

## 8. Observability — drift & SLO alerts (Constitution VI)
- **Infra**: `infrastructure/modules/monitoring.bicep` (Log Analytics + App Insights) and
  `infrastructure/modules/monitoring-alerts.bicep` (action group + scheduled-query rules),
  wired in `resources.bicep` (`deployAlerts`, `alertEmail`).
- **Alerts**:
  - **Freshness/SLO**: no simulator telemetry within the SLO window ⇒ ingestion stalled.
  - **Model drift**: sustained drop in mean P1 prediction confidence ⇒ review model/features.
- **Runbook**: set `alertEmail`; route the action group to the on-call rota; on drift, freeze the
  model version and open a human review (predictions remain decision-support and lapse safely if
  unactioned — Constitution I).

## 9. EU data residency (Constitution III)
- All resources in EU regions (Sweden Central / West Europe / Germany West Central); IoT Hub is
  pinned to an EU region that supports it via `iotHubLocation`. Enforced as policy-as-code in
  `infrastructure/modules/policy.bicep` (allowed-locations). Zero egress.

## 10. Managed-identity auth posture (least standing secrets)
- Service-to-service auth uses **managed identity + RBAC** rather than keys/connection strings
  wherever supported:
  - Functions runtime storage: identity-based `AzureWebJobsStorage__*` + Storage Blob/Queue/Table
    Data role assignments (`infrastructure/modules/functions.bicep`).
  - App code (Foundry chat/embeddings, Fabric capacity control, Content Safety) uses
    `DefaultAzureCredential` (`workloads/.../foundry_client.py`, `content_safety.py`,
    `Services/FabricCapacityService.cs`).
  - Data-plane RBAC grants in `infrastructure/modules/rbac.bicep` (Storage/KeyVault/OpenAI/ACR).
  - CI/CD uses GitHub OIDC federation (no stored cloud keys).
- **Documented residual key usage** (no MI option): the Azure Files content share on Elastic
  Premium Functions, the Container Apps built-in Log Analytics `sharedKey`, and the IoT Hub
  **device** connection string (devices are not Entra principals) — the last is held in Key Vault.

## 11. Automated deployment (no manual portal steps, where possible)
Everything below is deployable via IaC / REST / job triggers with a suitably-privileged identity
(managed identity or `az login`); no keys.

| Task | Command | Live status |
|---|---|---|
| Azure Monitor alerts | `az deployment group create -g rg-novasteel-dev --template-file infrastructure/modules/monitoring-alerts.bicep --parameters logAnalyticsId=<id> alertEmail=<you>` | ✅ Deployed (`ag-novasteel-dev` + freshness + drift rules) |
| Train ML models (P1 RUL, P3 quality) | `python platform/scripts/train_models_live.py` (needs ≥F4) | ✅ Trained + MLflow-registered (`novasteel-p1-rul` MAE 0.23d, `novasteel-p3-quality` F1 1.0) |
| Entra RBAC groups + Fabric roles | `python platform/scripts/provision_entra_rbac.py --apply` | ✅ Deployed (24 `ns-<persona>-<site>` groups + 24 Fabric workspace role bindings) |
| Purview source registration + scan | `python platform/scripts/register_purview_sources.py --apply` | ⛔ **Not possible in this tenant.** Account-backed Purview is blocked: West Europe residency-rejected (`39002`); Sweden Central denied (`21010`) by the management-group **MCAPSGov Deny Policies** on Purview managed resources. Use Fabric-native lineage (§1) / unified Purview SaaS (tenant-admin portal). |
| Power BI Direct Lake semantic model + RLS | `python platform/scripts/deploy_powerbi_model.py --apply` (def: `platform/bi/semantic_model/`) | ✅ Deployed (Direct Lake model "NovaSteel" + per-site RLS roles) |
| Scheduled batch (bump→run→pause) | `.github/workflows/scheduled-batch.yml` (Azure OIDC) | ⚙️ Manual/cron-ready |

**Irreducibly manual** (business input, not automatable): alert recipients, *who* belongs to each
`ns-<persona>-<site>` group, the one-time Fabric→Purview tenant setting, real labelled data for
production model quality, and final Power BI report *visual* design.

---
### Test
```
python -m pytest platform/kpi/tests -q
az bicep build --file infrastructure/modules/monitoring-alerts.bicep --stdout > $null
```
