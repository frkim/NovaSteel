"""Operator procedure library — the structured, source-cited knowledge base (FR-012).

Each item is a captured piece of operator expertise with a stable source id and title
so answers can cite where guidance came from (SC-008). In production this is backed by
OneLake + Foundry IQ; here it is a small in-memory/JSON library for the assistant and
its tests.
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeItem:
    source_id: str          # stable citation id, e.g. 'SOP-FURNACE-RELINE-014'
    title: str
    text: str               # the procedure / captured knowledge
    site: str | None = None
    tags: tuple[str, ...] = ()


# Seed library captured from operator interviews (structured SOPs). Extend via capture_interview.py.
SEED_LIBRARY: list[KnowledgeItem] = [
    KnowledgeItem(
        source_id="SOP-FURNACE-RELINE-014",
        title="Blast furnace lining relining trigger",
        text=("Schedule a controlled furnace-lining relining when the physics-informed RUL "
              "model forecasts failure within 21 days, or when heat-flux at the hearth exceeds "
              "the campaign threshold for three consecutive shifts. Never run to failure: an "
              "unplanned lining breach costs ~EUR 8M. Coordinate with maintenance to book the "
              "next planned downtime window."),
        tags=("furnace", "lining", "maintenance", "rul"),
    ),
    KnowledgeItem(
        source_id="SOP-ENERGY-DISPATCH-007",
        title="Shifting energy-intensive heats to low-price windows",
        text=("Move reheating and rolling campaigns into day-ahead low-price / low-carbon windows "
              "when production deadlines allow. The energy-dispatch agent proposes a schedule; the "
              "energy manager must approve before operations act. Do not delay a heat past its "
              "committed order deadline to chase a cheaper slot."),
        tags=("energy", "dispatch", "cost", "co2"),
    ),
    KnowledgeItem(
        source_id="SOP-QUALITY-AUTOMOTIVE-021",
        title="High-grade automotive steel SPC response",
        text=("For automotive grades, when SPC flags composition drift, hold the heat for review and "
              "apply the recommended trim addition before casting. Record predicted vs actual quality "
              "for each heat so the model can be evaluated. A rejected coil is scrapped, not shipped."),
        tags=("quality", "spc", "automotive"),
    ),
]


def load_library(path: str | pathlib.Path | None = None) -> list[KnowledgeItem]:
    """Load the library from a JSON file, or return the seed library."""
    if path is None:
        return list(SEED_LIBRARY)
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return [KnowledgeItem(**item) for item in data]
