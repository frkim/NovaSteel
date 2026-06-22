# 12. ⚙️ Technology Stack

*Audience: CTO / Head of IT/OT (4), AI Architect (14), Head of Data Science / ML Lead
(13), OT Engineer (15), CISO (8).*

This is the concrete **Azure / Microsoft Fabric / Foundry** mapping behind the
architecture in [Section 5](05-target-architecture.md). It reflects the **Final
Decision** in [`../1_azure_services.md`](../1_azure_services.md): a **single,
consolidated stack** — excluded services (Azure ML, Databricks, IoT Edge/Operations,
Arc, AKS) are intentionally absent.

---

## 12.1 Azure cloud services mapping (by capability)

| Capability | Service | Role |
|-----------|---------|------|
| **IoT ingestion** | **Azure IoT Hub** | Cloud-direct, per-device secure telemetry (one-way out, Purdue) |
| **Streaming** | **Azure Event Hubs** | High-throughput sensor & external market streams |
| **Data platform** | **Microsoft Fabric / OneLake** | Single governed medallion lakehouse (Bronze/Silver/Gold) |
| **Real-time** | **Fabric Real-Time Intelligence** | Eventstreams / KQL / Activator — sub-second furnace alerts |
| **Data engineering** | **Data Factory, Dataflows Gen2, Spark** | Ingestion + physics-informed features |
| **ML / MLOps** | **Fabric Data Science** | MLflow, registry, endpoints, batch & live scoring, drift |
| **GenAI / agents** | **Microsoft Foundry** | Agent Service, Foundry IQ (RAG), models |
| **LLM** | **Azure OpenAI / Foundry Models (GPT-5)** | Reasoning, summarisation, extraction; `text-embedding-3-large` |
| **AI Services** | **Speech / Language / Document Intelligence / Content Safety** | Operator interview capture & structuring |
| **Optimisation compute** | **Azure Functions / Container Apps** | Energy-dispatch MILP/heuristic agent (event-triggered) |
| **Workflow** | **Azure Logic Apps** | Approvals / human-in-the-loop orchestration |
| **BI** | **Power BI (Direct Lake)** | Always-fresh exec / engineering / ops dashboards |
| **Experience** | **Teams + Copilot** | Operator knowledge assistant with citations |

## 12.2 Cloud-direct ingestion architecture (no edge runtime)

- **Azure IoT Hub** ingests telemetry **cloud-direct**, one-way out of the plant —
  **no edge runtime** (Azure IoT Edge/Operations explicitly excluded).
- **Azure Event Hubs** handles high-throughput sensor and **market feeds** (spot
  price, grid carbon).
- **Hot path:** IoT Hub → Real-Time Intelligence (Eventstreams/KQL) → Activator
  alerts and a **Fabric ML endpoint** for low-latency furnace scoring.
- **Batch path:** MES/ERP via Data Factory → OneLake medallion.

## 12.3 Data platform (Microsoft Fabric)

| Component | Purpose |
|-----------|---------|
| **OneLake** | One governed copy; medallion Bronze/Silver/Gold |
| **Shortcuts** | Zero-copy access to existing stores |
| **Mirroring** | SAP/ERP data without duplication |
| **OneLake Catalog** | Discovery, endorsement, classification |
| **Data Factory / Dataflows Gen2 / Spark** | Orchestration, cleansing, feature engineering |
| **Real-Time Intelligence** | Eventstreams, Eventhouse/KQL DB, Activator, anomaly detection, digital-twin builder |
| **Fabric Data Warehouse / SQL endpoint** | Governed finance/emissions/quality marts |
| **Power BI Direct Lake** | Dashboards without import/refresh |

## 12.4 AI services (Microsoft Foundry + Fabric Data Science)

| Component | Purpose |
|-----------|---------|
| **Foundry Agent Service** | Knowledge & maintenance copilots; agent orchestration |
| **Foundry IQ** | Grounding / RAG over the procedure library |
| **Azure OpenAI / Foundry Models** | **GPT-5** reasoning; `text-embedding-3-large` vectors |
| **AI Services** | Speech (interviews), Language (extraction), Document Intelligence (SOP parsing), Content Safety |
| **Fabric Data Science** | Physics-informed RUL + energy-forecast models; MLflow registry; Fabric ML endpoints; drift monitoring |

## 12.5 Security, governance & networking

| Layer | Service | Role |
|-------|---------|------|
| **Identity** | **Entra ID** | SSO, conditional access, PIM, least-privilege by domain |
| **Secrets** | **Key Vault** | BYOK, managed identities |
| **Policy** | **Azure Policy** | EU region pinning, service guardrails |
| **Governance** | **Microsoft Purview** | Lineage (sensor → feature → model → report), classification |
| **Security posture** | **Defender for Cloud + Defender for IoT** | Posture, OT threat detection |
| **Networking** | **VNet + Private Link, ExpressRoute/VPN, Azure Firewall** | Private PaaS, OT/IT connectivity, segmented egress |

## 12.6 Observability & monitoring tools

| Concern | Tool | Signal |
|---------|------|--------|
| **Logs & traces** | **Azure Monitor / Application Insights** | Structured logging, distributed traces |
| **Model health** | Azure Monitor + Fabric DS | Data drift, model quality, retraining triggers |
| **SLOs & alerts** | Azure Monitor | Latency/availability of furnace alerting hot path |
| **Audit trail** | Log Analytics (immutable) + Purview | Every prediction/recommendation/approval logged |

> **Monitoring is a rubric-graded capability** — the platform implements **structured
> logging and relevant metrics** (model drift, SLOs, audit completeness), not just
> infrastructure health.

## 12.7 Environments & IaC

- **Environments:** Dev → Test → **Pilot (one line, prod-like)** → Prod (multi-site).
- **Infrastructure as Code:** **Bicep / Terraform**; **CI/CD** via **GitHub Actions /
  Azure DevOps**.
- **Regions:** **Sweden Central** primary; **West Europe**, **Germany West Central**
  alternates — all EU.

## 12.8 Why this stack (decision summary)

| Lever | Decision | Benefit |
|-------|----------|---------|
| **Consolidation** | One Fabric data plane + one Foundry AI plane | Less sprawl, one governance fabric |
| **Safety** | Cloud-direct IoT (no edge) | Smaller plant-side attack surface |
| **Trust** | Physics-informed + uncertainty + citations | Explainable, defensible AI |
| **Compliance** | EU regions, Purview lineage, AI Act file | Auditable by design |
| **Cost control** | Fabric capacity right-sizing, reservations, FinOps | Predictable, optimisable run cost |

---

*Continue to → [13. Risks & Mitigation](13-risks-mitigation.md)*
