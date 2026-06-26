using FluentAssertions;
using NovaSteel.Contracts;
using Xunit;

namespace NovaSteel.Contracts.Tests;

public class InMemoryTransportTests
{
    [Fact]
    public async Task Published_readings_are_observed_by_source()
    {
        var channel = new InMemoryTelemetryChannel();
        var reading = new TelemetryReading("LU-BF1", AssetType.BlastFurnace, Site.LU,
            Metric.HeatFlux, 12.3, "kW/m2", DateTimeOffset.UtcNow, Quality.Good);

        await channel.PublishAsync(reading);
        channel.Complete();

        var received = new List<TelemetryReading>();
        await foreach (var r in channel.ReadAllAsync())
            received.Add(r);

        received.Should().ContainSingle().Which.Should().Be(reading);
    }
}
