from __future__ import annotations

import pathlib
import sys
from datetime import datetime, timezone

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "platform"))

from governance.eu_ets import EmissionRecord, compute_ets_report  # noqa: E402


def _rec(rid, site, year, scope, tco2, origin="Real", verified=True):
    return EmissionRecord(rid, site, datetime(year, 6, 1, tzinfo=timezone.utc), scope, tco2, origin, verified)


def test_verified_real_emissions_only_count() -> None:
    records = [
        _rec("r1", "DE", 2026, "DirectCombustion", 1000.0),
        _rec("r2", "DE", 2026, "ProcessEmissions", 400.0),
        _rec("r3", "DE", 2026, "DirectCombustion", 50.0, origin="Synthetic"),   # excluded
        _rec("r4", "DE", 2026, "DirectCombustion", 30.0, verified=False),        # unverified
        _rec("r5", "LU", 2026, "DirectCombustion", 999.0),                       # other site
        _rec("r6", "DE", 2025, "DirectCombustion", 999.0),                       # other year
    ]
    report = compute_ets_report(records, site="DE", year=2026, installation_id="INST-DE-01")
    assert report.verified_tco2 == 1400.0
    assert report.unverified_tco2 == 30.0
    assert report.synthetic_excluded_tco2 == 50.0
    assert report.by_scope == {"DirectCombustion": 1000.0, "ProcessEmissions": 400.0}
    assert set(report.record_ids) == {"r1", "r2"}


def test_report_dict_shape() -> None:
    report = compute_ets_report([_rec("r1", "DE", 2026, "DirectCombustion", 1234.5)],
                                site="DE", year=2026, installation_id="INST-DE-01")
    d = report.to_dict()
    assert d["installationId"] == "INST-DE-01"
    assert d["verifiedTco2"] == 1234.5
    assert d["byScope"]["DirectCombustion"] == 1234.5
    assert d["recordCount"] == 1


def test_empty_is_zero_not_error() -> None:
    report = compute_ets_report([], site="ES", year=2026, installation_id="INST-ES-01")
    assert report.verified_tco2 == 0.0
    assert report.record_ids == []
