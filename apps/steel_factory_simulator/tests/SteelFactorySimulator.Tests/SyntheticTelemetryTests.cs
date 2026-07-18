using System.Text.Json;
using Microsoft.Extensions.Options;
using NovaSteel.Contracts;
using SteelFactorySimulator.Options;
using SteelFactorySimulator.Simulation;

namespace SteelFactorySimulator.Tests;

public sealed class SyntheticTelemetryTests
{
    [Fact]
    public void GeneratedReadingsCarrySyntheticOriginAndSourceId()
    {
        var engine = CreateEngine(1234);
        var readings = engine.Generate(DateTimeOffset.Parse("2026-06-23T12:00:00Z"), 0);

        Assert.NotEmpty(readings);
        Assert.All(readings, reading =>
        {
            Assert.Equal(Origin.Synthetic, reading.Origin);
            Assert.False(string.IsNullOrWhiteSpace(reading.SourceId));
        });
    }

    [Fact]
    public void GeneratedReadingSerializesToTelemetrySchemaShape()
    {
        var engine = CreateEngine(1234);
        var reading = engine.Generate(DateTimeOffset.Parse("2026-06-23T12:00:00Z"), 0).First();
        var json = JsonSerializer.Serialize(reading, NovaSteelJson.Options);
        using var document = JsonDocument.Parse(json);
        var root = document.RootElement;

        Assert.Equal("Synthetic", root.GetProperty("origin").GetString());
        Assert.False(string.IsNullOrWhiteSpace(root.GetProperty("sourceId").GetString()));
        Assert.Equal("BlastFurnace", root.GetProperty("assetType").GetString());
        Assert.Equal("LU", root.GetProperty("site").GetString());
        Assert.True(root.TryGetProperty("assetId", out _));
        Assert.True(root.TryGetProperty("metric", out _));
        Assert.True(root.TryGetProperty("value", out _));
        Assert.True(root.TryGetProperty("unit", out _));
        Assert.True(root.TryGetProperty("timestamp", out _));
        Assert.True(root.TryGetProperty("quality", out _));
    }

    [Fact]
    public void EmitsQualityAndTariffMetricsForP2AndP3()
    {
        var engine = CreateEngine(1234);
        var readings = engine.Generate(DateTimeOffset.Parse("2026-06-23T12:00:00Z"), 0);

        // P3 quality tap-chemistry on blast furnaces.
        Assert.Contains(readings, r => r.Metric == Metric.TappingTemp && r.AssetType == AssetType.BlastFurnace);
        Assert.Contains(readings, r => r.Metric == Metric.SulfurPct && r.AssetType == AssetType.BlastFurnace);
        Assert.Contains(readings, r => r.Metric == Metric.InclusionIndex && r.AssetType == AssetType.BlastFurnace);

        // P2 grid tariff / carbon at the utility interface.
        Assert.Contains(readings, r => r.Metric == Metric.SpotPriceEurMwh && r.AssetType == AssetType.Utility);
        Assert.Contains(readings, r => r.Metric == Metric.GridCarbonGPerKwh && r.AssetType == AssetType.Utility);

        // In-spec baselines (automotive-grade DP800 window) so P3 SPC/quality see a healthy process.
        var sulfur = readings.First(r => r.Metric == Metric.SulfurPct);
        Assert.InRange(sulfur.Value, 0.0, 0.010);
        var tapping = readings.First(r => r.Metric == Metric.TappingTemp);
        Assert.InRange(tapping.Value, 1600, 1720);
    }

    private static SensorReadingEngine CreateEngine(int seed) =>
        new(Microsoft.Extensions.Options.Options.Create(new SimulatorOptions { Seed = seed }));
}
