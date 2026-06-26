using NovaSteel.Contracts;

namespace SteelFactorySimulator.Simulation;

public sealed record AssetDefinition(string AssetId, AssetType AssetType, Site Site, IReadOnlyList<MetricProfile> Metrics);

public sealed record MetricProfile(
    Metric Metric,
    string Unit,
    double Baseline,
    double CycleAmplitude,
    double NoiseAmplitude,
    double DriftPerDay,
    double Minimum,
    double Maximum);
