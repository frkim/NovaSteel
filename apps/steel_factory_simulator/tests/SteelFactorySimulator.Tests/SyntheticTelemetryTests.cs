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

    private static SensorReadingEngine CreateEngine(int seed) =>
        new(Microsoft.Extensions.Options.Options.Create(new SimulatorOptions { Seed = seed }));
}
