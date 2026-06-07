#!/usr/bin/env python3
"""NovaSteel — Project Ignition live demo (self-contained implementation).

This module is a runnable implementation of the live demo described in
``documentation/work/08-demo-script.md``. It proves the three AI workloads and
the compliance "trust moment" entirely on **synthetic, clearly-labelled data**:

* Scene A — Furnace-lining Remaining-Useful-Life (RUL) model raising a **21-day
  advance alert** with an uncertainty band and its drivers.
* Scene B — Carbon-aware **energy-dispatch optimization** reporting €/ton and
  tCO₂/ton deltas (target −14% energy / −22% CO₂).
* Scene C — A grounded **knowledge assistant** (RAG-style) with citations and an
  interview-capture mode.
* Trust — an **audit / lineage log** of every prediction, recommendation and
  human approval.

It is deliberately dependency-free (Python standard library only) so the
walkthrough always runs offline — meeting the demo script's "recorded fallback"
requirement. In production these workloads run on the Azure services described in
``documentation/work/02-solution-architecture.md`` and
``documentation/work/03-data-and-ai-design.md``.

Run the web walkthrough::

    python novasteel_demo.py            # serves http://127.0.0.1:5000/

Run the tests::

    python -m unittest test_novasteel_demo
"""

from __future__ import annotations

import hashlib
import html
import math
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, List, Optional, Sequence, Tuple
from urllib.parse import parse_qs, urlparse

# ---------------------------------------------------------------------------
# Configuration — illustrative demo estimates (see documentation/work/)
# ---------------------------------------------------------------------------

SYNTHETIC_DATA_LABEL = "Synthetic demo data"
RANDOM_SEED = 2026

# Headline KPI targets (illustrative demo estimates) — see 00/01/07.
TARGETS = {
    "energy_reduction_pct": -14.0,   # O1 — energy per ton
    "co2_reduction_pct": -22.0,      # O2 — CO2 per ton
    "furnace_warning_days": 21,      # O3 — advance warning
    "yield_improvement_pct": 8.0,    # O4 — high-grade yield
}

AVERTED_FAILURE_EUR = 8_000_000
GOVERNANCE_STATEMENT = (
    "EU-resident · GDPR + EU AI Act aligned · human-in-the-loop · "
    "every prediction, recommendation and approval is logged."
)


# ---------------------------------------------------------------------------
# Synthetic data generators
# ---------------------------------------------------------------------------

def generate_furnace_telemetry(
    days: int = 110,
    failure_day: int = 105,
    as_of_day: int = 84,
    seed: int = RANDOM_SEED,
) -> List[Dict[str, float]]:
    """Generate synthetic daily furnace-lining telemetry with injected wear.

    Wear ramps slowly, then accelerates so that, at ``as_of_day`` (the demo's
    "today"), the recent wear-rate projects a refractory failure in ~21 days.
    """
    import random

    rng = random.Random(seed)
    s_final = 0.012                      # wear/day in the accelerated phase
    knee = 60                            # day where wear acceleration begins
    h_asof = 1.0 - s_final * (failure_day - as_of_day)
    wear_knee = h_asof + s_final * (knee - as_of_day)
    early_slope = (wear_knee - 0.10) / knee

    rows: List[Dict[str, float]] = []
    for d in range(days):
        if d <= knee:
            wear = 0.10 + early_slope * d
        else:
            wear = h_asof + s_final * (d - as_of_day)
        wear = max(0.0, wear)
        thermal = 35.0 + 25.0 * wear + rng.gauss(0.0, 0.3)      # °C/cm
        vibration = 1.5 + 3.0 * wear + rng.gauss(0.0, 0.04)     # mm/s
        offgas = 2.0 + 1.5 * wear + rng.gauss(0.0, 0.05)        # index
        rows.append(
            {
                "day": d,
                "wear_true": round(wear, 4),
                "thermal_gradient": round(thermal, 3),
                "vibration": round(vibration, 4),
                "offgas_index": round(offgas, 4),
            }
        )
    return rows


# Energy-dispatch synthetic scenario: four 6-hour blocks over a day.
# Prices in €/MWh, grid carbon in kgCO2/MWh (illustrative demo series).
ENERGY_BLOCKS: List[Dict[str, float]] = [
    {"block": "Night (00–06)", "price": 42.0, "carbon": 150.0, "base": 1.0, "flex_capacity": 5.0},
    {"block": "Morning (06–12)", "price": 78.0, "carbon": 320.0, "base": 1.0, "flex_capacity": 2.0},
    {"block": "Midday (12–18)", "price": 120.0, "carbon": 210.0, "base": 1.0, "flex_capacity": 2.0},
    {"block": "Evening (18–24)", "price": 95.0, "carbon": 470.0, "base": 1.0, "flex_capacity": 3.0},
]
# Energy-intensive flexible steps (MWh/ton) the optimizer is allowed to shift.
FLEX_ENERGY = 1.18
# Baseline runs the flexible steps in the high-carbon Evening block.
BASELINE_FLEX_BLOCK = 3


def generate_sop_corpus() -> List[Dict[str, object]]:
    """A small synthetic Standard-Operating-Procedure corpus (no real data)."""
    return [
        {
            "id": "SOP-101",
            "title": "Cold-start surface quality on grade X",
            "tags": ["grade x", "cold start", "surface quality", "casting"],
            "text": (
                "During a cold start on grade X, stabilise surface quality by ramping "
                "the preheat slowly to avoid thermal shock. Hold the tundish temperature "
                "within the target superheat window and use the qualified mold powder for "
                "grade X. Reduce casting speed for the first heats until the shell forms "
                "uniformly. Inspect the first slabs for surface cracks before increasing "
                "throughput."
            ),
            "status": "approved",
        },
        {
            "id": "SOP-102",
            "title": "Refractory lining inspection window",
            "tags": ["furnace", "lining", "refractory", "maintenance"],
            "text": (
                "When the predictive model raises a lining alert, schedule a refractory "
                "inspection within the recommended window. Confirm the thermal gradient and "
                "vibration trends before planning the reline so production is not stopped "
                "unnecessarily."
            ),
            "status": "approved",
        },
        {
            "id": "SOP-103",
            "title": "Shifting energy-intensive steps off-peak",
            "tags": ["energy", "dispatch", "carbon", "scheduling"],
            "text": (
                "Move energy-intensive steps into low-price and low-carbon windows when the "
                "production schedule allows. The optimizer recommends a slot; the operator "
                "confirms before any change is applied."
            ),
            "status": "approved",
        },
        {
            "id": "SOP-104",
            "title": "Grade X chemistry control",
            "tags": ["grade x", "chemistry", "quality"],
            "text": (
                "Keep grade X carbon and manganese within the narrow automotive specification. "
                "Trim alloy additions gradually and re-sample before tapping to protect "
                "high-grade yield."
            ),
            "status": "approved",
        },
    ]


# ---------------------------------------------------------------------------
# Scene A — Furnace RUL model (predictive maintenance)
# ---------------------------------------------------------------------------

def estimate_health(row: Dict[str, float]) -> float:
    """Estimate the lining health index (0 healthy → 1 failure) from sensors."""
    thermal_norm = (row["thermal_gradient"] - 35.0) / 25.0
    vibration_norm = (row["vibration"] - 1.5) / 3.0
    return 0.5 * thermal_norm + 0.5 * vibration_norm


def _linfit(xs: Sequence[float], ys: Sequence[float]) -> Tuple[float, float]:
    """Ordinary least-squares fit, returning (slope, intercept)."""
    n = len(xs)
    if n < 2:
        raise ValueError("need at least two points for a fit")
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    sxx = sum((x - mean_x) ** 2 for x in xs)
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    if sxx == 0:
        raise ValueError("degenerate x values")
    slope = sxy / sxx
    intercept = mean_y - slope * mean_x
    return slope, intercept


def assess_furnace(
    telemetry: Sequence[Dict[str, float]],
    as_of_day: int = 84,
    window: int = 14,
    threshold: float = 1.0,
    alert_horizon: int = 21,
) -> Dict[str, object]:
    """Project Remaining-Useful-Life and raise a horizon alert with uncertainty.

    Returns predicted RUL in days, an uncertainty band, whether a "failure within
    ``alert_horizon`` days" alert fires, and the ranked degradation drivers.
    """
    pts = [
        (r["day"], estimate_health(r))
        for r in telemetry
        if as_of_day - window < r["day"] <= as_of_day
    ]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    slope, intercept = _linfit(xs, ys)
    health_now = slope * as_of_day + intercept

    residuals = [y - (slope * x + intercept) for x, y in pts]
    dof = max(1, len(pts) - 2)
    sigma = math.sqrt(sum(e * e for e in residuals) / dof)

    if slope <= 0:
        rul = float("inf")
        rul_low = float("inf")
        rul_high = float("inf")
    else:
        rul = (threshold - health_now) / slope
        # An earlier (pessimistic) and later (optimistic) bound from sensor noise.
        rul_low = max(0.0, (threshold - (health_now + sigma)) / slope)
        rul_high = (threshold - (health_now - sigma)) / slope

    alert = math.isfinite(rul) and rul <= alert_horizon

    drivers = _degradation_drivers(telemetry, as_of_day, window)

    return {
        "as_of_day": as_of_day,
        "health_now": round(health_now, 4),
        "health_slope": round(slope, 5),
        "predicted_rul_days": round(rul, 1) if math.isfinite(rul) else None,
        "rul_low_days": round(rul_low, 1) if math.isfinite(rul_low) else None,
        "rul_high_days": round(rul_high, 1) if math.isfinite(rul_high) else None,
        "alert_horizon": alert_horizon,
        "alert": alert,
        "drivers": drivers,
    }


def _degradation_drivers(
    telemetry: Sequence[Dict[str, float]], as_of_day: int, window: int
) -> List[Dict[str, object]]:
    """Rank the contribution of each sensor family to the recent degradation."""
    rows = [r for r in telemetry if as_of_day - window < r["day"] <= as_of_day]
    now = rows[-1]
    thermal_level = max(0.0, (now["thermal_gradient"] - 35.0) / 25.0)
    wear_rate_level = max(0.0, (now["vibration"] - 1.5) / 3.0)
    total = thermal_level + wear_rate_level or 1.0
    drivers = [
        {
            "name": "Thermal gradient",
            "value": round(now["thermal_gradient"], 1),
            "unit": "°C/cm",
            "contribution_pct": round(100.0 * thermal_level / total, 1),
        },
        {
            "name": "Wear-rate proxy (vibration)",
            "value": round(now["vibration"], 2),
            "unit": "mm/s",
            "contribution_pct": round(100.0 * wear_rate_level / total, 1),
        },
    ]
    drivers.sort(key=lambda d: d["contribution_pct"], reverse=True)
    return drivers


# ---------------------------------------------------------------------------
# Scene B — Energy-dispatch optimization
# ---------------------------------------------------------------------------

def _norm(value: float, low: float, high: float) -> float:
    if high == low:
        return 0.0
    return (value - low) / (high - low)


def optimize_dispatch(
    blocks: Sequence[Dict[str, float]] = ENERGY_BLOCKS,
    flex_energy: float = FLEX_ENERGY,
    baseline_block: int = BASELINE_FLEX_BLOCK,
    price_weight: float = 0.5,
    carbon_weight: float = 0.5,
) -> Dict[str, object]:
    """Shift flexible energy-intensive steps into low-price / low-carbon windows.

    Returns per-block baseline and optimized load plus €/ton and tCO₂/ton before
    and after, the percentage deltas, and the share of energy shifted.
    """
    base_load = [b["base"] for b in blocks]
    baseline = list(base_load)
    baseline[baseline_block] += flex_energy

    prices = [b["price"] for b in blocks]
    carbons = [b["carbon"] for b in blocks]
    p_lo, p_hi = min(prices), max(prices)
    c_lo, c_hi = min(carbons), max(carbons)

    def score(i: int) -> float:
        return price_weight * _norm(prices[i], p_lo, p_hi) + carbon_weight * _norm(
            carbons[i], c_lo, c_hi
        )

    order = sorted(range(len(blocks)), key=score)
    optimized = list(base_load)
    remaining = flex_energy
    for i in order:
        if remaining <= 1e-9:
            break
        take = min(blocks[i]["flex_capacity"], remaining)
        optimized[i] += take
        remaining -= take
    if remaining > 1e-6:
        raise ValueError("insufficient flexible capacity to schedule the load")

    cost_base = sum(p * l for p, l in zip(prices, baseline))
    cost_opt = sum(p * l for p, l in zip(prices, optimized))
    carbon_base = sum(c * l for c, l in zip(carbons, baseline)) / 1000.0  # tCO2/ton
    carbon_opt = sum(c * l for c, l in zip(carbons, optimized)) / 1000.0

    total_energy = sum(baseline)
    return {
        "blocks": [b["block"] for b in blocks],
        "prices": prices,
        "carbons": carbons,
        "baseline_load": [round(x, 3) for x in baseline],
        "optimized_load": [round(x, 3) for x in optimized],
        "cost_per_ton_base": round(cost_base, 2),
        "cost_per_ton_opt": round(cost_opt, 2),
        "carbon_per_ton_base": round(carbon_base, 4),
        "carbon_per_ton_opt": round(carbon_opt, 4),
        "cost_delta_pct": round(100.0 * (cost_opt - cost_base) / cost_base, 1),
        "carbon_delta_pct": round(100.0 * (carbon_opt - carbon_base) / carbon_base, 1),
        "energy_shifted_pct": round(100.0 * flex_energy / total_energy, 1),
        "total_energy_mwh_per_ton": round(total_energy, 3),
    }


# ---------------------------------------------------------------------------
# Scene C — GenAI knowledge assistant (grounded retrieval with citations)
# ---------------------------------------------------------------------------

_STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "do", "we",
    "how", "what", "is", "are", "with", "during", "our", "my", "i", "it", "by",
    "at", "as", "be", "this", "that", "from",
}


def _tokenize(text: str) -> List[str]:
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in _STOPWORDS]


class KnowledgeAssistant:
    """A grounded RAG-style assistant over a synthetic SOP corpus.

    Answers are built only from retrieved procedures and always carry citations;
    when nothing relevant is found the assistant refuses rather than inventing an
    answer. The interview mode captures a new tip into the library, pending human
    (metallurgist) review — keeping AI advising and people deciding.
    """

    def __init__(self, corpus: Optional[List[Dict[str, object]]] = None):
        self.corpus: List[Dict[str, object]] = corpus if corpus is not None else generate_sop_corpus()
        self._next_id = 200

    def _idf(self, token: str) -> float:
        df = sum(1 for doc in self.corpus if token in _tokenize(str(doc["text"]) + " " + str(doc["title"])))
        return math.log((1 + len(self.corpus)) / (1 + df)) + 1.0

    def _score(self, query_tokens: Sequence[str], doc: Dict[str, object]) -> float:
        doc_tokens = _tokenize(str(doc["text"]) + " " + str(doc["title"]))
        if not doc_tokens:
            return 0.0
        score = 0.0
        for qt in set(query_tokens):
            tf = doc_tokens.count(qt) / len(doc_tokens)
            if tf:
                score += tf * self._idf(qt)
        return score

    def retrieve(self, query: str, top_k: int = 2) -> List[Tuple[Dict[str, object], float]]:
        query_tokens = _tokenize(query)
        scored = [(doc, self._score(query_tokens, doc)) for doc in self.corpus]
        scored = [pair for pair in scored if pair[1] > 0.0]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]

    def answer(self, query: str, threshold: float = 0.02, min_overlap: int = 2) -> Dict[str, object]:
        results = self.retrieve(query)
        query_tokens = set(_tokenize(query))

        def overlap(doc: Dict[str, object]) -> int:
            return len(query_tokens & set(_tokenize(str(doc["text"]) + " " + str(doc["title"]))))

        if (
            not results
            or results[0][1] < threshold
            or overlap(results[0][0]) < min_overlap
        ):
            return {
                "grounded": False,
                "answer": (
                    "I can't find this in the approved procedure library, so I won't "
                    "answer. Please capture it via interview mode for review."
                ),
                "citations": [],
            }
        snippets: List[str] = []
        citations: List[Dict[str, str]] = []
        for doc, _ in results:
            sentences = re.split(r"(?<=[.!?])\s+", str(doc["text"]))
            best = max(
                sentences,
                key=lambda s: len(query_tokens & set(_tokenize(s))),
                default="",
            )
            if best:
                snippets.append(f"{best.strip()} [{doc['id']}]")
                citations.append({"id": str(doc["id"]), "title": str(doc["title"]), "status": str(doc["status"])})
        return {
            "grounded": True,
            "answer": " ".join(snippets),
            "citations": citations,
            "disclaimer": "AI advises, metallurgists decide.",
        }

    def capture_tip(self, title: str, text: str, author: str = "operator") -> Dict[str, object]:
        """Interview mode — capture a new tip, pending human review."""
        if not title.strip() or not text.strip():
            raise ValueError("title and text are required to capture a tip")
        sop_id = f"SOP-{self._next_id}"
        self._next_id += 1
        record = {
            "id": sop_id,
            "title": title.strip(),
            "tags": _tokenize(title),
            "text": text.strip(),
            "status": "pending metallurgist review",
            "captured_by": author,
        }
        self.corpus.append(record)
        return record


# ---------------------------------------------------------------------------
# Trust moment — audit / lineage log
# ---------------------------------------------------------------------------

@dataclass
class AuditRecord:
    seq: int
    ts: str
    actor: str
    action: str
    workload: str
    summary: str
    prev_hash: str
    hash: str = ""

    def payload(self) -> str:
        return f"{self.seq}|{self.ts}|{self.actor}|{self.action}|{self.workload}|{self.summary}|{self.prev_hash}"


class AuditLog:
    """Tamper-evident audit/lineage log (hash-chained) for the trust moment."""

    GENESIS = "GENESIS"

    def __init__(self) -> None:
        self.records: List[AuditRecord] = []

    def record(self, actor: str, action: str, workload: str, summary: str) -> AuditRecord:
        prev_hash = self.records[-1].hash if self.records else self.GENESIS
        rec = AuditRecord(
            seq=len(self.records) + 1,
            ts=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            actor=actor,
            action=action,
            workload=workload,
            summary=summary,
            prev_hash=prev_hash,
        )
        rec.hash = hashlib.sha256(rec.payload().encode("utf-8")).hexdigest()
        self.records.append(rec)
        return rec

    def verify(self) -> bool:
        prev_hash = self.GENESIS
        for rec in self.records:
            if rec.prev_hash != prev_hash:
                return False
            if hashlib.sha256(rec.payload().encode("utf-8")).hexdigest() != rec.hash:
                return False
            prev_hash = rec.hash
        return True


# ---------------------------------------------------------------------------
# Web walkthrough (standard-library HTTP server, inline SVG charts)
# ---------------------------------------------------------------------------

_CSS = """
* { box-sizing: border-box; }
body { font-family: 'Segoe UI', Roboto, Arial, sans-serif; margin: 0; color: #1b2733;
       background: #f4f6f8; }
a { color: #0f6cbd; }
.banner { background: #b54708; color: #fff; text-align: center; padding: 6px;
          font-weight: 600; letter-spacing: .03em; }
header { background: #1b2733; color: #fff; padding: 18px 28px; }
header h1 { margin: 0; font-size: 1.25rem; }
header p { margin: 4px 0 0; color: #9fb1c1; font-size: .9rem; }
nav { display: flex; gap: 4px; background: #25405a; padding: 0 16px; flex-wrap: wrap; }
nav a { color: #cfe0f0; text-decoration: none; padding: 12px 16px; font-size: .92rem; }
nav a.active, nav a:hover { background: #0f6cbd; color: #fff; }
main { max-width: 980px; margin: 24px auto; padding: 0 20px 60px; }
.card { background: #fff; border: 1px solid #e1e6ea; border-radius: 10px;
        padding: 22px; margin-bottom: 22px; box-shadow: 0 1px 2px rgba(0,0,0,.04); }
h2 { margin-top: 0; }
.kpis { display: flex; gap: 14px; flex-wrap: wrap; }
.kpi { flex: 1 1 160px; background: #eef4fb; border-radius: 10px; padding: 16px; text-align: center; }
.kpi .v { font-size: 1.6rem; font-weight: 700; color: #0f6cbd; }
.kpi .l { font-size: .82rem; color: #5a6b7b; }
.alert { background: #fde7e9; border: 1px solid #d13438; color: #a4262c; padding: 14px 16px;
         border-radius: 8px; font-weight: 600; }
.ok { background: #e6f4ea; border: 1px solid #107c10; color: #0b6a0b; padding: 14px 16px;
      border-radius: 8px; }
table { width: 100%; border-collapse: collapse; margin-top: 10px; }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid #e8ecef; font-size: .92rem; }
th { color: #5a6b7b; font-weight: 600; }
.tieback { font-style: italic; color: #44525f; border-left: 3px solid #0f6cbd; padding-left: 12px; margin-top: 14px; }
input[type=text], textarea { width: 100%; padding: 9px; border: 1px solid #cdd5dc; border-radius: 6px;
                             font-family: inherit; font-size: .95rem; }
button { background: #0f6cbd; color: #fff; border: 0; padding: 10px 18px; border-radius: 6px;
         font-size: .95rem; cursor: pointer; }
.cite { background: #eef4fb; border-radius: 6px; padding: 2px 8px; font-size: .82rem; }
.muted { color: #5a6b7b; font-size: .86rem; }
code { background: #eef1f4; padding: 1px 5px; border-radius: 4px; }
"""

_NAV = [
    ("/", "Overview"),
    ("/scene-a", "A · Predict failure"),
    ("/scene-b", "B · Energy & CO₂"),
    ("/scene-c", "C · Knowledge"),
    ("/trust", "Trust · Compliance"),
    ("/close", "Close"),
]


def _esc(value: object) -> str:
    return html.escape(str(value))


def layout(title: str, body: str, active: str) -> str:
    nav = "".join(
        '<a class="%s" href="%s">%s</a>'
        % ("active" if path == active else "", path, _esc(label))
        for path, label in _NAV
    )
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<title>" + _esc(title) + " · NovaSteel Project Ignition</title>"
        "<style>" + _CSS + "</style></head><body>"
        "<div class='banner'>" + _esc(SYNTHETIC_DATA_LABEL)
        + " — no real plant or personal data · figures are illustrative demo estimates</div>"
        "<header><h1>NovaSteel — Project Ignition demo</h1>"
        "<p>" + _esc(title) + "</p></header>"
        "<nav>" + nav + "</nav><main>" + body + "</main></body></html>"
    )


def svg_line_chart(
    series: Sequence[Tuple[str, str, Sequence[Tuple[float, float]]]],
    width: int = 760,
    height: int = 260,
    vlines: Sequence[Tuple[float, str, str]] = (),
    hlines: Sequence[Tuple[float, str, str]] = (),
) -> str:
    """Render a minimal multi-series line chart as inline SVG."""
    pad = 36
    all_x = [p[0] for _, _, pts in series for p in pts]
    all_y = [p[1] for _, _, pts in series for p in pts]
    all_y += [y for y, _, _ in hlines]
    if not all_x or not all_y:
        return ""
    x_lo, x_hi = min(all_x), max(all_x)
    y_lo, y_hi = min(all_y), max(all_y)
    if x_hi == x_lo:
        x_hi += 1
    if y_hi == y_lo:
        y_hi += 1

    def sx(x: float) -> float:
        return pad + (x - x_lo) / (x_hi - x_lo) * (width - 2 * pad)

    def sy(y: float) -> float:
        return height - pad - (y - y_lo) / (y_hi - y_lo) * (height - 2 * pad)

    parts = [f"<svg viewBox='0 0 {width} {height}' width='100%' height='{height}' "
             "role='img' xmlns='http://www.w3.org/2000/svg'>"]
    parts.append(f"<rect x='0' y='0' width='{width}' height='{height}' fill='#fff'/>")
    parts.append(
        f"<line x1='{pad}' y1='{height-pad}' x2='{width-pad}' y2='{height-pad}' stroke='#c8d0d8'/>"
        f"<line x1='{pad}' y1='{pad}' x2='{pad}' y2='{height-pad}' stroke='#c8d0d8'/>"
    )
    for y, color, label in hlines:
        yy = sy(y)
        parts.append(
            f"<line x1='{pad}' y1='{yy:.1f}' x2='{width-pad}' y2='{yy:.1f}' "
            f"stroke='{color}' stroke-dasharray='5 4'/>"
            f"<text x='{width-pad}' y='{yy-4:.1f}' font-size='11' fill='{color}' "
            f"text-anchor='end'>{_esc(label)}</text>"
        )
    for x, color, label in vlines:
        xx = sx(x)
        parts.append(
            f"<line x1='{xx:.1f}' y1='{pad}' x2='{xx:.1f}' y2='{height-pad}' "
            f"stroke='{color}' stroke-dasharray='4 4'/>"
            f"<text x='{xx+4:.1f}' y='{pad+12}' font-size='11' fill='{color}'>{_esc(label)}</text>"
        )
    for label, color, pts in series:
        d = " ".join(
            ("M" if i == 0 else "L") + f"{sx(x):.1f} {sy(y):.1f}"
            for i, (x, y) in enumerate(pts)
        )
        parts.append(f"<path d='{d}' fill='none' stroke='{color}' stroke-width='2'/>")
    # legend
    lx = pad + 6
    for label, color, _ in series:
        parts.append(
            f"<rect x='{lx}' y='{pad-8}' width='10' height='10' fill='{color}'/>"
            f"<text x='{lx+14}' y='{pad+1}' font-size='11' fill='#44525f'>{_esc(label)}</text>"
        )
        lx += 18 + 8 * len(label)
    parts.append("</svg>")
    return "".join(parts)


def svg_grouped_bars(
    categories: Sequence[str],
    series: Sequence[Tuple[str, str, Sequence[float]]],
    width: int = 760,
    height: int = 260,
    unit: str = "",
) -> str:
    """Render a grouped bar chart (baseline vs optimized) as inline SVG."""
    pad = 40
    all_v = [v for _, _, vals in series for v in vals]
    if not all_v:
        return ""
    v_hi = max(all_v) * 1.15 or 1.0
    n_cat = len(categories)
    n_ser = len(series)
    group_w = (width - 2 * pad) / n_cat
    bar_w = group_w / (n_ser + 1)

    def by(v: float) -> float:
        return height - pad - v / v_hi * (height - 2 * pad)

    parts = [f"<svg viewBox='0 0 {width} {height}' width='100%' height='{height}' "
             "role='img' xmlns='http://www.w3.org/2000/svg'>"]
    parts.append(f"<rect x='0' y='0' width='{width}' height='{height}' fill='#fff'/>")
    parts.append(f"<line x1='{pad}' y1='{height-pad}' x2='{width-pad}' y2='{height-pad}' stroke='#c8d0d8'/>")
    for ci, cat in enumerate(categories):
        gx = pad + ci * group_w
        for si, (label, color, vals) in enumerate(series):
            bx = gx + bar_w * (si + 0.5)
            v = vals[ci]
            parts.append(
                f"<rect x='{bx:.1f}' y='{by(v):.1f}' width='{bar_w*0.9:.1f}' "
                f"height='{height-pad-by(v):.1f}' fill='{color}'/>"
            )
        parts.append(
            f"<text x='{gx+group_w/2:.1f}' y='{height-pad+16}' font-size='11' "
            f"fill='#44525f' text-anchor='middle'>{_esc(cat)}</text>"
        )
    lx = pad + 6
    for label, color, _ in series:
        parts.append(
            f"<rect x='{lx}' y='10' width='10' height='10' fill='{color}'/>"
            f"<text x='{lx+14}' y='19' font-size='11' fill='#44525f'>{_esc(label)}</text>"
        )
        lx += 24 + 8 * len(label)
    if unit:
        parts.append(f"<text x='{pad}' y='20' font-size='11' fill='#8a97a3'>{_esc(unit)}</text>")
    parts.append("</svg>")
    return "".join(parts)


# --- page builders ---------------------------------------------------------

def page_overview() -> str:
    t = TARGETS
    kpis = (
        f"<div class='kpi'><div class='v'>{t['energy_reduction_pct']:.0f}%</div><div class='l'>Energy / ton (O1)</div></div>"
        f"<div class='kpi'><div class='v'>{t['co2_reduction_pct']:.0f}%</div><div class='l'>CO₂ / ton (O2)</div></div>"
        f"<div class='kpi'><div class='v'>{t['furnace_warning_days']} days</div><div class='l'>Furnace warning (O3)</div></div>"
        f"<div class='kpi'><div class='v'>+{t['yield_improvement_pct']:.0f}%</div><div class='l'>High-grade yield (O4)</div></div>"
    )
    body = (
        "<div class='card'><h2>Live walkthrough</h2>"
        "<p>This demo proves the three AI workloads and the compliance trust moment "
        "on <strong>synthetic, clearly-labelled data</strong>, mirroring "
        "<code>documentation/work/08-demo-script.md</code>. Everything runs offline so "
        "it doubles as the recorded fallback.</p>"
        "<div class='kpis'>" + kpis + "</div></div>"
        "<div class='card'><h2>Before the room — setup checklist</h2><ul>"
        "<li>✅ Dashboards load below (Scenes A–C and the trust moment).</li>"
        "<li>✅ Synthetic datasets generated: furnace telemetry with injected degradation; "
        "illustrative spot-price / carbon series; synthetic SOP corpus.</li>"
        "<li>✅ Knowledge assistant indexed and responding (Scene C).</li>"
        "<li>✅ Fallback: this app runs with no external services.</li>"
        "<li>✅ Visible <strong>“Synthetic demo data”</strong> label on every screen.</li>"
        "</ul></div>"
        "<div class='card'><h2>Run order (≈12 min)</h2><ol>"
        "<li><a href='/scene-a'>Scene A</a> — predict a furnace failure 21 days early.</li>"
        "<li><a href='/scene-b'>Scene B</a> — optimize energy &amp; CO₂.</li>"
        "<li><a href='/scene-c'>Scene C</a> — capture operator expertise.</li>"
        "<li><a href='/trust'>Trust moment</a> — audit &amp; lineage.</li>"
        "<li><a href='/close'>Close</a> — the ask.</li></ol></div>"
    )
    return layout("Overview & setup", body, "/")


def page_scene_a(as_of_day: int, audit: AuditLog) -> str:
    telemetry = generate_furnace_telemetry()
    max_day = telemetry[-1]["day"]
    as_of_day = max(15, min(as_of_day, max_day))
    result = assess_furnace(telemetry, as_of_day=as_of_day)
    audit.record(
        "rul-model", "prediction", "A · Predictive maintenance",
        f"RUL {result['predicted_rul_days']}d at day {as_of_day}; alert={result['alert']}",
    )

    health_pts = [(r["day"], estimate_health(r)) for r in telemetry if r["day"] <= as_of_day]
    chart = svg_line_chart(
        series=[("Estimated lining health", "#0f6cbd", health_pts)],
        hlines=[(1.0, "#d13438", "failure threshold")],
        vlines=[(as_of_day, "#b54708", "today")],
    )

    if result["alert"]:
        status = (
            f"<div class='alert'>⚠ 21-day advance alert — predicted lining failure in "
            f"~{result['predicted_rul_days']} days "
            f"(uncertainty band {result['rul_low_days']}–{result['rul_high_days']} days).</div>"
        )
    else:
        status = (
            f"<div class='ok'>No alert yet — predicted Remaining-Useful-Life "
            f"≈ {result['predicted_rul_days']} days. Fast-forward the timeline to see the alert fire.</div>"
        )

    drivers = "".join(
        f"<tr><td>{_esc(d['name'])}</td><td>{_esc(d['value'])} {_esc(d['unit'])}</td>"
        f"<td>{_esc(d['contribution_pct'])}%</td></tr>"
        for d in result["drivers"]
    )

    scrub = "".join(
        f"<a href='/scene-a?day={d}'>{d}</a> "
        for d in (40, 60, 75, 84, 95)
    )

    body = (
        "<div class='card'><h2>Scene A — Predict a furnace failure</h2>"
        + status
        + "<p class='muted'>Fast-forward the synthetic timeline (today = day "
        + _esc(as_of_day) + "): " + scrub + "</p>"
        + chart
        + "</div>"
        "<div class='card'><h2>Drivers &amp; recommended action</h2>"
        "<table><tr><th>Driver</th><th>Current value</th><th>Contribution</th></tr>"
        + drivers + "</table>"
        "<p class='muted'>Recommended inspection window: within the next "
        f"{_esc(result['rul_low_days'])}–{_esc(result['predicted_rul_days'])} days, "
        "operator-confirmed.</p>"
        "<p class='tieback'>Tie-back (COO): “This is the €8M event we now see 21 days early.”</p>"
        "</div>"
    )
    return layout("Scene A · Predict a furnace failure", body, "/scene-a")


def page_scene_b(audit: AuditLog) -> str:
    r = optimize_dispatch()
    audit.record(
        "energy-optimizer", "recommendation", "B · Energy dispatch",
        f"Shift {r['energy_shifted_pct']}% load → cost {r['cost_delta_pct']}%, CO₂ {r['carbon_delta_pct']}%",
    )
    curves = svg_line_chart(
        series=[
            ("Spot price (€/MWh)", "#0f6cbd", list(zip(range(len(r["prices"])), r["prices"]))),
            ("Grid carbon (kg/MWh)", "#b54708", list(zip(range(len(r["carbons"])), r["carbons"]))),
        ],
    )
    loads = svg_grouped_bars(
        categories=r["blocks"],
        series=[
            ("Baseline load", "#9fb1c1", r["baseline_load"]),
            ("Optimized load", "#107c10", r["optimized_load"]),
        ],
        unit="MWh/ton per block",
    )
    body = (
        "<div class='card'><h2>Scene B — Optimize energy &amp; CO₂</h2>"
        "<p>The optimizer shifts energy-intensive steps into low-price / low-carbon "
        "windows, within production constraints. Operator confirms before any change.</p>"
        + curves +
        "<div class='kpis' style='margin-top:16px'>"
        f"<div class='kpi'><div class='v'>{r['cost_delta_pct']:.1f}%</div>"
        f"<div class='l'>€/ton: {r['cost_per_ton_base']:.0f} → {r['cost_per_ton_opt']:.0f} (target −14%)</div></div>"
        f"<div class='kpi'><div class='v'>{r['carbon_delta_pct']:.1f}%</div>"
        f"<div class='l'>tCO₂/ton: {r['carbon_per_ton_base']:.3f} → {r['carbon_per_ton_opt']:.3f} (target −22%)</div></div>"
        f"<div class='kpi'><div class='v'>{r['energy_shifted_pct']:.1f}%</div>"
        f"<div class='l'>energy shifted to clean/cheap windows</div></div>"
        "</div></div>"
        "<div class='card'><h2>Load shift by block</h2>" + loads +
        "<p class='tieback'>Tie-back (CFO &amp; Head of Sustainability / ESG): cost down and a "
        "verifiable carbon story.</p></div>"
    )
    return layout("Scene B · Optimize energy & CO₂", body, "/scene-b")


def page_scene_c(
    assistant: KnowledgeAssistant,
    audit: AuditLog,
    asked: Optional[str] = None,
    answer: Optional[Dict[str, object]] = None,
    captured: Optional[Dict[str, object]] = None,
) -> str:
    default_q = "How do we stabilise surface quality on grade X during a cold start?"
    answer_block = ""
    if answer is not None:
        if answer["grounded"]:
            cites = " ".join(
                f"<span class='cite'>{_esc(c['id'])} — {_esc(c['title'])} ({_esc(c['status'])})</span>"
                for c in answer["citations"]
            )
            answer_block = (
                "<div class='ok'><strong>Grounded answer:</strong> "
                + _esc(answer["answer"]) + "</div>"
                "<p class='muted'>Citations: " + cites + "</p>"
                "<p class='tieback'>" + _esc(answer.get("disclaimer", "")) + "</p>"
            )
        else:
            answer_block = "<div class='alert'>" + _esc(answer["answer"]) + "</div>"
    captured_block = ""
    if captured is not None:
        captured_block = (
            "<div class='ok'>Captured <strong>" + _esc(captured["id"]) + "</strong> — “"
            + _esc(captured["title"]) + "”, status: " + _esc(captured["status"])
            + ". It is now retrievable, pending review.</div>"
        )

    library = "".join(
        f"<tr><td>{_esc(d['id'])}</td><td>{_esc(d['title'])}</td><td>{_esc(d['status'])}</td></tr>"
        for d in assistant.corpus
    )

    body = (
        "<div class='card'><h2>Scene C — Capture operator expertise</h2>"
        "<form method='post' action='/scene-c'>"
        "<label class='muted'>Ask the knowledge assistant</label>"
        "<input type='text' name='question' value='" + _esc(asked or default_q) + "'>"
        "<p><button name='action' value='ask'>Ask</button></p></form>"
        + answer_block +
        "</div>"
        "<div class='card'><h2>Interview mode — capture a new tip</h2>"
        "<form method='post' action='/scene-c'>"
        "<label class='muted'>Title</label><input type='text' name='title' placeholder='e.g. Stabilising grade Y during restart'>"
        "<label class='muted'>Tip</label><textarea name='text' rows='3' placeholder='Best-known method from a senior operator…'></textarea>"
        "<p><button name='action' value='capture'>Capture (pending review)</button></p></form>"
        + captured_block +
        "<p class='tieback'>Tie-back (Head of Quality): best-known methods, preserved and "
        "spread → supports +8% yield; AI advises, metallurgists decide.</p></div>"
        "<div class='card'><h2>Procedure library</h2>"
        "<table><tr><th>ID</th><th>Title</th><th>Status</th></tr>" + library + "</table></div>"
    )
    return layout("Scene C · Capture operator expertise", body, "/scene-c")


def page_trust(audit: AuditLog) -> str:
    if not audit.records:
        audit.record("system", "info", "Trust", "Audit log initialised")
    rows = "".join(
        f"<tr><td>{r.seq}</td><td class='muted'>{_esc(r.ts)}</td><td>{_esc(r.actor)}</td>"
        f"<td>{_esc(r.action)}</td><td>{_esc(r.workload)}</td><td>{_esc(r.summary)}</td>"
        f"<td class='muted'>{_esc(r.hash[:12])}…</td></tr>"
        for r in audit.records
    )
    verified = audit.verify()
    status = (
        "<div class='ok'>✔ Lineage verified — hash chain intact across "
        f"{len(audit.records)} records.</div>"
        if verified
        else "<div class='alert'>✗ Lineage broken — tamper detected.</div>"
    )
    body = (
        "<div class='card'><h2>Trust moment — audit &amp; lineage</h2>"
        + status +
        "<p>Every prediction, recommendation and human approval is logged and hash-chained "
        "(Purview lineage + Azure Monitor in production).</p>"
        "<p class='muted'>" + _esc(GOVERNANCE_STATEMENT) + "</p>"
        "<table><tr><th>#</th><th>Time (UTC)</th><th>Actor</th><th>Action</th>"
        "<th>Workload</th><th>Summary</th><th>Hash</th></tr>" + rows + "</table>"
        "<p class='tieback'>Tie-back (Compliance Officer &amp; Data Protection Officer (DPO)): "
        "auditable and compliant by design.</p></div>"
    )
    return layout("Trust · Compliance", body, "/trust")


def page_close() -> str:
    body = (
        "<div class='card'><h2>Close — the ask</h2>"
        "<p>We predicted a failure 21 days early, cut energy &amp; CO₂, and preserved "
        "expertise — all governed and auditable.</p>"
        "<p><strong>The ask:</strong> approve a time-boxed pilot on one line. "
        "See <code>documentation/work/07-presentation-deck.md</code>.</p>"
        "<p class='muted'>Q&amp;A: the data is synthetic for the demo; AI recommends, humans "
        "approve; uncertainty is always shown; personal data never leaves the EU.</p></div>"
    )
    return layout("Close", body, "/close")


# --- HTTP server -----------------------------------------------------------

class _DemoState:
    def __init__(self) -> None:
        self.audit = AuditLog()
        self.assistant = KnowledgeAssistant()


def _make_handler(state: _DemoState):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, html_text: str, code: int = 200) -> None:
            data = html_text.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:  # noqa: N802 (stdlib naming)
            parsed = urlparse(self.path)
            path = parsed.path
            query = parse_qs(parsed.query)
            if path == "/":
                self._send(page_overview())
            elif path == "/scene-a":
                day = int(query.get("day", ["84"])[0]) if query.get("day", ["84"])[0].isdigit() else 84
                self._send(page_scene_a(day, state.audit))
            elif path == "/scene-b":
                self._send(page_scene_b(state.audit))
            elif path == "/scene-c":
                self._send(page_scene_c(state.assistant, state.audit))
            elif path == "/trust":
                self._send(page_trust(state.audit))
            elif path == "/close":
                self._send(page_close())
            else:
                self._send(layout("Not found", "<div class='card'>Page not found.</div>", ""), 404)

        def do_POST(self) -> None:  # noqa: N802
            if urlparse(self.path).path != "/scene-c":
                self._send(layout("Not found", "<div class='card'>Not found.</div>", ""), 404)
                return
            length = int(self.headers.get("Content-Length", 0))
            form = parse_qs(self.rfile.read(length).decode("utf-8"))
            action = form.get("action", [""])[0]
            asked = answer = captured = None
            if action == "ask":
                asked = form.get("question", [""])[0]
                answer = state.assistant.answer(asked)
                state.audit.record(
                    "knowledge-assistant", "query", "C · Knowledge capture",
                    f"Q: {asked[:60]}; grounded={answer['grounded']}",
                )
            elif action == "capture":
                title = form.get("title", [""])[0]
                text = form.get("text", [""])[0]
                if title.strip() and text.strip():
                    captured = state.assistant.capture_tip(title, text)
                    state.audit.record(
                        "knowledge-assistant", "capture", "C · Knowledge capture",
                        f"Captured {captured['id']} (pending review)",
                    )
            self._send(page_scene_c(state.assistant, state.audit, asked, answer, captured))

        def log_message(self, *args) -> None:  # silence default logging
            return

    return Handler


def main() -> None:
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    state = _DemoState()
    server = ThreadingHTTPServer((host, port), _make_handler(state))
    print(f"NovaSteel Project Ignition demo — {SYNTHETIC_DATA_LABEL}")
    print(f"Open http://{host}:{port}/  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
