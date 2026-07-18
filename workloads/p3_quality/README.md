# P3 — Quality Prediction & SPC (decision-support)

Predicts automotive-grade (DP800) coil outcomes per heat from process features, links
**predicted-vs-actual** outcomes, proposes **reviewable** corrective adjustments for recoverable
excursions, and raises **SPC-drift** signals from control charts. Decision-support only — a
metallurgist reviews and approves; nothing is actuated (Constitution I).

## Success criterion
- **SC-004**: ≥ **+8%** high-grade yield.

On the deterministic reference batch (20 heats) the model lifts high-grade yield from **0.65 →
0.95** (+30 percentage points) by flagging recoverable sulphur/inclusion excursions for an
approved in-run fix. Non-recoverable excursions (e.g., severe inclusion) are flagged but get **no**
auto-fix.

## Model
- `generate_quality_scenario.py` — deterministic heats with process features and ground-truth
  high-grade outcomes; recoverable and non-recoverable excursions; a late upward temperature
  drift for SPC.
- `spc.py` — dependency-free 3-sigma control limits + Western Electric rules 1 & 2.
- `quality_model.py` — `predict_heat` → `Prediction(kind=QualityOutcome)` with evidence + a
  `Recommendation(Proposed)` for recoverable heats; `spc_drift_prediction` →
  `Prediction(kind=SpcDrift)`; `baseline_yield` / `recommended_yield` / `yield_uplift`.
- `decision_service.py` — quality prediction audit + human Confirm/Edit/Reject (ReviewerRole.Quality).
- `p3_notebook.py` — Fabric wrapper: reads `gold_quality_features`, writes
  `p3_quality_predictions`, `p3_quality_recommendations`, `p3_spc_drift`.

## Explainability / safety
- Every prediction carries per-metric `evidence` and confidence (Constitution VI).
- Recommendations carry a rationale and pass Content Safety; emitted `Proposed` for review.
- SPC drift is detected on the reference batch at `HEAT-DE-016` (3-sigma), demonstrating early
  warning before the grade band is breached.

## Explainability (Principle VI)
- `explainer.py` — `QualityExplainer` produces a grounded **root-cause narrative** for a heat using
  **only** its evidence metrics (sulphur/inclusion/tapping temp vs spec), states **uncertainty**
  from the model confidence, references the recommended fix, passes Content Safety, and **declines**
  rather than fabricates. Injectable `ChatClient`; unit-tested with a fake.
- Advisory only — the prediction stays `Raised` for metallurgist review (Principle I).

## Simulator telemetry (P3.1)
The simulator emits the quality signals this pillar consumes on each blast furnace —
`TappingTemp`, `SulfurPct`, `InclusionIndex` — with in-spec baselines inside the automotive
DP800 bands (sulphur ≤ 0.010 %, inclusion ≤ 2.0, tapping 1630–1670 °C). SPC control limits are
computed downstream in `spc.py` from an in-control window. See
`apps/steel_factory_simulator/.../AssetCatalog.cs`.

## Golden fixture
`libs/fixtures/p3_quality_prediction_golden.json` — the deterministic `Prediction` for a known
at-risk heat; `test_p3_golden.py` regression-guards the model output.

## Test
```
python -m pytest workloads/p3_quality/tests -q
```
