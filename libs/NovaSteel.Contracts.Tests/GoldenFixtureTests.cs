using System.IO;
using System.Text.Json;
using FluentAssertions;
using NovaSteel.Contracts;
using Xunit;

namespace NovaSteel.Contracts.Tests;

public class GoldenFixtureTests
{
    private static string FixturePath(string name)
    {
        var dir = AppContext.BaseDirectory;
        while (dir is not null && !Directory.Exists(Path.Combine(dir, "libs", "fixtures")))
            dir = Directory.GetParent(dir)?.FullName;

        if (dir is null)
            throw new DirectoryNotFoundException("Could not locate libs/fixtures from test output.");

        return Path.Combine(dir, "libs", "fixtures", name);
    }

    private static List<T> ReadJsonLines<T>(string name)
    {
        return File.ReadLines(FixturePath(name))
            .Where(line => !string.IsNullOrWhiteSpace(line))
            .Select(line => JsonSerializer.Deserialize<T>(line, NovaSteelJson.Options)
                ?? throw new InvalidDataException($"Could not deserialize fixture line in {name}."))
            .ToList();
    }

    [Fact]
    public void Golden_telemetry_fixture_deserialises()
    {
        var readings = ReadJsonLines<TelemetryReading>("telemetry_reading.json");
        var r = readings[0];

        readings.Should().HaveCountGreaterThanOrEqualTo(2);
        r.AssetId.Should().Be("LU-BF1");
        r.Metric.Should().Be(Metric.ThermocoupleTemp);
        r.Site.Should().Be(Site.LU);
        r.Origin.Should().Be(Origin.Real);
        r.SourceId.Should().Be("ot:LU-historian");

        var synthetic = readings.Should().ContainSingle(reading => reading.Origin == Origin.Synthetic).Which;
        synthetic.SourceId.Should().Be("sim:steel_factory_simulator@v1");
    }

    [Fact]
    public void Golden_market_fixture_deserialises()
    {
        var m = ReadJsonLines<MarketSignal>("market_signal.json")[0];

        m.Market.Should().Be(Site.LU);
        m.SpotPriceEurMwh.Should().Be(92.4);
    }
}
