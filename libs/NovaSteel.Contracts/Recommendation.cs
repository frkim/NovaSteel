using System.Text.Json.Nodes;
using System.Text.Json.Serialization;

namespace NovaSteel.Contracts;

/// <summary>Source citation for grounded knowledge recommendations.</summary>
public readonly record struct Citation
{
    private readonly string? _sourceId;
    private readonly string? _title;
    private readonly string? _locator;

    public string SourceId
    {
        get => _sourceId ?? "";
        init => _sourceId = value;
    }

    public string Title
    {
        get => _title ?? "";
        init => _title = value;
    }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? Locator
    {
        get => _locator;
        init => _locator = value;
    }
}

/// <summary>Proposed action with rationale, expected impact, review status, and optional citations.</summary>
public readonly record struct Recommendation
{
    private readonly string? _recommendationId;
    private readonly string? _summary;
    private readonly string? _rationale;
    private readonly string[]? _conflictsWith;

    public Recommendation()
    {
    }

    public string RecommendationId
    {
        get => _recommendationId ?? "";
        init => _recommendationId = value;
    }

    public RecommendationPillar Pillar { get; init; }

    public Site Site { get; init; }

    public string? RelatedPredictionId { get; init; }

    public string? RelatedHeatId { get; init; }

    public string Summary
    {
        get => _summary ?? "";
        init => _summary = value;
    }

    public string Rationale
    {
        get => _rationale ?? "";
        init => _rationale = value;
    }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public JsonObject? ExpectedImpact { get; init; }

    public Citation[]? Citations { get; init; }

    public double? Confidence { get; init; }

    public bool ContentSafetyPassed { get; init; } = true;

    public string[]? ConflictsWith
    {
        get => _conflictsWith;
        init => _conflictsWith = value;
    }

    public RecommendationStatus Status { get; init; }
}
