"""Deterministic synthetic quality scenario for automotive-grade heats (Constitution IX).

Each heat carries process features (tapping temperature, sulphur, inclusion cleanliness) and a
ground-truth high-grade outcome derived from an explicit spec. A subset of heats drift out of
spec; some are recoverable by a reviewable process adjustment, some are not. A separate temp
stream drifts upward late in the campaign to exercise SPC detection.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from novasteel_core.models import Origin

BASE_TIME = datetime(2026, 4, 6, 6, 0, tzinfo=timezone.utc)
GRADE_TARGET = "AutoDP800"

# High-grade spec (automotive dual-phase 800): all must hold.
SULFUR_MAX_PCT = 0.010
INCLUSION_MAX = 2.0
TAPPING_MIN_C = 1630.0
TAPPING_MAX_C = 1670.0


@dataclass(frozen=True)
class Heat:
    heat_id: str
    site: str
    grade_target: str
    sequence: int
    tapping_temp_c: float
    sulfur_pct: float
    inclusion_index: float
    actual_high_grade: bool
    origin: Origin = Origin.Synthetic


def _is_high_grade(sulfur_pct: float, inclusion_index: float, tapping_temp_c: float) -> bool:
    return (
        sulfur_pct <= SULFUR_MAX_PCT
        and inclusion_index <= INCLUSION_MAX
        and TAPPING_MIN_C <= tapping_temp_c <= TAPPING_MAX_C
    )


def generate_quality_scenario(
    *,
    site: str = "DE",
    heats: int = 20,
    seed: int = 23,
) -> list[Heat]:
    """Build a deterministic batch of heats with a mix of in-spec and drifted outcomes.

    Roughly 70% are high-grade; the remainder drift on sulphur/inclusion (recoverable) or on
    tapping temperature (some far out-of-band = non-recoverable). Heats 15+ add an upward
    temperature drift for SPC testing.
    """
    rng = random.Random(seed)
    out: list[Heat] = []
    for i in range(heats):
        # Baseline in-spec process.
        sulfur = 0.006 + 0.001 * math.sin(i)
        inclusion = 1.4 + 0.2 * math.sin(i * 1.7)
        temp = 1650.0 + 4.0 * math.sin(i * 0.9)

        # Inject recoverable sulphur/inclusion excursions on selected heats.
        if i in (3, 7, 11, 16):
            sulfur = 0.014 + 0.001 * rng.random()   # over 0.010, recoverable by desulphurization
            inclusion = 2.6 + 0.1 * rng.random()    # over 2.0, recoverable by stirring
        # Inject a non-recoverable severe cleanliness excursion (no in-run reviewable fix).
        if i in (9,):
            inclusion = 4.0  # far above 2.0 and beyond the recoverable range

        # Late-campaign upward temperature drift for SPC (temperature stays in-band earlier).
        if i >= 15:
            temp += 6.0 * (i - 14)

        high_grade = _is_high_grade(sulfur, inclusion, temp)
        out.append(Heat(
            heat_id=f"HEAT-{site}-{i + 1:03d}",
            site=site,
            grade_target=GRADE_TARGET,
            sequence=i,
            tapping_temp_c=round(temp, 3),
            sulfur_pct=round(sulfur, 5),
            inclusion_index=round(inclusion, 3),
            actual_high_grade=high_grade,
            origin=Origin.Synthetic,
        ))
    return out


def heat_timestamp(heat: Heat) -> datetime:
    return BASE_TIME + timedelta(hours=heat.sequence)
