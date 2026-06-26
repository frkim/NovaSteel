# Quickstart: AI-Powered Steel Production Optimization Platform

**Feature**: `001-steel-optimization-platform` | **Date**: 2026-06-23 | **Plan**: [plan.md](./plan.md)

A runnable validation guide proving the platform works end-to-end. It links to
[contracts/](./contracts) and [data-model.md](./data-model.md) rather than duplicating
them. Implementation code lives in the repo (`libs/`, `apps/`, `workloads/`,
`infrastructure/`) and is built out in `tasks.md`; this guide is **build → run → deploy →
validate**.

> Run all commands from the **repository root**: `D:\work\20260507 - NovaSteel\NovaSteel`.

## Prerequisites

| Tool | Version | Used for |
|------|---------|----------|
| .NET SDK | 8.0+ | `libs/NovaSteel.Contracts`, `.Tests`, the simulator |
| Python | 3.11+ | `libs/novasteel_core`, energy solver, Fabric notebook logic |
| Azure CLI | 2.76+ (`az bicep` enabled) | infrastructure build/validate/deploy |
| Docker | latest | building the simulator container image |
| Entra ID | subscription Owner/Contributor + an EU subscription | deployment |

Azure context:

```powershell
az login
az account set --subscription "<your-EU-subscription-id>"
```

---

## 1. Build & test the shared contracts (`libs/`) — TEST-FIRST (Constitution VIII)

The golden fixtures in `libs/fixtures` are the single source of truth; both the C# and
Python stacks must round-trip them identically. After the **CT-2** additive change
(`origin` + `sourceId` on `TelemetryReading`), the fixtures and both mirrors are updated
together.

**.NET (xUnit):**

```powershell
dotnet test libs/NovaSteel.Contracts.Tests/NovaSteel.Contracts.Tests.csproj
```

Expected: all tests pass, including `GoldenFixtureTests` deserializing
`libs/fixtures/telemetry_reading.json` (now containing `"origin":"Real"` and a `sourceId`)
and the new fixtures (`prediction.json`, `recommendation.json`, `energy_plan.json`,
`human_decision.json`, `audit_record.json`).

**Python (pytest):**

```powershell
cd libs/novasteel_core
pip install -e .[dev]
pytest
cd ../..
```

Expected: `test_parity.py` passes — the Python models parse the **same** fixtures with
camelCase parity, confirming C#↔Python contract parity for the provenance marker.

> Validation point (Constitution VIII/IX): both stacks accept the `origin`/`sourceId`
> fields with defaults, proving the change is additive and provenance is carried in the
> contract itself.

---

## 2. Run the simulator locally against the in-memory transport

The `apps/steel_factory_simulator` Container App is the **device side of IoT Hub**. Locally
it can publish to the in-memory transport (`InMemoryTelemetryChannel` in
`libs/NovaSteel.Contracts/Transport.cs`) — no Azure needed — to prove contract conformance
and synthetic provenance before wiring real IoT Hub.

```powershell
cd apps/steel_factory_simulator
dotnet run --project src --transport inmemory
```

Then open the web UI (default `http://localhost:5080`) and verify:

- **Start/Stop** toggles telemetry generation for furnaces/mills/utilities.
- **Sensor overview** shows live readings conforming to
  [`telemetry-reading.schema.json`](./contracts/telemetry-reading.schema.json).
- Every emitted reading carries **`origin = "Synthetic"`** and a `sourceId`
  (e.g. `sim:steel_factory_simulator@v1`) — Constitution IX.
- **Incident/failure injection** lets you inject an abnormal metric or a failure scenario.

Run the simulator's contract-conformance tests:

```powershell
dotnet test tests
cd ../..
```

Expected: simulated messages validate against
[`simulator-device-message.schema.json`](./contracts/simulator-device-message.schema.json)
and every reading is `Synthetic`.

---

## 3. Deploy the infrastructure (Bicep, EU-only)

> **Prerequisite (CT-1):** before first deploy, the two excluded modules
> (`infrastructure/modules/machine-learning.bicep`, `infrastructure/modules/search.bicep`)
> and all their wiring MUST be removed per plan.md → *CT-1 ordered removal task*. Verify the
> template builds clean first:

```powershell
az bicep build --file infrastructure/main.bicep
```

Expected: builds with **no warnings about unresolved `search`/`machineLearning`
references**. Then validate and deploy at subscription scope (EU region enforced by
`@allowed` + the new Azure Policy module, Constitution III):

```powershell
# Validate
az deployment sub validate `
  --location swedencentral `
  --template-file infrastructure/main.bicep `
  --parameters infrastructure/main.bicepparam

# Deploy
az deployment sub create `
  --location swedencentral `
  --template-file infrastructure/main.bicep `
  --parameters infrastructure/main.bicepparam
```

Expected outputs (from `main.bicep`): `resourceGroupName`, `location` (an EU region),
`foundryEndpoint`, `keyVaultName`, `dataLakeName`, `fabricCapacityName`. There MUST be
**no** `searchName` or `machineLearningWorkspaceName` output (removed in CT-1).

Validation points:
- **EU residency (Constitution III):** attempting `--location eastus` (or any non-EU
  region) fails — blocked by `@allowed` and the `allowedLocations` policy (research.md R9).
- **One-way OT→IT (Constitution IV):** IoT Hub is provisioned device→cloud only; no
  cloud-to-device/command path exists.

---

## 4. P1 Independent Test — degrading-furnace replay → ≥21-day warning (SC-003)

This is the headline acceptance test (spec User Story 1 Independent Test, FR-002, SC-003).
It uses a **deterministic, replayable synthetic failure case** so it runs without real
plant data — and the synthetic data stays queryable as synthetic end-to-end (Constitution
IX).

1. **Replay** a degrading-furnace scenario from the simulator (synthetic-marked):

   ```powershell
   cd apps/steel_factory_simulator
   dotnet run --project src --replay degrading-furnace-LU-BF1 --speed 100x --transport iothub
   cd ../..
   ```

   The scenario streams a furnace whose thermal signature degrades toward a lining failure,
   on the **same ingestion path as real OT** (IoT Hub → Event Hubs → Fabric RTI/OneLake),
   every reading tagged `origin = Synthetic`, `sourceId = sim:...`.

2. **Score** the P1 RUL model (Fabric Data Science, research.md R1) over the Silver/Gold
   feature window:

   ```powershell
   python workloads/p1_predictive_maintenance/run_rul_scoring.py --asset LU-BF1
   ```

3. **Assert** the platform raises a `Prediction`
   ([`prediction.schema.json`](./contracts/prediction.schema.json)) with:
   - `kind = "LiningFailureRisk"`, `assetId = "LU-BF1"`,
   - **`timeToFailureDays >= 21`** at least 21 days before the scripted failure date (SC-003),
   - non-empty `evidence` (contributing thermal signals — FR-003, Constitution VI),
   - a populated `modelVersion` (traceability — Constitution II),
   - `origin = "Synthetic"` (provenance preserved — Constitution IX).

4. **Human-in-the-loop & audit (FR-004/016/017, SC-005):** record a `HumanDecision`
   ([`human-decision.schema.json`](./contracts/human-decision.schema.json)) confirming the
   prediction and assert an immutable `AuditRecord`
   ([`audit-record.schema.json`](./contracts/audit-record.schema.json)) was appended
   (who/what/when/inputs/modelVersion/rationale). **No equipment action is taken** — a work
   order is only *proposed* to the maintenance system.

Run the full P1 integration test:

```powershell
dotnet test --filter Category=P1Independent
```

Expected: green — the ≥21-day warning is demonstrated, the decision is recorded, the audit
trail is complete and immutable, and the data is queryable as `Synthetic` (never presented
as real KPI input).

---

## What "done" looks like (validation summary)

| Check | Proves | Authority |
|-------|--------|-----------|
| `dotnet test` + `pytest` green on golden fixtures | Contract-first parity incl. provenance | Constitution VIII/IX |
| Simulator emits `origin=Synthetic` on the real path | Synthetic-data integrity | Constitution IX |
| `az bicep build` clean, no search/ML refs | Scoped stack (CT-1) | Constitution V |
| Non-EU deploy blocked | EU residency | Constitution III |
| IoT Hub device→cloud only | One-way OT→IT | Constitution IV |
| P1 replay → `timeToFailureDays >= 21` + evidence | ≥21-day warning, explainability | SC-003, FR-002/003 |
| HumanDecision recorded + immutable AuditRecord | Human-in-the-loop + traceability | SC-005, FR-016/017 |

Next: run `/speckit.tasks` to generate `tasks.md` (CT-1 cleanup first, then CT-2 contract
changes + fixtures, then P1→P4 workloads per spec priority).
