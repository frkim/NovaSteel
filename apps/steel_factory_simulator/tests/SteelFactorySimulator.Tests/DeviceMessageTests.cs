using System.Text.Json;
using Microsoft.Extensions.Options;
using NovaSteel.Contracts;
using SteelFactorySimulator.Models;
using SteelFactorySimulator.Options;
using SteelFactorySimulator.Simulation;
using SteelFactorySimulator.Transport;

namespace SteelFactorySimulator.Tests;

public sealed class DeviceMessageTests
{
    [Fact]
    public void SimulatorDeviceMessageContainsSyntheticReadingsAndRoundTrips()
    {
        var engine = new SensorReadingEngine(Microsoft.Extensions.Options.Options.Create(new SimulatorOptions { Seed = 9876 }));
        var readings = engine.Generate(DateTimeOffset.Parse("2026-06-23T12:00:00Z"), 0).Take(3).ToArray();
        var message = SimulatorDeviceMessageFactory.Create("sim-LU-BF1", readings, "degrading-furnace-LU-BF1", DateTimeOffset.Parse("2026-06-23T12:01:00Z"));

        Assert.NotEmpty(message.Readings);
        Assert.All(message.Readings, reading => Assert.Equal(Origin.Synthetic, reading.Origin));

        var json = JsonSerializer.Serialize(message, NovaSteelJson.Options);
        var roundTripped = JsonSerializer.Deserialize<SimulatorDeviceMessage>(json, NovaSteelJson.Options);

        Assert.NotNull(roundTripped);
        Assert.Equal(message.DeviceId, roundTripped.DeviceId);
        Assert.Equal(message.SchemaVersion, roundTripped.SchemaVersion);
        Assert.Equal(message.InjectedScenario, roundTripped.InjectedScenario);
        Assert.Equal(message.Readings.Count, roundTripped.Readings.Count);
        Assert.All(roundTripped.Readings, reading =>
        {
            Assert.Equal(Origin.Synthetic, reading.Origin);
            Assert.False(string.IsNullOrWhiteSpace(reading.SourceId));
        });
    }
}
