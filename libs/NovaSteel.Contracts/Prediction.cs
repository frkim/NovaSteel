using System.Text.Json.Serialization;

namespace NovaSteel.Contracts;

/// <summary>Contributing signal explaining why a prediction was raised.</summary>
public readonly record struct EvidenceItem
{
    private readonly string? _metric;
    private readonly string? _note;

    public string Metric
    {
        get => _metric ?? "";
        init => _metric = value;
    }

    public double Value { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public double? Weight { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? Note
    {
        get => _note;
        init => _note = value;
    }
}

/// <summary>Model output with confidence, evidence, model version, and review status.</summary>
public readonly record struct Prediction
{
    private readonly string? _predictionId;
    private readonly EvidenceItem[]? _evidence;
    private readonly string? _modelVersion;
    private readonly string? _inputWindowRef;

    public Prediction()
    {
    }

    public string PredictionId
    {
        get => _predictionId ?? "";
        init => _predictionId = value;
    }

    public Pillar Pillar { get; init; }

    public Site Site { get; init; }

    public string? AssetId { get; init; }

    public string? HeatId { get; init; }

    public PredictionKind Kind { get; init; }

    public double? TimeToFailureDays { get; init; }

    public DateTimeOffset PredictedAt { get; init; }

    public double Confidence { get; init; }

    public EvidenceItem[] Evidence
    {
        get => _evidence ?? Array.Empty<EvidenceItem>();
        init => _evidence = value;
    }

    public string ModelVersion
    {
        get => _modelVersion ?? "";
        init => _modelVersion = value;
    }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? InputWindowRef
    {
        get => _inputWindowRef;
        init => _inputWindowRef = value;
    }

    public Origin Origin { get; init; } = Origin.Real;

    public PredictionStatus Status { get; init; }
}
