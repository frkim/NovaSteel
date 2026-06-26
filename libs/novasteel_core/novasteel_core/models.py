"""Pydantic v2 models mirroring NovaSteel.Contracts (camelCase JSON parity)."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class _CamelModel(BaseModel):
    """Base model: serialise/parse using camelCase aliases, accept field names too."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class Origin(StrEnum):
    """Telemetry provenance marker preserved end-to-end."""

    Real = "Real"
    Synthetic = "Synthetic"


class Pillar(StrEnum):
    """Prediction pillar that produced a model output."""

    Maintenance = "Maintenance"
    Quality = "Quality"


class PredictionKind(StrEnum):
    """Type of prediction raised by a model."""

    LiningFailureRisk = "LiningFailureRisk"
    QualityOutcome = "QualityOutcome"
    SpcDrift = "SpcDrift"


class PredictionStatus(StrEnum):
    """Human-review lifecycle state for a prediction."""

    Raised = "Raised"
    UnderReview = "UnderReview"
    Confirmed = "Confirmed"
    Rejected = "Rejected"
    Lapsed = "Lapsed"


class RecommendationPillar(StrEnum):
    """Recommendation pillar that produced a proposed action."""

    Maintenance = "Maintenance"
    Quality = "Quality"
    Knowledge = "Knowledge"


class RecommendationStatus(StrEnum):
    """Human-review lifecycle state for a recommendation."""

    Proposed = "Proposed"
    UnderReview = "UnderReview"
    Approved = "Approved"
    Edited = "Edited"
    Rejected = "Rejected"
    Lapsed = "Lapsed"


class Solver(StrEnum):
    """Energy-dispatch solver engine."""

    Milp = "Milp"
    Heuristic = "Heuristic"


class EnergyPlanStatus(StrEnum):
    """Human-review lifecycle state for an energy plan."""

    Proposed = "Proposed"
    UnderReview = "UnderReview"
    Approved = "Approved"
    Adjusted = "Adjusted"
    Rejected = "Rejected"
    Lapsed = "Lapsed"


class DecisionSubjectType(StrEnum):
    """Type of subject reviewed by a human decision."""

    Prediction = "Prediction"
    Recommendation = "Recommendation"
    EnergyPlan = "EnergyPlan"


class DecisionType(StrEnum):
    """Human decision made about a review subject."""

    Confirm = "Confirm"
    Edit = "Edit"
    Reject = "Reject"


class ReviewerRole(StrEnum):
    """Authorized reviewer persona role."""

    Operator = "Operator"
    Maintenance = "Maintenance"
    Energy = "Energy"
    Quality = "Quality"
    ExecutiveEsg = "ExecutiveEsg"
    ComplianceDpo = "ComplianceDpo"


class AuditSubjectType(StrEnum):
    """Type of subject captured in an immutable audit record."""

    Prediction = "Prediction"
    Recommendation = "Recommendation"
    EnergyPlan = "EnergyPlan"
    HumanDecision = "HumanDecision"
    WorkOrder = "WorkOrder"
    KnowledgeItem = "KnowledgeItem"


class RetentionClass(StrEnum):
    """Audit retention classification."""

    PredictionDecisionAudit = "PredictionDecisionAudit"
    EnergyEts = "EnergyEts"


class TelemetryReading(_CamelModel):
    asset_id: str
    asset_type: str
    site: str
    metric: str
    value: float
    unit: str
    timestamp: datetime
    quality: str
    origin: Origin = Origin.Real
    source_id: str = ""


class MarketSignal(_CamelModel):
    market: str
    timestamp: datetime
    spot_price_eur_mwh: float
    grid_carbon_grams_per_kwh: float


class EvidenceItem(_CamelModel):
    metric: str
    value: float
    weight: float | None = None
    note: str | None = None


class Prediction(_CamelModel):
    prediction_id: str
    pillar: Pillar
    site: str
    asset_id: str | None = None
    heat_id: str | None = None
    kind: PredictionKind
    time_to_failure_days: float | None = None
    predicted_at: datetime
    confidence: float
    evidence: list[EvidenceItem]
    model_version: str
    input_window_ref: str | None = None
    origin: Origin = Origin.Real
    status: PredictionStatus


class Citation(_CamelModel):
    source_id: str
    title: str
    locator: str | None = None


class Recommendation(_CamelModel):
    recommendation_id: str
    pillar: RecommendationPillar
    site: str
    related_prediction_id: str | None = None
    related_heat_id: str | None = None
    summary: str
    rationale: str
    expected_impact: dict[str, Any] | None = None
    citations: list[Citation] | None = None
    confidence: float | None = None
    content_safety_passed: bool = True
    conflicts_with: list[str] | None = None
    status: RecommendationStatus


class PlanningHorizon(_CamelModel):
    from_: datetime = Field(alias="from")
    to: datetime


class ScheduledJob(_CamelModel):
    job_id: str
    slot_start: datetime
    slot_end: datetime
    deadline: datetime | None = None
    energy_mwh: float


class BaselineComparison(_CamelModel):
    baseline_energy_per_ton: float
    baseline_co2_per_ton: float
    baseline_cost_eur: float


class EnergyPlan(_CamelModel):
    energy_plan_id: str
    site: str
    planning_horizon: PlanningHorizon
    scheduled_jobs: list[ScheduledJob]
    expected_energy_per_ton: float
    expected_co2_per_ton: float
    expected_cost_eur: float
    baseline_comparison: BaselineComparison
    deadline_breaches: list[str] = Field(default_factory=list)
    solver: Solver
    origin: Origin = Origin.Real
    status: EnergyPlanStatus


class HumanDecision(_CamelModel):
    decision_id: str
    subject_type: DecisionSubjectType
    subject_id: str
    site: str
    decision: DecisionType
    reviewer_id: str
    reviewer_role: ReviewerRole
    rationale: str | None = None
    decided_at: datetime
    resulting_work_order_id: str | None = None


class AuditRecord(_CamelModel):
    audit_id: str
    subject_type: AuditSubjectType
    subject_id: str
    site: str
    action: str
    inputs_ref: list[str]
    model_or_logic_version: str
    output: dict[str, Any]
    reviewer_id: str | None = None
    rationale: str | None = None
    timestamp: datetime
    origin: Origin = Origin.Real
    retention_class: RetentionClass
