# P2 — Energy Dispatch Optimization (decision-support)

Shifts and batches flexible furnace heats into the cheapest, lowest-carbon slots ahead of
their deadlines to cut energy, cost and CO2. **Recommendations only — the platform never
actuates grid or furnace equipment** (Constitution I). Every plan is emitted `Proposed` for
an energy manager to Approve / Adjust / Reject, producing an immutable EU-ETS audit trail
(Constitution II).

## Success criteria
- **SC-001**: ≥ **14%** energy reduction vs the uncoordinated baseline.
- **SC-002**: ≥ **22%** CO2 reduction vs the uncoordinated baseline.

On the deterministic reference scenario the heuristic delivers **17.3% energy** and **51.8%
CO2** reduction (comfortably above target), by removing redundant furnace warm-ups (batching)
and moving the campaign into the overnight low-carbon trough.

## Model
- `generate_energy_scenario.py` — deterministic hourly market curve (spot price + grid carbon,
  diurnal) and flexible heats with staggered readiness and slack deadlines.
- `dispatch_model.py` — `baseline_dispatch` (run each heat on arrival, many warm-ups, daytime
  peak) vs `optimize_dispatch` (one batched campaign in the greenest feasible window). Produces
  a contract-shaped `EnergyPlan` with baseline comparison and `deadline_breaches` guard.
- `decision_service.py` — `EnergyPlan` audit + human Approve/Adjust/Reject (ReviewerRole.Energy,
  RetentionClass.EnergyEts).
- `p2_notebook.py` — Fabric wrapper: reads `gold_energy_jobs` + `gold_market_signals`, writes
  `p2_energy_plans`.

## Safety / constraints
- Never starts a heat before its charge is ready or after its deadline; infeasible batches are
  **flagged** in `deadline_breaches`, never silently dropped or forced.
- One job per furnace per slot (no overlap).
- `Solver.Heuristic` by default; a MILP (PuLP/CBC) refinement can replace `optimize_dispatch`
  without changing the contract.

## Explainability (Principle VI)
- `explainer.py` — `EnergyPlanExplainer` produces a grounded, operator-facing rationale for a plan
  using **only** the plan's own numbers, always states **uncertainty**, passes Content Safety, and
  **declines** rather than fabricates. Injectable `ChatClient` (the deployed
  `p4_knowledge_capture.foundry_client.FoundryClient` satisfies it); unit-tested with a fake.
- Advisory only — the plan stays `Proposed` for human approval (Principle I).

## Simulator telemetry (P2.1)
The steel-factory simulator emits the energy inputs this pillar consumes: `PowerDrawKw` (furnace
power draw) on every asset, plus a diurnal **grid tariff** signal at the utility interface —
`SpotPriceEurMwh` and `GridCarbonGPerKwh` (the load-shift windows). See
`apps/steel_factory_simulator/.../AssetCatalog.cs`.

## Golden fixture
`libs/fixtures/p2_energy_plan_golden.json` — the deterministic `EnergyPlan` produced by the
reference scenario; `test_p2_golden.py` regression-guards the model output shape and values.

## Test
```
python -m pytest workloads/p2_energy_dispatch/tests -q
```
