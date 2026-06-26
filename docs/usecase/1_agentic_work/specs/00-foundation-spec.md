# Spec 00 — Platform Foundation

> **Sub-project 0** · enabler for all others · Stack: C# (`NovaSteel.Contracts`) + Python (`novasteel_core`)
> Source: [01-master-design.md](../01-master-design.md) §C, [3_c4model.md](../../0_preliminary%20analysis/3_c4model.md)

## Purpose

Define the shared, versioned data contracts and transport abstractions that every
other sub-project consumes, so components stay decoupled and locally testable.

## Requirements

| ID | Requirement | Acceptance |
| --- | --- | --- |
| F-1 | A `TelemetryReading` record with: `assetId`, `assetType`, `site`, `metric`, `value:double`, `unit`, `timestamp:DateTimeOffset`, `quality` | Serialises to the canonical JSON in design §C |
| F-2 | Enums: `AssetType {BlastFurnace, RollingMill, Utility}`, `Site {LU, DE, BE, ES}`, `Quality {Good, Suspect, Bad}`, `Metric {ThermocoupleTemp, HeatFlux, Vibration, Throughput, PowerDrawKw, ...}` | Unknown enum value deserialises to a defined fallback, never throws |
| F-3 | A `MarketSignal` record: `market`, `timestamp`, `spotPriceEurMwh:double`, `gridCarbonGramsPerKwh:double` | Matches design §C |
| F-4 | `ITelemetrySource` (async stream of readings) and `ITelemetrySink` (async publish) interfaces | Both have an in-memory implementation for tests |
| F-5 | A Python package `novasteel_core` exposing the **same** schema via pydantic models | Golden JSON fixture round-trips identically in C# and Python |
| F-6 | Shared golden fixtures directory of example envelopes | Used by both `dotnet test` and `pytest` |

## Out of scope (YAGNI)

- No real Azure IoT Hub SDK wiring here — only the abstraction (adapter comes later).
- No persistence/ORM — Foundation is pure contracts + in-memory transport.

## Success criteria

- `dotnet test libs/NovaSteel.Contracts` green.
- `pytest libs/novasteel_core` green.
- A round-trip parity test proves C# and Python serialise `TelemetryReading` and
  `MarketSignal` to byte-identical JSON for the golden fixtures.
