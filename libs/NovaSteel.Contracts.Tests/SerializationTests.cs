using System.Text.Json;
using FluentAssertions;
using NovaSteel.Contracts;
using Xunit;

namespace NovaSteel.Contracts.Tests;

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
        json.Should().Contain("\"metric\":\"ThermocoupleTemp\"");
        json.Should().Contain("\"origin\":\"Real\"");
        json.Should().Contain("\"sourceId\":\"\"");

        var back = JsonSerializer.Deserialize<TelemetryReading>(json, NovaSteelJson.Options);
        back.Should().Be(r);
    }

    [Fact]
    public void TelemetryReading_preserves_synthetic_origin_and_source()
    {
        var r = new TelemetryReading("LU-BF1", AssetType.BlastFurnace, Site.LU,
            Metric.HeatFlux, 12.3, "kW/m2",
            DateTimeOffset.Parse("2026-06-21T10:00:01Z"), Quality.Good,
            Origin.Synthetic, "sim:steel_factory_simulator@v1");

        var json = JsonSerializer.Serialize(r, NovaSteelJson.Options);

        json.Should().Contain("\"origin\":\"Synthetic\"");
        json.Should().Contain("\"sourceId\":\"sim:steel_factory_simulator@v1\"");

        var back = JsonSerializer.Deserialize<TelemetryReading>(json, NovaSteelJson.Options);
        back.Should().Be(r);
    }

    [Fact]
    public void TelemetryReading_missing_provenance_uses_non_breaking_defaults()
    {
        const string oldShape = """
            {"assetId":"LU-BF1","assetType":"BlastFurnace","site":"LU","metric":"ThermocoupleTemp","value":1487.2,"unit":"C","timestamp":"2026-06-21T10:00:00Z","quality":"Good"}
            """;

        var back = JsonSerializer.Deserialize<TelemetryReading>(oldShape, NovaSteelJson.Options);

        back.Origin.Should().Be(Origin.Real);
        back.SourceId.Should().Be("");
    }

    [Fact]
    public void MarketSignal_round_trips_camelCase()
    {
        var m = new MarketSignal(Site.LU, DateTimeOffset.Parse("2026-06-21T10:00:00Z"), 92.4, 310.0);

        var json = JsonSerializer.Serialize(m, NovaSteelJson.Options);
        json.Should().Contain("\"spotPriceEurMwh\":92.4").And.Contain("\"gridCarbonGramsPerKwh\":310");

        var back = JsonSerializer.Deserialize<MarketSignal>(json, NovaSteelJson.Options);
        back.Should().Be(m);
    }
}
