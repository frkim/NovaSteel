namespace NovaSteel.Contracts;

/// <summary>Human review decision for a prediction, recommendation, or energy plan.</summary>
public readonly record struct HumanDecision
{
    private readonly string? _decisionId;
    private readonly string? _subjectId;
    private readonly string? _reviewerId;
    private readonly string? _rationale;

    public string DecisionId
    {
        get => _decisionId ?? "";
        init => _decisionId = value;
    }

    public DecisionSubjectType SubjectType { get; init; }

    public string SubjectId
    {
        get => _subjectId ?? "";
        init => _subjectId = value;
    }

    public Site Site { get; init; }

    public DecisionType Decision { get; init; }

    public string ReviewerId
    {
        get => _reviewerId ?? "";
        init => _reviewerId = value;
    }

    public ReviewerRole ReviewerRole { get; init; }

    public string? Rationale
    {
        get => _rationale;
        init => _rationale = value;
    }

    public DateTimeOffset DecidedAt { get; init; }

    public string? ResultingWorkOrderId { get; init; }
}
