# P1 Predictive Furnace-Lining Maintenance

Physics-informed RUL workload for NovaSteel blast-furnace lining wear. It uses deterministic synthetic `TelemetryReading` windows, extracts heat-flux wear features, extrapolates remaining useful life to the lining failure threshold, and raises `Prediction(kind=LiningFailureRisk)` only when degradation is actionable.

## Run

```powershell
pip install -e libs\novasteel_core
python -m pytest workloads\p1_predictive_maintenance\tests -q
python -m py_compile workloads\p1_predictive_maintenance\*.py
```

## Spec mapping

- FR-001/FR-002/SC-003: thermal trend analysis and >=21-day RUL warning.
- FR-003/Constitution VI: evidence, confidence, and model version on every prediction.
- FR-004/SC-005/Constitution I: maintenance decisions propose a work order id but never actuate equipment.
- FR-017/Constitution II: `AuditLog` appends immutable `AuditRecord` entries.
- Constitution IX: synthetic readings, predictions, and audits preserve `origin=Synthetic` and `source_id=sim:LU-BF1`.
