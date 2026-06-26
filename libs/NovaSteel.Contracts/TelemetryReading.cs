namespace NovaSteel.Contracts;

/// <summary>Canonical telemetry envelope. Shared verbatim across every sub-project.</summary>
public readonly record struct TelemetryReading(
    string AssetId,
    AssetType AssetType,
    Site Site,
    Metric Metric,
    double Value,
    string Unit,
    DateTimeOffset Timestamp,
    Quality Quality,
    Origin Origin = Origin.Real,
    string SourceId = "")
{
    private readonly string? _sourceId = SourceId;

    public string SourceId
    {
        get => _sourceId ?? "";
        init => _sourceId = value;
    }
}
