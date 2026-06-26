namespace SteelFactorySimulator.Options;

public sealed class IotHubOptions
{
    public string DeviceId { get; set; } = "sim-steel-factory-simulator";
    public string? ConnectionString { get; set; }
    public string? KeyVaultUri { get; set; }
    public string? ConnectionStringSecretName { get; set; }
    public int BatchSize { get; set; } = 50;
    public int FlushIntervalSeconds { get; set; } = 5;
}
