namespace SteelFactorySimulator.Options;

/// <summary>Identifies the Microsoft Fabric capacity the Settings page can pause/resume.</summary>
public sealed class FabricOptions
{
    public string SubscriptionId { get; set; } = "";
    public string ResourceGroup { get; set; } = "";
    public string CapacityName { get; set; } = "";
    public string ApiVersion { get; set; } = "2023-11-01";

    public bool IsConfigured =>
        SubscriptionId.Length > 0 && ResourceGroup.Length > 0 && CapacityName.Length > 0;

    public string ResourceId =>
        $"/subscriptions/{SubscriptionId}/resourceGroups/{ResourceGroup}" +
        $"/providers/Microsoft.Fabric/capacities/{CapacityName}";
}
