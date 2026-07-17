"""Statistical process control (SPC) — 3-sigma limits + Western Electric drift rules.

Dependency-free control-chart maths for detecting when a process metric (e.g. tapping
temperature) drifts out of statistical control. Detection is decision-support: it raises a
reviewable SPC-drift signal; it never adjusts the process.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ControlLimits:
    mean: float
    sigma: float

    @property
    def ucl(self) -> float:  # upper control limit (3-sigma)
        return self.mean + 3.0 * self.sigma

    @property
    def lcl(self) -> float:  # lower control limit (3-sigma)
        return self.mean - 3.0 * self.sigma


@dataclass(frozen=True)
class Violation:
    index: int
    value: float
    rule: str  # e.g. "3-sigma" or "2of3-2sigma"


def control_limits(in_control: list[float]) -> ControlLimits:
    """Compute mean and (population) sigma from an in-control reference window."""
    if len(in_control) < 2:
        raise ValueError("need at least two in-control points")
    mean = sum(in_control) / len(in_control)
    var = sum((x - mean) ** 2 for x in in_control) / len(in_control)
    return ControlLimits(mean=mean, sigma=var ** 0.5)


def detect_drift(series: list[float], limits: ControlLimits) -> list[Violation]:
    """Detect out-of-control points using Western Electric rules 1 and 2.

    - Rule 1: any single point beyond 3-sigma.
    - Rule 2: 2 of 3 consecutive points beyond 2-sigma on the same side.
    """
    violations: list[Violation] = []
    two_sigma_up = limits.mean + 2.0 * limits.sigma
    two_sigma_dn = limits.mean - 2.0 * limits.sigma

    for i, value in enumerate(series):
        if value > limits.ucl or value < limits.lcl:
            violations.append(Violation(i, value, "3-sigma"))
            continue
        # Rule 2 needs the current point plus the two before it.
        if i >= 2:
            window = series[i - 2:i + 1]
            up = sum(1 for v in window if v > two_sigma_up)
            dn = sum(1 for v in window if v < two_sigma_dn)
            if (up >= 2 or dn >= 2) and (value > two_sigma_up or value < two_sigma_dn):
                violations.append(Violation(i, value, "2of3-2sigma"))
    return violations


def first_drift(series: list[float], limits: ControlLimits) -> Violation | None:
    v = detect_drift(series, limits)
    return v[0] if v else None
