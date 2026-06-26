using Microsoft.Extensions.Options;
using NovaSteel.Contracts;
using SteelFactorySimulator.Options;
using SteelFactorySimulator.Simulation;

namespace SteelFactorySimulator.Tests;

public sealed class DegradingFurnaceScenarioTests
{
    [Fact]
    public void DegradingFurnaceReplayIsDeterministicAndHasTwentyOneDaySignal()
    {
        var start = DateTimeOffset.Parse("2026-01-01T06:00:00Z");
        var firstRun = CreateEngine(4242).GenerateDegradingFurnaceReplay("LU-BF1", start, horizonDays: 30, samplesPerDay: 1)
            .Where(reading => reading.Metric == Metric.HeatFlux)
            .ToArray();
        var secondRun = CreateEngine(4242).GenerateDegradingFurnaceReplay("LU-BF1", start, horizonDays: 30, samplesPerDay: 1)
            .Where(reading => reading.Metric == Metric.HeatFlux)
            .ToArray();

        Assert.Equal(firstRun.Select(reading => reading.Value), secondRun.Select(reading => reading.Value));
        for (var i = 1; i < firstRun.Length; i++)
        {
            Assert.True(firstRun[i].Value > firstRun[i - 1].Value, $"HeatFlux should increase at sample {i}.");
        }

        var initial = firstRun[0].Value;
        var twentyOneDaysBeforeFailure = firstRun[9].Value;
        var final = firstRun[^1].Value;
        Assert.True(twentyOneDaysBeforeFailure - initial > 20, "A detectable heat-flux signal must exist 21 days before scripted failure.");
        Assert.True(final - initial > 90, "The full degradation horizon must produce a strong failure trend.");
        Assert.Contains(firstRun, reading => reading.Quality == Quality.Suspect);
        Assert.Contains(firstRun, reading => reading.Quality == Quality.Bad);
    }

    private static SensorReadingEngine CreateEngine(int seed) =>
        new(Microsoft.Extensions.Options.Options.Create(new SimulatorOptions { Seed = seed }));
}
