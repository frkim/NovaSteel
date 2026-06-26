using System.Text.Json.Nodes;

namespace NovaSteel.Contracts;

/// <summary>Immutable traceability entry for predictions, recommendations, plans, and decisions.</summary>
public readonly record struct AuditRecord
{
    private readonly string? _auditId;
    private readonly string? _subjectId;
    private readonly string? _action;
    private readonly string[]? _inputsRef;
    private readonly string? _modelOrLogicVersion;

    public AuditRecord()
    {
    }

    public string AuditId
    {
        get => _auditId ?? "";
        init => _auditId = value;
    }

    public AuditSubjectType SubjectType { get; init; }

    public string SubjectId
    {
        get => _subjectId ?? "";
        init => _subjectId = value;
    }

    public Site Site { get; init; }

    public string Action
    {
        get => _action ?? "";
        init => _action = value;
    }

    public string[] InputsRef
    {
        get => _inputsRef ?? Array.Empty<string>();
        init => _inputsRef = value;
    }

    public string ModelOrLogicVersion
    {
        get => _modelOrLogicVersion ?? "";
        init => _modelOrLogicVersion = value;
    }

    public JsonObject Output { get; init; } = new();

    public string? ReviewerId { get; init; }

    public string? Rationale { get; init; }

    public DateTimeOffset Timestamp { get; init; }

    public Origin Origin { get; init; } = Origin.Real;

    public RetentionClass RetentionClass { get; init; }
}
