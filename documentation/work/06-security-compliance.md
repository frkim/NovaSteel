# 06 — Security & Compliance

**Project Ignition** — GDPR, EU AI Act, sector directives and Microsoft
Responsible AI for the NovaSteel platform.

> This is a **structured compliance position** for the demo, not legal advice.
> Validate with NovaSteel's legal/DPO and a qualified AI Act assessor.

---

## 1. Regulatory landscape

NovaSteel operates in **Luxembourg, Germany, Belgium and Spain**, so the platform
must satisfy:

- **GDPR** — any personal data (operator interviews, identities, access logs).
- **EU AI Act** — risk-based obligations per AI system.
- **EU ETS & sector directives** — integrity of emissions reporting.
- **Microsoft Responsible AI Standard** — engineering practice.

## 2. EU AI Act risk classification (per workload)

| Workload | Likely risk tier | Rationale | Key obligations applied |
| -------- | ---------------- | --------- | ----------------------- |
| A — Furnace predictive maintenance | **Limited / minimal** | Industrial asset prediction; no impact on persons' rights; human-confirmed action | Risk mgmt, data governance, logging, accuracy/robustness, human oversight |
| B — Energy-dispatch optimization | **Limited / minimal** | Operational scheduling; recommendations only | Same as above; ensure emissions reporting unaffected |
| C — GenAI knowledge assistant | **Limited (transparency)** | Interacts with people; processes personal data | Transparency (users know it's AI), GDPR, content grounding & review |

> No workload is intended as a **high-risk** AI system, but the classification is
> documented and revisited if scope changes (e.g. automated control actions).

## 3. GDPR / DPIA checklist

- [ ] **Lawful basis** identified for operator interview data (e.g. legitimate
      interest / consent) and documented.
- [ ] **Data minimisation** — capture knowledge, not unnecessary personal data;
      prefer anonymisation/pseudonymisation.
- [ ] **DPIA** completed before processing interview data.
- [ ] **EU residency** — data and embeddings stay in EU regions.
- [ ] **Retention & deletion** policy defined; right-to-erasure supported.
- [ ] **Transparency** notice to operators; purpose limitation.
- [ ] **Access controls & audit** via Entra ID; logs retained.
- [ ] **Processor terms** (Microsoft DPA) in place.

## 4. Control mapping (obligation → control → owner → evidence)

| Obligation | Azure control | Owner | Evidence |
| ---------- | ------------- | ----- | -------- |
| Data residency | EU regions, Policy geo-restrictions | Architect | Azure Policy compliance report |
| Identity & least privilege | Entra ID, RBAC, Conditional Access, PIM | Platform | Access reviews |
| Secrets management | Key Vault, managed identities | Platform | Key Vault audit |
| Data governance & lineage | Microsoft Purview | Data lead | Lineage & classification |
| Security posture & OT threats | Defender for Cloud / Defender for IoT | Security | Secure Score, alerts |
| Logging & auditability | Azure Monitor / Log Analytics, immutable logs | Ops | Retained audit trail |
| Model transparency | Model cards, data sheets, RAG citations | AI lead | Model card repository |
| Human oversight | Human-in-the-loop gates in workflows | Process owner | Approval records |
| Emissions integrity | Read-only feed; no AI write-back to ETS reports | Compliance | Reporting reconciliation |

## 5. Microsoft Responsible AI assessment

| Principle | How it is met |
| --------- | ------------- |
| Fairness | Knowledge assistant evaluated for bias; diverse failure modes in RUL back-test |
| Reliability & safety | Uncertainty shown; **human confirms** any safety/emissions/personnel action |
| Privacy & security | EU residency; synthetic/anonymised demo data; DPIA |
| Inclusiveness | Operator-friendly UX in Teams; multilingual support possible |
| Transparency | Users informed it is AI; explainable RUL drivers; cited answers |
| Accountability | Named owners; AI Act risk file; audit logs; steering oversight |

## 6. Compliance Officer & Data Protection Officer (DPO) Q&A (plain language)

- **"Where is our data?"** — In EU Azure regions; personal data never leaves the
  EU.
- **"Is this a high-risk AI system?"** — Based on current scope, no; we document
  the assessment and revisit if we add automated control.
- **"Can the AI mis-report emissions?"** — No; emissions reporting data is
  read-only to the AI; optimization recommendations are separate and
  human-approved.
- **"Can we audit decisions?"** — Yes; every prediction, recommendation and human
  approval is logged with lineage in Purview/Monitor.
- **"What about retiring operators' data?"** — Covered by a DPIA, lawful basis,
  minimisation, retention limits and erasure support.
- **"How are DPO obligations enforced?"** — Through DPIA sign-off, documented
  retention/deletion controls, data-subject rights handling, and EU-only data
  residency for personal data.

## 7. Open items to confirm

- Final lawful basis & DPIA sign-off with the Data Protection Officer (DPO).
- AI Act classification reviewed by a qualified assessor.
- Data-processing agreement and sub-processor list confirmed.
