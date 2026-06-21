# 08 — Demo Script

**Project Ignition** — live walkthrough that proves the three AI workloads using
**synthetic, clearly-labelled data** (no real plant or personal data).

> Goal: in ~12 minutes, show the jury the **21-day furnace alert**, **energy/CO₂
> optimization**, and the **knowledge assistant**, each tied back to its KPI.

---

## 0. Before the room (setup checklist)

- [ ] Pilot/demo environment reachable; dashboards loaded.
- [ ] Synthetic datasets generated: furnace telemetry with injected degradation;
      illustrative spot-price/carbon series; synthetic SOP corpus.
- [ ] Knowledge assistant grounded (Foundry IQ) and responding.
- [ ] Fallback: recorded screen capture in case of connectivity issues.
- [ ] On every screen, a visible "**Synthetic demo data**" label.

## 1. Opening (1 min)

- Recap the four targets (−14% energy, −22% CO₂, 21-day warning, +8% yield).
- "Everything you'll see runs on the real Azure platform with synthetic data."

## 2. Scene A — Predict a furnace failure (4 min)

1. Open the **furnace health dashboard**; show live thermal/vibration telemetry.
2. Fast-forward the synthetic timeline; the **RUL model** crosses the threshold
   and raises a **21-day advance alert** with an uncertainty band.
3. Click the alert → show **drivers** (thermal gradient, wear-rate proxy) and the
   recommended inspection window.
4. **Tie-back (COO):** "This is the €8M event we now see 21 days early."

## 3. Scene B — Optimize energy & CO₂ (3 min)

1. Open the **energy-dispatch view**; show day-ahead **spot price** and **grid
   carbon** curves.
2. Show the optimizer **shifting energy-intensive steps** into low-price /
   low-carbon windows, within production constraints.
3. Display the before/after **€/ton and tCO₂/ton** deltas → **−14% / −22%**.
4. **Tie-back (CFO & Head of Sustainability / ESG):** cost down and a
   verifiable carbon story.

## 4. Scene C — Capture operator expertise (3 min)

1. Open the **knowledge assistant** in Teams/Copilot.
2. Ask: *"How do we stabilise surface quality on grade X during a cold start?"*
3. Show a **grounded answer with citations** to the procedure library.
4. Show the **interview mode** capturing a new tip into the library.
5. **Tie-back (Head of Quality):** best-known methods, preserved and spread →
   supports +8% yield; **AI advises, metallurgists decide**.

## 5. Trust moment — compliance (1 min)

- Open **audit/lineage** (Purview/Monitor): every prediction, recommendation and
  human approval is logged.
- "EU-resident, GDPR + EU AI Act aligned, human-in-the-loop."
- **Tie-back (Compliance Officer & Data Protection Officer (DPO)):** auditable and compliant by design.

## 6. Close (30 sec)

- Recap: predicted a failure, cut energy & CO₂, preserved expertise — all
  governed.
- Transition to **[the ask](07-presentation-deck.md)**: approve the pilot.

---

## Role tie-back cheat sheet

| Scene | COO | CFO | Head of Quality | Head of Sustainability / ESG | Compliance Officer & Data Protection Officer (DPO) |
| ----- | --- | --- | --------------- | ----------------------------- | ----------------------------------------------- |
| A Predict | ✅ uptime | ✅ avoided €8M | — | — | audit log |
| B Energy | reliability | ✅ −14% cost | — | ✅ −22% CO₂ | reporting integrity |
| C Knowledge | continuity | productivity | ✅ +8% yield | brand narrative | GDPR/DPIA |
| Trust | observability | risk | traceability | trusted ESG metrics | ✅ AI Act |

## Q&A landmines & answers

- *"Is the data real?"* — Synthetic for the demo; the pilot proves it on real
  historian data.
- *"Will AI control the furnace?"* — No; recommendations only, human-approved.
- *"What if the model is wrong?"* — Uncertainty is shown; alerts are reviewed;
  models are monitored for drift and back-tested.
- *"Where does our data live?"* — EU Azure regions; personal data never leaves
  the EU.
