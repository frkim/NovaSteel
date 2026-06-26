# Spec 03 — Furnace-Lining RUL Predictor

> **Sub-project 3** · KPI: 21-day advance failure warning · Stack: Python (`services/rul_predictor`)
> Source: [3_c4model.md](../../0_preliminary%20analysis/3_c4model.md) §3c, [usecase.md](../../usecase.md)

## Purpose

Predict remaining useful life (RUL) of furnace refractory lining from thermal
signatures using **physics-informed** features, and raise a "failure within 21
days" alert with a confidence band.

## Requirements

| ID | Requirement | Acceptance |
| --- | --- | --- |
| R-1 | Compute physics-informed features from a telemetry window: heat-flux mean/variance, wear-rate (Δ over time), thermal-cycling count, spectral energy | Feature function is pure + unit-tested |
| R-2 | Train an RUL regression model on simulator data with a labelled degradation scenario | Model trains; MAE below a set threshold on held-out data |
| R-3 | Provide a "fail within 21 days" binary classifier derived from RUL + confidence | Precision/recall above set thresholds on test set |
| R-4 | Each prediction returns `rulDays`, `failWithin21d:bool`, `confidence:0..1` | Schema validated |
| R-5 | **Suppress** the 21-day alert when confidence is below a threshold (no crying wolf) | Low-confidence case asserted to not alert |
| R-6 | Expose scoring via a FastAPI `POST /score` accepting a telemetry window | Endpoint test green |
| R-7 | Detect data drift between training and scoring distributions | Drift flag set on a shifted-input test |

## Out of scope

- No real Fabric Data Science deployment here — local scoring service is the seam.
- No automated retraining pipeline (drift only flags; retrain is a later concern).

## Success criteria

- `pytest` covers feature purity, model MAE threshold, classifier precision/recall,
  confidence-gated alert suppression, and drift detection — all on simulator-derived
  fixtures so the 21-day scenario is reproducible.
