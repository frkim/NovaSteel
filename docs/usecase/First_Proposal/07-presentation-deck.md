# 07 — Presentation Deck

**Project Ignition** — slide-by-slide executive narrative for the jury
(COO · Head of Manufacturing / VP Operations · Head of Quality ·
Head of Sustainability / ESG · Compliance Officer · Data Protection Officer (DPO) · CFO).

> Format per slide: **Title · Key message · 3 bullets · Visual · Speaker notes.**
> Target length: ~16 slides for a crisp 30–40 minute executive session.
> Arc: *Context → Challenge → Vision → Solution → Proof → Value → Ask.*

---

## Slide 1 — Title

- **Key message:** NovaSteel + Microsoft: igniting AI-optimized steelmaking.
- Project Ignition · AI-Powered Steel Production Optimization Platform.
- Presented to the executive jury.
- Microsoft Cloud Solution Engineer — Cloud & AI.
- *Visual:* NovaSteel furnace + Azure mark.
- *Notes:* Set the tone — business outcomes, not technology.

## Slide 2 — NovaSteel today (Context)

- **Key message:** A century of metallurgy across four EU countries.
- Integrated producer: blast/oxygen/electric-arc furnaces + rolling mills.
- Customers: automotive, construction, energy, advanced manufacturing.
- Regulatory context: GDPR · EU AI Act · EU directives.
- *Visual:* map of LU/DE/BE/ES.
- *Notes:* Establish scale and stakes.

## Slide 3 — The challenge (Challenge)

- **Key message:** Four forces erode margin and resilience.
- Energy = 35% of cost, no real-time optimization; CO₂ under ETS pressure.
- Furnace-lining failures are unpredictable — **€8M each**.
- Quality inconsistency + retiring operators losing know-how.
- *Visual:* four-icon problem grid.
- *Notes:* Each juror sees their pain here.

## Slide 4 — The vision (Vision)

- **Key message:** Turn plant data into three better decisions.
- **Predict** failures · **Optimize** energy/CO₂ · **Capture** expertise.
- AI advises; people decide.
- Built on Azure, EU-resident, compliant by design.
- *Visual:* predict / optimize / capture triptych.

## Slide 5 — Target outcomes (Value preview)

- **Key message:** Concrete, measurable targets.
- Energy **−14%** · CO₂ **−22%**.
- Furnace warning **21 days** · High-grade yield **+8%**.
- Proven first on a time-boxed pilot.
- *Visual:* 4 KPI tiles.
- *Notes:* Promise to prove, not just claim.

## Slide 6 — Solution architecture (Solution)

- **Key message:** A clean path from sensor to decision on Azure.
- Cloud-direct IoT Hub → Fabric/OneLake → Fabric Data Science & Microsoft Foundry.
- Dashboards + operator Copilot; secure, governed, EU-resident.
- See [02 — Architecture](02-solution-architecture.md).
- *Visual:* the Mermaid architecture diagram.

## Slide 7 — AI workload A: predict furnace failures

- **Key message:** 21-day warning avoids €8M events.
- Physics-informed RUL model on thermal/vibration signatures.
- Real-Time Intelligence → resilient, low-latency cloud alerts.
- Proven by back-testing historical failures.
- *Visual:* lining wear curve with 21-day alert marker.

## Slide 8 — AI workload B: optimize energy & CO₂

- **Key message:** Schedule around price and carbon.
- Carbon-aware dispatch vs. spot prices → **−14% energy, −22% CO₂**.
- Recommendations; operator confirms.
- *Visual:* price/carbon curve with shifted load.

## Slide 9 — AI workload C: capture expertise

- **Key message:** Keep knowledge when operators retire.
- GenAI interviews → searchable, cited procedure library (RAG).
- Spreads best-known methods → supports **+8% yield**.
- *Visual:* Teams/Copilot assistant mock.

## Slide 10 — Quality (for the Head of Quality)

- **Key message:** Tighter process, certified consistency.
- SPC + Cp/Cpk: reduce variability, not just the mean.
- Full traceability (heat → coil); AI advises, metallurgists decide.
- *Visual:* narrowing SPC distribution.

## Slide 11 — Sustainability & brand (for the Head of Sustainability / ESG)

- **Key message:** A verifiable decarbonization story.
- **−22% CO₂**, auditable data → credible customer & ESG narrative.
- Differentiator for automotive customers.
- *Visual:* CO₂ downtrend + sustainability badge.

## Slide 12 — The numbers (for the CFO)

- **Key message:** Sub-12-month payback (illustrative).
- Build ~€0.6–1.1M · Run ~€0.3–0.7M/yr · Energy benefit ~€24.5M/yr (illustrative).
- Conservative/base/optimistic; pilot proves the % first.
- See [05 — Cost & ROI](05-cost-estimate.md).
- *Visual:* cost-vs-benefit bar + payback marker.

## Slide 13 — Trust & compliance (for the Compliance Officer and Data Protection Officer (DPO))

- **Key message:** Compliant and auditable by design.
- GDPR + EU AI Act mapped to controls; EU residency; human oversight.
- Purview lineage, Entra ID, Defender, full audit trail.
- See [06 — Security & compliance](06-security-compliance.md).
- *Visual:* control-mapping table excerpt.

## Slide 14 — How we deliver (Proof of plan)

- **Key message:** Gated, low-risk delivery.
- Mobilize → Foundation → Pilot → Review → Scale; demo every 2 weeks.
- SMEs embedded; decisions at each gate.
- See [04 — Implementation plan](04-implementation-plan.md).
- *Visual:* the roadmap gantt.

## Slide 15 — Live demo

- **Key message:** See it work.
- 21-day furnace alert · energy optimization · knowledge assistant.
- Synthetic data; real platform. See [08 — Demo script](08-demo-script.md).
- *Visual:* dashboard screenshot/placeholder.

## Slide 16 — The ask (Ask)

- **Key message:** Approve a time-boxed pilot on one line.
- Approve pilot + data access (under DPIA) + cross-functional team.
- Decision gate at pilot end to scale across four sites.
- **Per persona "so what":**
  - COO: fewer €8M failures, higher uptime.
  - Head of Manufacturing / VP Operations: scalable cross-site operating model.
  - CFO: sub-12-month payback, de-risked.
  - Head of Quality: +8% yield, full traceability.
  - Head of Sustainability / ESG: −22% CO₂ story.
  - Compliance Officer + Data Protection Officer (DPO): GDPR + EU AI Act, audit-ready.
- *Visual:* single CTA.

---

## Appendix slides (optional, for Q&A)

- A1 — Detailed architecture & Well-Architected mapping.
- A2 — MLOps & Responsible AI.
- A3 — Cost assumptions table.
- A4 — EU AI Act risk classification.
- A5 — Risk register & mitigations.
