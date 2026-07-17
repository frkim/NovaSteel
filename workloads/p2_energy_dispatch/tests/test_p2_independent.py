from __future__ import annotations

from datetime import datetime, timezone

import pytest
from novasteel_core.audit import AuditLog, ImmutableAuditError
from novasteel_core.models import (
    AuditSubjectType,
    DecisionType,
    EnergyPlanStatus,
    Origin,
    RetentionClass,
    Solver,
)

from workloads.p2_energy_dispatch.decision_service import (
    audit_energy_plan_proposed,
    record_energy_decision,
)
from workloads.p2_energy_dispatch.dispatch_model import (
    Job,
    baseline_dispatch,
    build_energy_plan,
    co2_savings_pct,
    cost_savings_pct,
    energy_savings_pct,
    optimize_dispatch,
)
from workloads.p2_energy_dispatch.generate_energy_scenario import generate_energy_scenario

# Success-criteria targets (spec SC-001/SC-002).
ENERGY_TARGET_PCT = 14.0
CO2_TARGET_PCT = 22.0


def _scenario():
    s = generate_energy_scenario()
    return s


def test_optimizer_meets_energy_and_co2_targets() -> None:
    s = _scenario()
    baseline = baseline_dispatch(s.jobs, s.market)
    optimized = optimize_dispatch(s.jobs, s.market)

    assert energy_savings_pct(baseline, optimized) >= ENERGY_TARGET_PCT
    assert co2_savings_pct(baseline, optimized) >= CO2_TARGET_PCT
    assert cost_savings_pct(baseline, optimized) > 0.0
    # Optimized never uses MORE energy/CO2/cost than the naive baseline.
    assert optimized.energy_mwh <= baseline.energy_mwh
    assert optimized.co2_kg <= baseline.co2_kg


def test_optimized_campaign_respects_readiness_and_deadlines() -> None:
    s = _scenario()
    optimized = optimize_dispatch(s.jobs, s.market)
    assert not optimized.deadline_breaches
    for p in optimized.placements:
        assert p.start_slot >= p.job.ready_slot  # never starts before charge is ready
        assert p.start_slot + p.job.duration_slots <= p.job.deadline_slot + 1  # meets deadline
    # Back-to-back campaign on a single furnace pays exactly one warm-up.
    warmups = sum(1 for p in optimized.placements if p.warmup)
    assert warmups == 1


def test_infeasible_deadline_is_flagged_not_forced() -> None:
    # Deadline before the charge is even ready -> infeasible; must be flagged, never silently
    # dropped or actuated.
    jobs = [Job(job_id="HEAT-X", furnace_id="LU-EAF1", site="LU", tons=150.0,
                production_mwh=20.0, duration_slots=2, ready_slot=20, deadline_slot=10,
                origin=Origin.Synthetic)]
    s = _scenario()
    result = optimize_dispatch(jobs, s.market)
    assert "LU-EAF1" in result.deadline_breaches


def test_energy_plan_contract_shape_and_human_in_the_loop() -> None:
    s = _scenario()
    plan = build_energy_plan(s.jobs, s.market, base_time=s.base_time)

    assert plan.status == EnergyPlanStatus.Proposed  # never auto-approved
    assert plan.solver == Solver.Heuristic
    assert plan.origin == Origin.Synthetic
    assert plan.expected_energy_per_ton < plan.baseline_comparison.baseline_energy_per_ton
    assert plan.expected_co2_per_ton < plan.baseline_comparison.baseline_co2_per_ton
    assert plan.expected_cost_eur < plan.baseline_comparison.baseline_cost_eur
    assert len(plan.scheduled_jobs) == len(s.jobs)

    payload = plan.model_dump(by_alias=True, mode="json")
    assert payload["status"] == "Proposed"
    assert payload["planningHorizon"]["from"]
    assert payload["baselineComparison"]["baselineEnergyPerTon"] > 0
    assert payload["scheduledJobs"][0]["energyMwh"] > 0


def test_proposed_plan_audit_and_decision_flow_is_immutable() -> None:
    s = _scenario()
    plan = build_energy_plan(s.jobs, s.market, base_time=s.base_time)
    log = AuditLog()

    proposed = audit_energy_plan_proposed(plan, log)
    assert proposed.subject_type == AuditSubjectType.EnergyPlan
    assert proposed.retention_class == RetentionClass.EnergyEts
    assert proposed.origin == Origin.Synthetic

    decision = record_energy_decision(
        plan,
        decision=DecisionType.Confirm,
        reviewer_id="energy-manager-01",
        rationale="Overnight batch approved; deadlines and furnace limits satisfied.",
        audit_log=log,
        decided_at=datetime(2026, 3, 2, 7, 0, tzinfo=timezone.utc),
    )
    assert decision.decision == DecisionType.Confirm
    assert len(log) == 2
    decision_audit = log.entries[-1]
    assert decision_audit.subject_type == AuditSubjectType.HumanDecision
    assert decision_audit.action == "EnergyPlanApproved"
    assert decision_audit.output["noAutomaticActuation"] is True

    with pytest.raises(ImmutableAuditError):
        log.pop()
    with pytest.raises(ImmutableAuditError):
        del log[0]
