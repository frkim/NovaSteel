# Platform Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `subagent-driven-development`
> (recommended) or `executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the shared C# + Python contracts and in-memory transport that every
NovaSteel sub-project depends on.

**Architecture:** A C# class library (`NovaSteel.Contracts`) and a parity Python
package (`novasteel_core`) define one telemetry/market schema. Transport is
abstracted by `ITelemetrySource`/`ITelemetrySink` with in-memory implementations.
Cross-language parity is proven by shared golden JSON fixtures.

**Tech Stack:** .NET 10, xUnit, FluentAssertions, System.Text.Json · Python 3.13,
pydantic v2, pytest.

## Global Constraints

- Target framework: `net10.0`. Nullable + implicit usings enabled.
- JSON: camelCase property names, ISO-8601 UTC timestamps, enums as strings.
- Unknown enum string → defined fallback member, never an exception (F-2).
- Python models use pydantic v2; field aliases produce camelCase JSON identical to C#.
- Golden fixtures live in `libs/fixtures/` and are the single source of truth.

---

### Task 1: Solution + Contracts project scaffold

**Files:**
- Create: `NovaSteel.sln`
- Create: `libs/NovaSteel.Contracts/NovaSteel.Contracts.csproj`
- Create: `libs/NovaSteel.Contracts.Tests/NovaSteel.Contracts.Tests.csproj`

- [ ] **Step 1: Create solution and projects**

```bash
dotnet new sln -n NovaSteel
dotnet new classlib -n NovaSteel.Contracts -o libs/NovaSteel.Contracts -f net10.0
dotnet new xunit -n NovaSteel.Contracts.Tests -o libs/NovaSteel.Contracts.Tests -f net10.0
dotnet sln add libs/NovaSteel.Contracts libs/NovaSteel.Contracts.Tests
dotnet add libs/NovaSteel.Contracts.Tests reference libs/NovaSteel.Contracts
dotnet add libs/NovaSteel.Contracts.Tests package FluentAssertions
```

- [ ] **Step 2: Verify it builds** — Run: `dotnet build`. Expected: success, 0 errors.
- [ ] **Step 3: Commit** — `git add -A && git commit -m "chore: scaffold NovaSteel solution + Contracts"`

---

### Task 2: Enums with safe-fallback parsing (F-2)

**Files:**
- Create: `libs/NovaSteel.Contracts/Enums.cs`
- Test: `libs/NovaSteel.Contracts.Tests/EnumsTests.cs`

**Produces:** `AssetType`, `Site`, `Quality`, `Metric` enums + `EnumParse.OrFallback<T>`.

- [ ] **Step 1: Write the failing test**

```csharp
public class EnumsTests
{
    [Fact]
    public void Unknown_metric_falls_back_to_Unknown()
    {
        EnumParse.OrFallback("NotARealMetric", Metric.Unknown).Should().Be(Metric.Unknown);
    }

    [Fact]
    public void Known_site_parses()
    {
        EnumParse.OrFallback("DE", Site.LU).Should().Be(Site.DE);
    }
}
```

- [ ] **Step 2: Run test to verify it fails** — Run: `dotnet test`. Expected: FAIL (types not defined).
- [ ] **Step 3: Write minimal implementation**

```csharp
namespace NovaSteel.Contracts;

public enum AssetType { Unknown = 0, BlastFurnace, RollingMill, Utility }
public enum Site { LU = 0, DE, BE, ES }
public enum Quality { Good = 0, Suspect, Bad }
public enum Metric { Unknown = 0, ThermocoupleTemp, HeatFlux, Vibration, Throughput, PowerDrawKw }

public static class EnumParse
{
    public static T OrFallback<T>(string? value, T fallback) where T : struct, Enum
        => Enum.TryParse<T>(value, ignoreCase: true, out var parsed) ? parsed : fallback;
}
```

- [ ] **Step 4: Run test to verify it passes** — Run: `dotnet test`. Expected: PASS.
- [ ] **Step 5: Commit** — `git commit -am "feat(contracts): enums with safe fallback parsing"`

---

### Task 3: TelemetryReading + MarketSignal records (F-1, F-3)

**Files:**
- Create: `libs/NovaSteel.Contracts/TelemetryReading.cs`
- Create: `libs/NovaSteel.Contracts/MarketSignal.cs`
- Create: `libs/NovaSteel.Contracts/NovaSteelJson.cs`
- Test: `libs/NovaSteel.Contracts.Tests/SerializationTests.cs`

**Produces:** `TelemetryReading`, `MarketSignal` records + `NovaSteelJson.Options`.

- [ ] **Step 1: Write the failing test**

```csharp
public class SerializationTests
{
    [Fact]
    public void TelemetryReading_round_trips_camelCase()
    {
        var r = new TelemetryReading("LU-BF1", AssetType.BlastFurnace, Site.LU,
            Metric.ThermocoupleTemp, 1487.2, "C",
            DateTimeOffset.Parse("2026-06-21T10:00:00Z"), Quality.Good);
        var json = JsonSerializer.Serialize(r, NovaSteelJson.Options);
        json.Should().Contain("\"assetId\":\"LU-BF1\"").And.Contain("\"value\":1487.2");
        var back = JsonSerializer.Deserialize<TelemetryReading>(json, NovaSteelJson.Options);
        back.Should().Be(r);
    }
}
```

- [ ] **Step 2: Run test to verify it fails** — Run: `dotnet test`. Expected: FAIL.
- [ ] **Step 3: Write minimal implementation**

```csharp
// NovaSteelJson.cs
namespace NovaSteel.Contracts;
public static class NovaSteelJson
{
    public static readonly JsonSerializerOptions Options = new(JsonSerializerDefaults.Web)
    {
        Converters = { new JsonStringEnumConverter() },
        WriteIndented = false
    };
}

// TelemetryReading.cs
public readonly record struct TelemetryReading(
    string AssetId, AssetType AssetType, Site Site, Metric Metric,
    double Value, string Unit, DateTimeOffset Timestamp, Quality Quality);

// MarketSignal.cs
public readonly record struct MarketSignal(
    Site Market, DateTimeOffset Timestamp, double SpotPriceEurMwh, double GridCarbonGramsPerKwh);
```

- [ ] **Step 4: Run test to verify it passes** — Run: `dotnet test`. Expected: PASS.
- [ ] **Step 5: Commit** — `git commit -am "feat(contracts): TelemetryReading + MarketSignal records"`

---

### Task 4: Transport abstraction + in-memory impl (F-4)

**Files:**
- Create: `libs/NovaSteel.Contracts/Transport.cs`
- Test: `libs/NovaSteel.Contracts.Tests/InMemoryTransportTests.cs`

**Produces:** `ITelemetrySink`, `ITelemetrySource`, `InMemoryTelemetryChannel`.

- [ ] **Step 1: Write the failing test**

```csharp
[Fact]
public async Task Published_readings_are_observed_by_source()
{
    var channel = new InMemoryTelemetryChannel();
    var reading = new TelemetryReading("LU-BF1", AssetType.BlastFurnace, Site.LU,
        Metric.HeatFlux, 12.3, "kW/m2", DateTimeOffset.UtcNow, Quality.Good);
    await channel.PublishAsync(reading);
    channel.Complete();
    var received = new List<TelemetryReading>();
    await foreach (var r in channel.ReadAllAsync()) received.Add(r);
    received.Should().ContainSingle().Which.Should().Be(reading);
}
```

- [ ] **Step 2: Run test to verify it fails** — Run: `dotnet test`. Expected: FAIL.
- [ ] **Step 3: Write minimal implementation**

```csharp
using System.Threading.Channels;
namespace NovaSteel.Contracts;

public interface ITelemetrySink { ValueTask PublishAsync(TelemetryReading reading, CancellationToken ct = default); }
public interface ITelemetrySource { IAsyncEnumerable<TelemetryReading> ReadAllAsync(CancellationToken ct = default); }

public sealed class InMemoryTelemetryChannel : ITelemetrySink, ITelemetrySource
{
    private readonly Channel<TelemetryReading> _channel = Channel.CreateUnbounded<TelemetryReading>();
    public ValueTask PublishAsync(TelemetryReading reading, CancellationToken ct = default) => _channel.Writer.WriteAsync(reading, ct);
    public void Complete() => _channel.Writer.Complete();
    public IAsyncEnumerable<TelemetryReading> ReadAllAsync(CancellationToken ct = default) => _channel.Reader.ReadAllAsync(ct);
}
```

- [ ] **Step 4: Run test to verify it passes** — Run: `dotnet test`. Expected: PASS.
- [ ] **Step 5: Commit** — `git commit -am "feat(contracts): in-memory telemetry transport"`

---

### Task 5: Golden fixtures (F-6)

**Files:**
- Create: `libs/fixtures/telemetry_reading.json`
- Create: `libs/fixtures/market_signal.json`
- Test: `libs/NovaSteel.Contracts.Tests/GoldenFixtureTests.cs`

- [ ] **Step 1: Write the failing test** — deserialise each fixture, assert key fields.

```csharp
[Fact]
public void Golden_telemetry_fixture_deserialises()
{
    var json = File.ReadAllText(FixturePath("telemetry_reading.json"));
    var r = JsonSerializer.Deserialize<TelemetryReading>(json, NovaSteelJson.Options);
    r.AssetId.Should().Be("LU-BF1");
    r.Metric.Should().Be(Metric.ThermocoupleTemp);
}
```

- [ ] **Step 2: Run to verify it fails** — Run: `dotnet test`. Expected: FAIL (file missing).
- [ ] **Step 3: Create the fixtures**

```json
// telemetry_reading.json
{"assetId":"LU-BF1","assetType":"BlastFurnace","site":"LU","metric":"ThermocoupleTemp","value":1487.2,"unit":"C","timestamp":"2026-06-21T10:00:00Z","quality":"Good"}
```
```json
// market_signal.json
{"market":"LU","timestamp":"2026-06-21T10:00:00Z","spotPriceEurMwh":92.4,"gridCarbonGramsPerKwh":310.0}
```

- [ ] **Step 4: Run to verify it passes** — Run: `dotnet test`. Expected: PASS.
- [ ] **Step 5: Commit** — `git commit -am "test(contracts): golden JSON fixtures"`

---

### Task 6: Python package + schema parity (F-5)

**Files:**
- Create: `libs/novasteel_core/pyproject.toml`
- Create: `libs/novasteel_core/novasteel_core/__init__.py`
- Create: `libs/novasteel_core/novasteel_core/models.py`
- Create: `libs/novasteel_core/tests/test_parity.py`

**Produces:** `TelemetryReading`, `MarketSignal` pydantic models with camelCase aliases.

- [ ] **Step 1: Write the failing test**

```python
import json, pathlib
from novasteel_core.models import TelemetryReading

FIX = pathlib.Path(__file__).parents[3] / "fixtures"

def test_telemetry_round_trips_camel():
    raw = json.loads((FIX / "telemetry_reading.json").read_text())
    r = TelemetryReading.model_validate(raw)
    assert r.asset_id == "LU-BF1"
    assert json.loads(r.model_dump_json(by_alias=True)) == raw
```

- [ ] **Step 2: Run to verify it fails** — Run: `pytest libs/novasteel_core`. Expected: FAIL (module missing).
- [ ] **Step 3: Write minimal implementation**

```python
# models.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class _Camel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=lambda s: s[0] + ''.join(w.capitalize() for w in s.split('_'))[1:] if False else _camel(s))

def _camel(s: str) -> str:
    head, *tail = s.split('_')
    return head + ''.join(w.capitalize() for w in tail)

class TelemetryReading(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_camel)
    asset_id: str
    asset_type: str
    site: str
    metric: str
    value: float
    unit: str
    timestamp: datetime
    quality: str

class MarketSignal(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=_camel)
    market: str
    timestamp: datetime
    spot_price_eur_mwh: float
    grid_carbon_grams_per_kwh: float
```

- [ ] **Step 4: Run to verify it passes** — Run: `pip install -e libs/novasteel_core pydantic pytest && pytest libs/novasteel_core`. Expected: PASS.
- [ ] **Step 5: Commit** — `git commit -am "feat(core): python parity models + fixture test"`

---

## Self-Review

- **Spec coverage:** F-1 (T3), F-2 (T2), F-3 (T3), F-4 (T4), F-5 (T6), F-6 (T5). ✅ all covered.
- **Placeholder scan:** no TBD/TODO; every code step has real code. ✅
- **Type consistency:** `TelemetryReading`/`MarketSignal` field names match across C# and Python and the fixtures. ✅
