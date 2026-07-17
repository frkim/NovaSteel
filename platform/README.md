# NovaSteel Platform — Ingestion & Medallion (Phase 2d)

Shared data-and-AI plane that feeds every pillar. These artifacts target the **live**
Azure platform deployed by `infrastructure/` (RG `rg-novasteel-dev`, Sweden Central;
IoT Hub in West Europe; Fabric capacity `fabnovasteedevox26fi`).

## Layout

| Path | Task | What it is |
| --- | --- | --- |
| `medallion/transforms.py` | T028–T030 core | Spark-free, **tested** Bronze→Silver→Gold transforms (provenance-preserving) |
| `medallion/data_quality.py` | T032 | Reusable data-quality gate (provenance present, no synthetic-in-real-KPI) |
| `medallion/tests/test_provenance_propagation.py` | **T026** | pytest gate — proves `origin/sourceId/site/quality` survive all layers and synthetic is excluded from real KPIs |
| `medallion/bronze_telemetry.py` | T028 | Fabric notebook: append-only Bronze landing + provenance quarantine |
| `medallion/silver_telemetry.py` | T029 | Fabric notebook: dedup, freshness/quality flags, partition by site |
| `medallion/gold_marts.py` | T030 | Fabric notebook: KPI marts (real vs synthetic) + furnace features |
| `rti/eventhouse.kql` | T027 | Eventhouse (KQL DB) schema, ingestion mapping, quarantine update policy, live features |
| `rti/eventstream-telemetry.json` | T027 | Eventstream topology: IoT Hub → Eventhouse + OneLake Bronze |
| `rti/activator-freshness.kql` | T033 | Activator rules: dropout / late-arrival / quality-degradation |
| `ingestion/df_mes_erp_eam.json` | T031 | Data Factory batch: MES/ERP/EAM + market feed → Bronze (read/propose only) |

## Constitution gates enforced here

- **IX Synthetic integrity** — `origin`/`sourceId` preserved verbatim Bronze→Silver→Gold;
  synthetic data bucketed to a separate `data_class` and **never** counted in a real KPI;
  readings missing provenance are quarantined, never defaulted.
- **VI Explainability** — stale/late/missing telemetry is flagged (Suspect / Activator alert),
  never presented as current.
- **IV One-way OT→IT** — ingestion is device→cloud only; Data Factory reads systems of record
  and proposes; no write-back path.
- **VIII Test-first** — the provenance/data-quality gate (T026/T032) is a passing pytest.

## Run the gate locally

```powershell
pip install -e libs\novasteel_core   # provides novasteel_core contracts
python -m pytest platform\medallion\tests -q
```

## Deploy to the live Fabric workspace

1. **Workspace + capacity**: create a Fabric workspace and assign it to capacity
   `fabnovasteedevox26fi` (Fabric portal, or `scripts/create_fabric_workspace.ps1`).
2. **Lakehouse**: create lakehouse `onelake_novasteel` (medallion Bronze/Silver/Gold Delta tables).
3. **Eventhouse**: create KQL DB `novasteel-rti`; run `rti/eventhouse.kql`.
4. **Eventstream**: import `rti/eventstream-telemetry.json`; bind the IoT Hub source
   (`iot-novastee-dev-ox26fi`, consumer group `fabric-rti`) with a Key Vault–sourced secret.
5. **Notebooks**: import the three `medallion/*.py` notebooks; schedule Bronze→Silver→Gold.
6. **Activator**: create rules from `rti/activator-freshness.kql`; route to the ops dashboard.
7. **Data Factory**: import `ingestion/df_mes_erp_eam.json`; wire MES/ERP/EAM/market endpoints.

> The `medallion/transforms.py` functions are the **reference semantics**; the Spark
> notebooks mirror them so behaviour matches the passing pytest gate.

## Live environment status (2026-07-02)

Provisioned on the F8 capacity `fabnovasteedevox26fi` (workspace **novasteel-dev**):
Lakehouse `onelake_novasteel`, Eventhouse/KQL DB `novasteel_rti`, Eventstream `es_telemetry`,
DataPipeline `df_mes_erp_eam`, and notebooks `bronze_telemetry` / `silver_telemetry` /
`gold_marts` / `p1_rul_scoring` (all on a **daily 06:00 UTC schedule**).

- **Simulator → IoT Hub is LIVE**: device `sim-LU-BF1` publishes `SimulatorDeviceMessage`
  device→cloud (verified via `az iot hub monitor-events`). IoT Hub consumer group
  **`fabric-rti`** is created for Fabric.
- **Eventhouse** `TelemetryRaw` table + `TelemetryRawMapping` created; synthetic telemetry
  ingested and queried with provenance preserved (`origin=Synthetic`).
- **P1 RUL scoring runs on live features**: `workloads/p1_predictive_maintenance/run_p1_live.py`
  ingests a degrading-furnace series, queries it back from the eventhouse, and produces a
  `LiningFailureRisk` prediction with `timeToFailureDays≥21` (SC-003).

### Bind Eventstream → IoT Hub (AUTOMATED via API — no portal step)

The Fabric connections API **does** support IoT Hub — the connection type is **`IoTHub`**
(exact casing; `IotHub` / `AzureEventHubs` are rejected). The live binding is scripted in
`scripts/bind_eventstream_iothub.ps1`:

1. Apply `rti/eventhouse.kql` (creates `TelemetryRaw`) **and** `rti/eventhouse-staging.kql`
   (creates the `TelemetryIngest` staging table + `ExpandTelemetry` fan-out + update policy).
2. Run `scripts/bind_eventstream_iothub.ps1` — it creates the `IoTHub` connection
   (`IoTHub.Contents` + Basic creds = the `service` SAS policy/key) and sets the eventstream
   topology (AzureIoTHub source → DefaultStream → Eventhouse destination) via `updateDefinition`.

Design note: IoT Hub device messages are **batches** (`SimulatorDeviceMessage.readings[]`), so
the Eventhouse destination targets the `TelemetryIngest` staging table and the KQL update policy
`ExpandTelemetry` (mv-expand) fans each batch into flat `TelemetryRaw` — provenance preserved.
Two gotchas: the Eventhouse destination `itemId` must be the **KQLDatabase** item id, and its
`inputNodes` must reference the **stream**, not the source.

**Verified live (2026-07-17):** simulator → IoT Hub → Eventstream → `TelemetryIngest` →
`TelemetryRaw` at ~7000 rows / 3 min, all `Origin=Synthetic`.

Once bound, live simulator telemetry flows automatically into `TelemetryRaw`, and the scheduled
medallion notebooks promote it Bronze → Silver → Gold for `p1_rul_scoring`.

### OneLake shortcut: KQL DB → lakehouse (so notebooks read live TelemetryRaw)

1. Enable **OneLake availability** on the KQL table (mirrors it to OneLake as Delta):
   `.alter table TelemetryRaw policy mirroring dataformat=parquet with (IsEnabled=true, TargetLatencyInMinutes=5)`
2. Create a **lakehouse shortcut** to the mirrored table (Fabric Shortcuts API):
   `POST /v1/workspaces/{ws}/items/{lakehouseId}/shortcuts` with
   `{ "path":"Tables", "name":"telemetry_raw_kql", "target":{ "oneLake":{ "workspaceId":<ws>, "itemId":<KQLDatabaseId>, "path":"Tables/TelemetryRaw" } } }`.
3. Bind the default lakehouse to the medallion notebooks so table names resolve
   (`scripts/bind_notebook_lakehouse.py` sets `metadata.dependencies.lakehouse`); notebooks
   reference tables by **bare name** (e.g. `spark.read.table("telemetry_raw_kql")`).

**Status (2026-07-18):** shortcut created + registered as a queryable lakehouse table; live data
mirrored to OneLake (Delta files confirmed). Medallion notebooks run green end-to-end
(bronze → silver → gold_furnace_features) once (a) the capacity is **≥F4** and (b) each `.py`
notebook has a **default lakehouse** bound in its `# META`/`dependencies.lakehouse` block.

> ⚠️ **F2 cannot run Spark notebooks** — it rejects them with HTTP 430
> `TooManyRequestsForCapacity`. Live KQL/Eventhouse ingestion runs fine on F2, but Bronze→Gold
> promotion needs **≥F4**. Bump the capacity for a batch window, then drop back to F2:
> `az rest --method patch --uri ".../capacities/{name}?api-version=2023-11-01" --body '{"sku":{"name":"F4","tier":"Fabric"}}'`

Use `scripts/bind_medallion_lakehouse.py <notebookId> ...` to bind the default lakehouse into a
`.py` notebook definition (it also repairs the stale `onelake_novasteel.` schema prefix on table
names) so on-demand / scheduled runs resolve `spark.read.table(...)` without an interactive attach.

