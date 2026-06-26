namespace NovaSteel.Contracts;

/// <summary>Type of plant asset emitting telemetry.</summary>
public enum AssetType { Unknown = 0, BlastFurnace, RollingMill, Utility }

/// <summary>NovaSteel operating site (country code).</summary>
public enum Site { LU = 0, DE, BE, ES }

/// <summary>Data-quality tag carried with every reading for auditability.</summary>
public enum Quality { Good = 0, Suspect, Bad }

/// <summary>Measured signal type.</summary>
public enum Metric { Unknown = 0, ThermocoupleTemp, HeatFlux, Vibration, Throughput, PowerDrawKw }

/// <summary>Telemetry provenance marker preserved end-to-end.</summary>
public enum Origin { Real = 0, Synthetic }

/// <summary>Prediction pillar that produced a model output.</summary>
public enum Pillar { Maintenance = 0, Quality }

/// <summary>Type of prediction raised by a model.</summary>
public enum PredictionKind { LiningFailureRisk = 0, QualityOutcome, SpcDrift }

/// <summary>Human-review lifecycle state for a prediction.</summary>
public enum PredictionStatus { Raised = 0, UnderReview, Confirmed, Rejected, Lapsed }

/// <summary>Recommendation pillar that produced a proposed action.</summary>
public enum RecommendationPillar { Maintenance = 0, Quality, Knowledge }

/// <summary>Human-review lifecycle state for a recommendation.</summary>
public enum RecommendationStatus { Proposed = 0, UnderReview, Approved, Edited, Rejected, Lapsed }

/// <summary>Energy-dispatch solver engine.</summary>
public enum Solver { Milp = 0, Heuristic }

/// <summary>Human-review lifecycle state for an energy plan.</summary>
public enum EnergyPlanStatus { Proposed = 0, UnderReview, Approved, Adjusted, Rejected, Lapsed }

/// <summary>Type of subject reviewed by a human decision.</summary>
public enum DecisionSubjectType { Prediction = 0, Recommendation, EnergyPlan }

/// <summary>Human decision made about a review subject.</summary>
public enum DecisionType { Confirm = 0, Edit, Reject }

/// <summary>Authorized reviewer persona role.</summary>
public enum ReviewerRole { Operator = 0, Maintenance, Energy, Quality, ExecutiveEsg, ComplianceDpo }

/// <summary>Type of subject captured in an immutable audit record.</summary>
public enum AuditSubjectType { Prediction = 0, Recommendation, EnergyPlan, HumanDecision, WorkOrder, KnowledgeItem }

/// <summary>Audit retention classification.</summary>
public enum RetentionClass { PredictionDecisionAudit = 0, EnergyEts }

/// <summary>Enum parsing that never throws: unknown values map to a caller-supplied fallback.</summary>
public static class EnumParse
{
    public static T OrFallback<T>(string? value, T fallback) where T : struct, Enum
        => Enum.TryParse<T>(value, ignoreCase: true, out var parsed) ? parsed : fallback;
}
