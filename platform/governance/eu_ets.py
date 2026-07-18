"""EU-ETS annual verified-emissions report (Constitution II/III/IX).

Aggregates per-installation (site) verified CO2 for a compliance year from emission records.
Only REAL, verified records count toward the reportable figure — synthetic data is excluded and
counted separately so it can never be presented as a real regulatory emission (Constitution IX).
Every figure is traceable back to its contributing record ids (Constitution II).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class EmissionRecord:
    record_id: str
    site: str
    timestamp: datetime
    scope: str          # e.g. "DirectCombustion", "ProcessEmissions", "ImportedElectricity"
    tco2: float         # tonnes CO2
    origin: str = "Real"  # "Real" | "Synthetic"
    verified: bool = True


@dataclass(frozen=True)
class EtsReport:
    installation_id: str
    site: str
    year: int
    verified_tco2: float
    unverified_tco2: float
    synthetic_excluded_tco2: float
    by_scope: dict[str, float]
    record_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "installationId": self.installation_id,
            "site": self.site,
            "year": self.year,
            "verifiedTco2": round(self.verified_tco2, 3),
            "unverifiedTco2": round(self.unverified_tco2, 3),
            "syntheticExcludedTco2": round(self.synthetic_excluded_tco2, 3),
            "byScope": {k: round(v, 3) for k, v in sorted(self.by_scope.items())},
            "recordCount": len(self.record_ids),
        }


def compute_ets_report(
    records: list[EmissionRecord],
    *,
    site: str,
    year: int,
    installation_id: str,
) -> EtsReport:
    """Compute the verified EU-ETS emissions figure for one installation/year.

    Reportable ``verified_tco2`` includes only Real + verified records for the site/year.
    Synthetic emissions are summed separately and never added to the reportable total.
    """
    verified = 0.0
    unverified = 0.0
    synthetic = 0.0
    by_scope: dict[str, float] = {}
    ids: list[str] = []
    for r in records:
        if r.site != site or r.timestamp.year != year:
            continue
        if r.origin == "Synthetic":
            synthetic += r.tco2
            continue  # excluded from real reporting (Constitution IX)
        if r.verified:
            verified += r.tco2
            by_scope[r.scope] = by_scope.get(r.scope, 0.0) + r.tco2
            ids.append(r.record_id)
        else:
            unverified += r.tco2
    return EtsReport(
        installation_id=installation_id,
        site=site,
        year=year,
        verified_tco2=verified,
        unverified_tco2=unverified,
        synthetic_excluded_tco2=synthetic,
        by_scope=by_scope,
        record_ids=ids,
    )
