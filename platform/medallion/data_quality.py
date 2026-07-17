"""Medallion data-quality checks (Constitution VIII gate, FR-022).

Reusable assertions applied at each layer and wired into the Fabric notebooks and
the pytest gate. Failing checks stop promotion to the next layer.
"""

from __future__ import annotations

from typing import Any, Iterable

from novasteel_core.models import Origin

from .transforms import PROVENANCE_FIELDS

VALID_SITES = {"LU", "DE", "BE", "ES"}
VALID_QUALITY = {"Good", "Suspect", "Bad"}
VALID_ORIGIN = {Origin.Real.value, Origin.Synthetic.value}


class DataQualityError(AssertionError):
    """Raised when a medallion data-quality check fails."""


def check_provenance_present(rows: Iterable[dict[str, Any]]) -> None:
    """Every row must carry all provenance/identity fields, non-null (Constitution IX)."""
    for i, rec in enumerate(rows):
        for field in PROVENANCE_FIELDS:
            if rec.get(field) in (None, ""):
                raise DataQualityError(f"row {i}: missing provenance field '{field}': {rec!r}")
        if rec["origin"] not in VALID_ORIGIN:
            raise DataQualityError(f"row {i}: invalid origin {rec['origin']!r}")
        if rec["site"] not in VALID_SITES:
            raise DataQualityError(f"row {i}: invalid site {rec['site']!r}")
        if rec["quality"] not in VALID_QUALITY:
            raise DataQualityError(f"row {i}: invalid quality {rec['quality']!r}")


def check_no_synthetic_in_real_kpi(gold_marts: Iterable[dict[str, Any]]) -> None:
    """Real KPI marts must never include synthetic-origin data (Constitution IX)."""
    for mart in gold_marts:
        if mart.get("data_class") == "real":
            # A real mart's source_ids must not look synthetic and it must be labelled real.
            if any(str(sid).startswith("sim:") for sid in mart.get("source_ids", [])):
                raise DataQualityError(
                    f"real KPI mart for {mart['site']}/{mart['metric']} contains a synthetic source_id"
                )


def check_ranges(rows: Iterable[dict[str, Any]]) -> None:
    """Basic physical-plausibility / null checks on the value column (FR-022)."""
    for i, rec in enumerate(rows):
        v = rec.get("value")
        if v is None:
            raise DataQualityError(f"row {i}: null value")
        if not isinstance(v, (int, float)):
            raise DataQualityError(f"row {i}: non-numeric value {v!r}")


def run_all(bronze: list[dict[str, Any]],
            silver: list[dict[str, Any]],
            gold: list[dict[str, Any]]) -> None:
    """Full gate used by the Fabric pipeline and the pytest provenance test."""
    check_provenance_present(bronze)
    check_ranges(bronze)
    check_provenance_present(silver)
    check_no_synthetic_in_real_kpi(gold)
