using NovaSteel.Contracts;

namespace SteelFactorySimulator.Simulation;

public static class AssetCatalog
{
    public static IReadOnlyList<AssetDefinition> DefaultAssets { get; } = BuildAssets();

    private static IReadOnlyList<AssetDefinition> BuildAssets()
    {
        var assets = new List<AssetDefinition>();
        foreach (var site in new[] { Site.LU, Site.DE, Site.BE, Site.ES })
        {
            var prefix = site.ToString();
            assets.Add(BlastFurnace($"{prefix}-BF1", site));
            assets.Add(BlastFurnace($"{prefix}-BF2", site));
            assets.Add(RollingMill($"{prefix}-RM1", site));
            assets.Add(RollingMill($"{prefix}-RM2", site));
            assets.Add(Utility($"{prefix}-UTL1", site));
        }

        return assets;
    }

    private static AssetDefinition BlastFurnace(string assetId, Site site) => new(assetId, AssetType.BlastFurnace, site,
    [
        new(Metric.ThermocoupleTemp, "C", 1435, 8, 1.2, 0.01, 1350, 1700),
        new(Metric.HeatFlux, "kW/m2", 42, 1.5, 0.4, 0.005, 25, 160),
        new(Metric.Vibration, "mm/s", 2.2, 0.25, 0.08, 0.001, 0.4, 20),
        new(Metric.PowerDrawKw, "kW", 18500, 600, 80, 0.2, 15000, 23000)
    ]);

    private static AssetDefinition RollingMill(string assetId, Site site) => new(assetId, AssetType.RollingMill, site,
    [
        new(Metric.Vibration, "mm/s", 3.1, 0.35, 0.12, 0.001, 0.5, 18),
        new(Metric.Throughput, "t/h", 225, 18, 3.5, 0.01, 120, 330),
        new(Metric.PowerDrawKw, "kW", 9400, 450, 70, 0.1, 6500, 13000)
    ]);

    private static AssetDefinition Utility(string assetId, Site site) => new(assetId, AssetType.Utility, site,
    [
        new(Metric.PowerDrawKw, "kW", 4200, 350, 45, 0.05, 2500, 6800),
        new(Metric.Throughput, "t/h", 95, 8, 1.6, 0.002, 55, 140),
        new(Metric.Vibration, "mm/s", 1.1, 0.15, 0.05, 0, 0.2, 8)
    ]);
}
