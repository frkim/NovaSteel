"""Human-review and immutable audit support for P2 energy plans (Constitution I/II).

An energy manager reviews each ``Proposed`` plan and Approves / Adjusts / Rejects it.
No plan ever actuates furnace or grid equipment; approval only records intent and yields
an immutable, EU-ETS-retained audit trail.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid4, uuid5

from novasteel_core.models import (
    AuditRecord,
    AuditSubjectType,
    DecisionSubjectType,
    DecisionType,
    EnergyPlan,
    HumanDecision,
    Origin,
    RetentionClass,
    ReviewerRole,
)
from novasteel_core.audit import AuditLog

LOGIC_VERSION = "p2-human-review-v1"


def _now(decided_at: datetime | None = None) -> datetime:
    if decided_at is None:
        return datetime.now(timezone.utc)
    return decided_at if decided_at.tzinfo else decided_at.replace(tzinfo=timezone.utc)


def audit_energy_plan_proposed(plan: EnergyPlan, audit_log: AuditLog) -> AuditRecord:
    """Append the immutable audit entry for a proposed energy plan."""
    record = AuditRecord(
        audit_id=str(uuid5(NAMESPACE_URL, f"audit:{plan.energy_plan_id}:proposed")),
        subject_type=AuditSubjectType.EnergyPlan,
        subject_id=plan.energy_plan_id,
        site=plan.site,
        action="EnergyPlanProposed",
        inputs_ref=[j.job_id for j in plan.scheduled_jobs],
        model_or_logic_version=LOGIC_VERSION,
        output=plan.model_dump(by_alias=True, mode="json"),
        reviewer_id=None,
        rationale="Energy plan proposed for human review; no automatic grid/furnace actuation.",
        timestamp=plan.planning_horizon.from_,
        origin=plan.origin,
        retention_class=RetentionClass.EnergyEts,
    )
    audit_log.append(record)
    return record


def record_energy_decision(
    plan: EnergyPlan,
    *,
    decision: DecisionType,
    reviewer_id: str,
    rationale: str,
    audit_log: AuditLog,
    decided_at: datetime | None = None,
) -> HumanDecision:
    """Record an approve/adjust/reject decision and append the traceability audit entry."""
    decided_at = _now(decided_at)
    decision_id = str(uuid4())
    human_decision = HumanDecision(
        decision_id=decision_id,
        subject_type=DecisionSubjectType.EnergyPlan,
        subject_id=plan.energy_plan_id,
        site=plan.site,
        decision=decision,
        reviewer_id=reviewer_id,
        reviewer_role=ReviewerRole.Energy,
        rationale=rationale,
        decided_at=decided_at,
    )
    action = {
        DecisionType.Confirm: "EnergyPlanApproved",
        DecisionType.Edit: "EnergyPlanAdjusted",
        DecisionType.Reject: "EnergyPlanRejected",
    }[decision]
    audit_log.append(AuditRecord(
        audit_id=str(uuid4()),
        subject_type=AuditSubjectType.HumanDecision,
        subject_id=decision_id,
        site=plan.site,
        action=action,
        inputs_ref=[plan.energy_plan_id],
        model_or_logic_version=LOGIC_VERSION,
        output={
            "humanDecision": human_decision.model_dump(by_alias=True, mode="json"),
            "energyPlan": plan.model_dump(by_alias=True, mode="json"),
            "noAutomaticActuation": True,
        },
        reviewer_id=reviewer_id,
        rationale=rationale,
        timestamp=decided_at,
        origin=Origin.Synthetic if plan.origin == Origin.Synthetic else Origin.Real,
        retention_class=RetentionClass.EnergyEts,
    ))
    return human_decision
