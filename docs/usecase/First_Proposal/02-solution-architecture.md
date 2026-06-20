# 02 — Solution Architecture

**Project Ignition** — Azure reference architecture for the NovaSteel AI
production-optimization platform.

> Designed against the **Azure Well-Architected Framework** (Reliability,
> Security, Cost Optimization, Operational Excellence, Performance Efficiency)
> and the **Cloud Adoption Framework**. Default region: **Sweden Central**, with
> **West Europe** and **Germany West Central** as alternates for EU data residency.

**Primary target roles:** COO (1), Head of Manufacturing / VP Operations (2),
Plant Director / Site Manager (3), CTO / Head of IT/OT (4), CISO (8),
Chief Data Officer (12), AI Architect / Digital Twin Architect (14),
OT Engineer / Automation Engineer (15).

---

## 1. Architecture at a glance

```mermaid
flowchart LR
    subgraph OT["Plant floor (OT / Purdue L0-L2)"]
        S["Sensors: thermal, vibration,\ngas, energy meters"]
        H["Historian / SCADA / MES"]
    end

    subgraph EDGE["Edge (Purdue L3 / Azure Arc)"]
        IOA["Azure IoT Operations\n(MQTT broker, data flows)"]
        AML_EDGE["Edge inference\n(furnace alerts)"]
    end

    subgraph CLOUD["Azure (EU regions)"]
        subgraph INGEST["Ingest & stream"]
            IOT["IoT Hub / Event Hubs"]
            RTI["Fabric Real-Time Intelligence"]
        end
        subgraph DATA["Data platform — Microsoft Fabric / OneLake"]
            BRONZE["Bronze (raw)"]
            SILVER["Silver (clean)"]
            GOLD["Gold (features / marts)"]
        end
        subgraph AI["AI & ML"]
            AML["Azure Machine Learning\n(RUL & energy models, MLOps)"]
            AOAI["Azure AI Foundry + Azure OpenAI\n(knowledge assistant)"]
            SRCH["Azure AI Search (RAG)"]
        end
        subgraph APP["Optimization & experience"]
            DISP["Energy-dispatch agent\n(Functions / Container Apps)"]
            BI["Power BI / Fabric dashboards"]
            COPILOT["Teams + Copilot for operators"]
        end
        subgraph GOV["Cross-cutting"]
            ENTRA["Entra ID"]
            KV["Key Vault"]
            MON["Azure Monitor"]
            PURVIEW["Microsoft Purview"]
            DEF["Defender for Cloud / IoT"]
        end
    end

    EXT["Electricity spot prices &\ngrid carbon intensity"]

    S --> H --> IOA --> IOT --> RTI --> BRONZE --> SILVER --> GOLD
    GOLD --> AML --> DISP
    AML --> AML_EDGE
    GOLD --> SRCH --> AOAI --> COPILOT
    EXT --> DISP
    DISP --> BI
    AML --> BI
    AOAI --> BI
```

> **Editable diagram:** an Excalidraw version of the Fabric + IoT view is at
> [`../../business/images/fabric-iot-architecture.excalidraw`](../../business/images/fabric-iot-architecture.excalidraw)
> — open it in [aka.ms/excalidraw](https://aka.ms/excalidraw) to edit or export.

![NovaSteel Microsoft Fabric + IoT reference architecture](../../business/images/fabric-iot-architecture.png)

## 2. Layer-by-layer

### 2.1 Plant floor (OT) and edge

- **Sources:** thermal cameras/pyrometers, vibration, off-gas analyzers, energy
  meters, plus the **historian/SCADA/MES**.
- **Azure IoT Operations** on an **Azure Arc**-enabled edge cluster provides an
  MQTT broker and data flows. The OT/IT boundary follows the **Purdue model**;
  ingestion is **one-way out** of the plant for safety.
- **Edge inference** keeps furnace alerts low-latency and resilient to
  connectivity loss.

### 2.2 Ingestion & streaming

- **IoT Hub / Event Hubs** for device telemetry; **Fabric Real-Time
  Intelligence** for streaming analytics and hot-path alerting.

### 2.3 Data platform (Microsoft Fabric / OneLake)

- **Medallion** architecture: **Bronze** (raw), **Silver** (validated, modelled),
  **Gold** (curated features and marts) on **OneLake / ADLS Gen2**.
- Lineage and classification through **Microsoft Purview**.

### 2.4 AI & ML

- **Azure Machine Learning** trains and serves the **physics-informed RUL model**
  (furnace lining) and the **energy-optimization model**, with full **MLOps**
  (registry, CI/CD, drift & quality monitoring).
- **Azure AI Foundry + Azure OpenAI** power the **knowledge-capture assistant**,
  grounded with **Azure AI Search** (RAG) over the procedure library.

### 2.5 Optimization & experience

- **Energy-dispatch agent** (Azure Functions / Container Apps) consumes
  day-ahead spot prices and grid carbon intensity and recommends scheduling.
- **Power BI / Fabric dashboards** for executives and engineers; **Teams +
  Copilot** surface guidance to operators.

### 2.6 Cross-cutting (security, governance, operations)

- **Microsoft Entra ID** (identity, conditional access), **Key Vault** (secrets),
  **Azure Monitor / Log Analytics** (observability), **Microsoft Purview**
  (governance & lineage), **Defender for Cloud / Defender for IoT** (posture &
  OT threat detection). Private networking via **VNet + Private Endpoints**.

### 2.7 Microsoft Fabric estate (detail)

The data platform above is realised on **Microsoft Fabric** over **OneLake** —
one logical copy of data, many engines (hot, warm and cold paths). The full
component-by-component design is in
[02a — Fabric + IoT architecture](02a-fabric-iot-architecture.md); in brief, the
seven Fabric capability layers map to NovaSteel as:

| Layer | Fabric / IoT components | Role at NovaSteel |
| ----- | ----------------------- | ----------------- |
| Foundation & storage | OneLake, Shortcuts, Mirroring, OneLake Catalog | One governed copy of plant + ERP + market data |
| Data engineering | Data Factory, Pipelines, Dataflows Gen2, Spark notebooks | Physics-informed Gold features, reproducible |
| Data science & AI | Data Science, Experiments/Models, AI functions, Copilot, Fabric data agents | RUL + energy forecast + NL data agent |
| Warehouse & DB | Fabric Data Warehouse, SQL database, SQL Analytics Endpoint | Governed finance / emissions / quality marts |
| Real-Time Intelligence | Eventstreams, Eventhouse/KQL, Activator, Anomaly detection, Digital twin builder | Sub-second furnace alerts, live telemetry (IoT hot path) |
| Business intelligence | Power BI, Direct Lake | Always-fresh exec / engineer / ops dashboards |
| Governance & admin | Purview, Entra, Fabric Admin, Git/DevOps | Lineage, EU residency, EU AI Act traceability |

The **edge inference / Azure ML** split is unchanged: Fabric Data Science owns
feature engineering, experiment tracking and batch scoring; **Azure ML** owns the
production registry, CI/CD, drift monitoring and **edge serving** of the hot-path
furnace model.

## 3. Mapping services to business outcomes

| Outcome | Primary services | How |
| ------- | ---------------- | --- |
| 21-day furnace warning (O3) | IoT Operations, AML, edge inference | RUL model on thermal/vibration features, alerted on the hot path |
| −14% energy (O1) | Dispatch agent, AML, Event Hubs | Schedule energy-intensive steps around spot price / carbon |
| −22% CO₂ (O2) | Dispatch agent, Fabric, Purview | Carbon-aware scheduling + auditable emissions data |
| +8% yield (O4) | Fabric (Gold features), AML, Power BI | Process-parameter recommendations + SPC dashboards |
| Knowledge capture | AI Foundry, Azure OpenAI, AI Search | Interview assistant + RAG procedure library |

## 4. Well-Architected highlights

- **Reliability:** edge buffering and inference survive cloud disconnects;
  multi-zone services; IaC for reproducible environments.
- **Security:** EU residency, private endpoints, Entra ID, least privilege,
  Defender, secrets in Key Vault, OT segmentation.
- **Cost optimization:** consumption-based services, Fabric capacity sizing,
  reservations/savings plans as levers (see [05](05-cost-estimate.md)).
- **Operational excellence:** MLOps + DevOps, full observability, runbooks.
- **Performance efficiency:** hot path at the edge/stream, batch training in the
  cloud.

## 4a. Architecture & design patterns

The design is built from explicit, well-known patterns so it is modular,
testable and scalable:

| Pattern | Where it is applied |
| ------- | ------------------- |
| **Medallion (Bronze/Silver/Gold)** | OneLake data platform — separation of raw, conformed and curated data |
| **Lambda / hot-warm-cold paths** | Real-Time Intelligence (hot furnace alerts), warm analytics, cold ML training on one lake |
| **Event-driven ingestion** | IoT Hub → Event Hubs → Eventstreams; decoupled producers/consumers |
| **Edge-cloud split (CQRS-like)** | Low-latency inference at the edge; heavy training/serving in the cloud |
| **Retrieval-Augmented Generation (RAG)** | Knowledge assistant grounds answers in the procedure library via AI Search |
| **Agent + human-in-the-loop** | Energy-dispatch agent recommends; an operator confirms before action |
| **MLOps (registry + CI/CD + monitoring)** | Versioned models, gated promotion, drift detection |
| **Hub-and-spoke + landing zone** | Subscriptions/resource groups per environment with policy guardrails |
| **Strangler-style rollout** | Pilot one line, then incrementally onboard lines/sites without big-bang cutover |

## 4b. Monitoring & observability

Observability is first-class, not an afterthought:

- **Structured logging & tracing** — all services emit structured logs and
  distributed traces to **Application Insights / Log Analytics**; correlation IDs
  follow a recommendation from sensor → model → dashboard → operator decision.
- **Platform & app metrics** — **Azure Monitor** dashboards and **KQL** queries
  track ingestion lag, hot-path alert latency, API health, and Fabric capacity
  utilisation; **alerts** fire on SLO breaches.
- **Model monitoring (MLOps)** — Azure ML tracks **data drift, prediction drift,
  and quality**; degradation triggers retraining with approval gates.
- **GenAI evaluation** — groundedness, relevance and citation-rate are monitored
  continuously for the knowledge assistant.
- **Audit & lineage** — every prediction, recommendation and human approval is
  logged immutably; **Purview** captures end-to-end lineage for EU AI Act
  traceability.

## 5. Environments

`Dev → Test → Pilot (prod-like, one line) → Production (multi-site)`, all
provisioned via **Infrastructure as Code** (Bicep/Terraform) with separated
subscriptions/resource groups and policy guardrails (Azure Policy).

## 6. Key assumptions

- Historian exposes the needed tags; edge cluster can be deployed plant-side.
- EU regions satisfy residency; external price/carbon feeds are licensed.
- These are **demo/reference assumptions** to be confirmed in a design workshop.
