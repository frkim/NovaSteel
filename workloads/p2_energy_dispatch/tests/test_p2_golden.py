from __future__ import annotations

import json
import pathlib

from novasteel_core.models import EnergyPlan
from workloads.p2_energy_dispatch.dispatch_model import build_energy_plan
from workloads.p2_energy_dispatch.generate_energy_scenario import generate_energy_scenario

GOLDEN = pathlib.Path(__file__).resolve().parents[3] / "libs" / "fixtures" / "p2_energy_plan_golden.json"


def test_energy_plan_matches_golden_fixture() -> None:
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    # Golden round-trips through the shared contract (camelCase parity).
    parsed = EnergyPlan.model_validate(golden)
    assert parsed.status.value == "Proposed"

    s = generate_energy_scenario()
    fresh = build_energy_plan(s.jobs, s.market, base_time=s.base_time).model_dump(by_alias=True, mode="json")
    # Deterministic (uuid5 + rounded floats): the model must keep producing the golden output.
    assert fresh == golden
