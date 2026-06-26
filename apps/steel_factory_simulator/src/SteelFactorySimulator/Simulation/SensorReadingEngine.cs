using System.Security.Cryptography;
using System.Text;
using Microsoft.Extensions.Options;
using NovaSteel.Contracts;
using SteelFactorySimulator.Options;

namespace SteelFactorySimulator.Simulation;

public sealed class SensorReadingEngine(IOptions<SimulatorOptions> options)
{
    private readonly SimulatorOptions _options = options.Value;

    public IReadOnlyList<TelemetryReading> Generate(DateTimeOffset timestamp, int stepIndex, ActiveScenario? scenario = null)
    {
        var readings = new List<TelemetryReading>(AssetCatalog.DefaultAssets.Sum(asset => asset.Metrics.Count));
        foreach (var asset in AssetCatalog.DefaultAssets)
        {
            foreach (var metric in asset.Metrics)
            {
                readings.Add(GenerateReading(asset, metric, timestamp, stepIndex, scenario));
            }
        }

        return readings;
    }

    public IReadOnlyList<TelemetryReading> GenerateDegradingFurnaceReplay(
        string assetId,
        DateTimeOffset start,
        int horizonDays,
        int samplesPerDay = 1)
    {
        if (samplesPerDay <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(samplesPerDay), "Samples per day must be positive.");
        }

        var scenario = new ActiveScenario($"degrading-furnace-{assetId}", "degrading-furnace", assetId, start, horizonDays);
        var readings = new List<TelemetryReading>();
        var totalSamples = (horizonDays * samplesPerDay) + 1;
        for (var sample = 0; sample < totalSamples; sample++)
        {
            var timestamp = start.AddMinutes(sample * (1440.0 / samplesPerDay));
            readings.AddRange(Generate(timestamp, sample, scenario).Where(reading => reading.AssetId == assetId));
        }

        return readings;
    }

    private TelemetryReading GenerateReading(
        AssetDefinition asset,
        MetricProfile profile,
        DateTimeOffset timestamp,
        int stepIndex,
        ActiveScenario? scenario)
    {
        var random = CreateDeterministicRandom(_options.Seed, asset.AssetId, profile.Metric, stepIndex);
        var elapsedDays = stepIndex * Math.Max(_options.StepMinutes, 1) / 1440.0;
        var phase = StableUnitInterval(asset.AssetId, profile.Metric.ToString()) * Math.Tau;
        var dayFraction = timestamp.TimeOfDay.TotalDays;
        var cycle = Math.Sin((dayFraction * Math.Tau) + phase) * profile.CycleAmplitude;
        var noise = ((random.NextDouble() * 2) - 1) * profile.NoiseAmplitude;
        var value = profile.Baseline + cycle + noise + (elapsedDays * profile.DriftPerDay);
        var quality = Quality.Good;

        if (scenario is not null &&
            scenario.Kind.Equals("degrading-furnace", StringComparison.OrdinalIgnoreCase) &&
            asset.AssetId.Equals(scenario.AssetId, StringComparison.OrdinalIgnoreCase) &&
            asset.AssetType == AssetType.BlastFurnace)
        {
            var progress = scenario.ProgressAt(timestamp);
            value += DegradationDelta(profile.Metric, progress);
            quality = progress switch
            {
                >= 0.85 => Quality.Bad,
                >= 0.40 => Quality.Suspect,
                _ => quality
            };
        }

        value = Math.Clamp(value, profile.Minimum, profile.Maximum);
        return new TelemetryReading(
            asset.AssetId,
            asset.AssetType,
            asset.Site,
            profile.Metric,
            Math.Round(value, 3, MidpointRounding.AwayFromZero),
            profile.Unit,
            timestamp,
            quality,
            Origin.Synthetic,
            _options.SourceIdFor(asset.AssetId));
    }

    private static double DegradationDelta(Metric metric, double progress) => metric switch
    {
        Metric.ThermocoupleTemp => (140 * progress) + (20 * progress * progress),
        Metric.HeatFlux => (85 * progress) + (15 * progress * progress),
        Metric.Vibration => (8 * progress) + (2 * progress * progress),
        Metric.PowerDrawKw => 900 * progress,
        _ => 0
    };

    private static Random CreateDeterministicRandom(int seed, string assetId, Metric metric, int stepIndex)
    {
        var value = StableHash($"{seed}:{assetId}:{metric}:{stepIndex}");
        return new Random(unchecked((int)(value & 0x7fffffff)));
    }

    private static double StableUnitInterval(string left, string right)
    {
        var hash = StableHash($"{left}:{right}");
        return (hash % 100000) / 100000.0;
    }

    private static ulong StableHash(string value)
    {
        var bytes = SHA256.HashData(Encoding.UTF8.GetBytes(value));
        return BitConverter.ToUInt64(bytes, 0);
    }
}

public static class SimulatorOptionsExtensions
{
    public static string SourceIdFor(this SimulatorOptions options, string assetId) =>
        string.IsNullOrWhiteSpace(options.SourceId)
            ? $"sim:{assetId}"
            : options.SourceId;
}
