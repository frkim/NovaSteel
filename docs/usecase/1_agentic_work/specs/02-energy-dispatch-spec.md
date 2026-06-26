# Spec 02 — Energy-Dispatch Optimisation Agent

> **Sub-project 2** · KPI: −14% energy/ton, −22% CO₂ · Stack: Python solver + C# API
> Source: [3_c4model.md](../../0_preliminary%20analysis/3_c4model.md) §3a, [usecase.md](../../usecase.md)

## Purpose

Schedule energy-intensive production steps into low-price / low-carbon time
windows, respecting production deadlines and furnace constraints, with a
human-in-the-loop approval step. The agent **recommends**, never actuates.

## Requirements

| ID | Requirement | Acceptance |
| --- | --- | --- |
| E-1 | Ingest a demand forecast, `MarketSignal` price + carbon series, and a set of schedulable jobs (each with energy, duration, earliest/latest finish) | Inputs validated against Foundation schema |
| E-2 | Produce a schedule that minimises a weighted cost = `α·price + β·carbon` subject to constraints | Solver returns a feasible assignment |
| E-3 | Never schedule a job past its deadline or beyond capacity per window | No constraint violation in output |
| E-4 | Output a `DispatchPlan` with per-job window, projected € and tCO₂ vs a naïve baseline (run-now) | Plan reports % savings |
| E-5 | Demonstrate ≥10% modelled energy-cost saving and ≥10% carbon saving on the reference scenario | Test asserts savings thresholds (proxy for the −14%/−22% targets) |
| E-6 | Expose a C# API `POST /dispatch/plan` returning the plan + rationale; `POST /dispatch/approve` logs the decision | API tests green; approval is audited |
| E-7 | Each recommendation carries a human-readable rationale | Rationale references the chosen windows and savings |

## Out of scope

- No direct control of plant equipment (recommendation-only, by design).
- No real-time sub-second loop — this is a planning horizon (hours/day-ahead).

## Success criteria

- `pytest` proves feasibility, constraint respect, and the savings thresholds on a
  fixed reference scenario.
- `dotnet test` covers the API contract and the audit log of approvals.
