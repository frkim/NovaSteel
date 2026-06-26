# Spec 01 — Steel Factory Simulator

> **Sub-project 1** · feeds 2·3·4 · Stack: C# .NET worker service (`apps/steel_factory_simulator`)
> Source: [01-master-design.md](../01-master-design.md) §B, [usecase.md](../../usecase.md)

## Purpose

Emit physics-plausible synthetic telemetry for furnaces, rolling mills, and
utilities across the four sites, plus a day-ahead energy market feed — so the AI
workloads can be developed and tested entirely offline.

## Requirements

| ID | Requirement | Acceptance |
| --- | --- | --- |
| S-1 | Generate `TelemetryReading`s for ≥1 blast furnace per site (LU, DE, BE, ES) | Stream contains all 4 sites |
| S-2 | Furnace thermocouple temp follows a realistic band (1400–1550 °C) with slow drift + noise | Values stay in band; mean ≈ configurable setpoint |
| S-3 | Model **lining wear** as a monotonically increasing state that raises heat-flux variance over a campaign | Heat-flux variance trends up as wear → enables RUL signal |
| S-4 | Inject a configurable **degradation scenario** that drives a furnace toward failure within N days | RUL predictor can detect the 21-day signal in tests |
| S-5 | Emit `MarketSignal` day-ahead spot price + grid carbon with daily peak/off-peak shape | Price has plausible diurnal curve; carbon anti-correlates with renewables proxy |
| S-6 | Configurable emission **rate** and **seed** for deterministic tests | Same seed → identical stream |
| S-7 | Publish via `ITelemetrySink` (Foundation) | Swappable in-memory vs Azure later |
| S-8 | Occasionally tag readings `Suspect`/`Bad` at a configurable fault rate | Downstream quality filter is exercised |

## Out of scope

- No real sensor protocols (OPC-UA/Modbus) — synthetic only.
- No UI — it is a headless worker.

## Success criteria

- `dotnet test` covers: temperature band, wear monotonicity, determinism by seed,
  market diurnal shape, fault injection rate, all-sites coverage.
- Running the worker prints/streams readings at the configured rate.
