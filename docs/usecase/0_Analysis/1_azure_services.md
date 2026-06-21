# 🏭 UC12 – AI-Powered Steel Production Optimisation Platform

A practical scoring matrix for the AI-Powered Steel Production Optimisation Platform.

Use case reference: [docs/usecase/usecase.md](../usecase.md)

## 🎯 Scoring Method

Score **5** = critical, **4** = highly relevant, **3** = useful/selective, **2** = niche/optional, **1** = low relevance. In the matrix each score also carries an icon for quick scanning: ⭐ 5 · 🔷 4 · 🔹 3 · ▫️ 2 · ⬜ 1.

The score is an architecture recommendation for this use case, while the factual positioning of services (for example Microsoft Foundry being the unified AI platform, AI Services being exposed in Foundry, manufacturing focus on intelligent factories, and Foundry/Fabric/IoT alignment) is grounded in Microsoft sources and enterprise materials.

The **Over-Engineering Risk** column rates how likely it is that adopting the service would add disproportionate cost, complexity, or operational overhead relative to what UC12 actually needs (often because a simpler service or an already-listed service covers the same need). It is independent of relevance: a highly relevant service can still carry over-engineering risk if a lighter option would do, and a low-relevance service can be low risk if it is cheap and easy to drop. Ratings: 🟢 **Low** = proportionate, hard to over-build; 🟡 **Medium** = justify before adopting, watch for overlap; 🔴 **High** = likely overkill for this use case unless a specific requirement forces it.

The **Priority** column indicates *when* to adopt the service: 🚀 **Now** = foundational, bring in for the pilot/first phase; ⏭️ **Next** = add in a following phase once the core is proven; ⏳ **Later** = defer until a specific requirement justifies it; 🚫 **Excluded** = deliberately out of scope for this project (see the **Final Decision** section below).


## 🧭 UC12 Azure Service Relevance Matrix

| Category | Azure / Microsoft Service | Main Role in UC12 | Relevance Score | Priority | Over-Engineering Risk | Why it matters for steel production optimization |
| --- | --- | --- | :---: | :---: | :---: | --- |
| 🤖 AI platform | Microsoft Foundry | Core AI platform for agents, models, orchestration, grounding, observability | ⭐ 5 | 🚀 Now | 🟢 Low | Best fit for the AI control layer: production AI agents, model management, enterprise governance, evaluation, and grounded AI apps. |
| 🤖 AI platform | Foundry Agent Service | Energy optimization agent, knowledge agents, maintenance copilots | ⭐ 5 | 🚀 Now | 🟢 Low | Directly relevant for action-oriented agents that automate or assist production, maintenance, and operations workflows. |
| 🤖 AI platform | Foundry IQ | Grounding on procedures, maintenance docs, operator knowledge, reports | ⭐ 5 | 🚀 Now | 🟢 Low | Highly relevant for searchable operational knowledge, retrieval, and grounded responses for technicians/operators. |
| 🤖 AI platform | Foundry Tools / AI Services in Foundry | Speech, language, document, content tools for knowledge capture and industrial workflows | ⭐ 5 | 🚀 Now | 🟢 Low | Strong fit for operator interview capture, multilingual knowledge extraction, document understanding, and AI enrichment. |
| 🤖 AI platform | Foundry Local | Offline / plant-edge AI inference when connectivity or sovereignty constraints apply | 🔷 4 | ⏭️ Next | 🟡 Medium | Relevant where industrial sites require local inference, resilience, or limited connectivity. |
| 🤖 AI platform | Azure Machine Learning | Train/serve the physics-informed furnace RUL model + energy forecast; MLOps, model registry | ⭐ 5 | 🚫 Excluded | 🟢 Low | The capability is essential, but it is delivered **inside Microsoft Fabric (Data Science / ML)** to keep one unified platform — a separate Azure ML service is out of scope for this project. |
| 🧠 Models | Azure OpenAI / Foundry Models | LLMs for copilots, knowledge capture, reasoning, summarization, recommendations | ⭐ 5 | 🚀 Now | 🟢 Low | Core for GenAI use cases and agent reasoning on operational and knowledge workflows. |
| 🧠 Models | Third-party / OSS models in Foundry | Specialized models for optimized cost/performance or multilingual/edge scenarios | 🔷 4 | ⏭️ Next | 🟡 Medium | Useful when you want model choice optimization, cost control, or specialized domain behavior. |
| 🗣️ AI API layer | Azure AI Services (suite) | Unified API layer for speech, language, vision, document, safety | ⭐ 5 | 🚀 Now | 🟢 Low | Direct enabler for knowledge capture, OCR, multilingual operations, safety and extraction scenarios. |
| 🗣️ AI API layer | Speech | Capture and transcribe operator interviews, voice procedures, multilingual support | ⭐ 5 | 🚀 Now | 🟢 Low | Excellent fit for preserving retiring operator know-how and turning voice into searchable content. |
| 🗣️ AI API layer | Language | Summarization, entity extraction, procedural structuring, multilingual normalization | ⭐ 5 | 🚀 Now | 🟢 Low | Very relevant for transforming tacit knowledge into structured operational guidance. |
| 🗣️ AI API layer | Document Intelligence / Content Understanding | Parsing SOPs, maintenance reports, inspection forms, PDFs, logs | ⭐ 5 | 🚀 Now | 🟢 Low | Strong fit for extracting structured data from industrial and compliance documents. |
| 🗣️ AI API layer | Vision / OCR | Reading gauges, images, labels, scanned forms, visual process evidence | 🔷 4 | ⏭️ Next | 🟡 Medium | Useful for inspection and image-based process support if the program expands into visual QA. |
| 🗣️ AI API layer | Content Safety | Governance and safety filtering for GenAI interactions | 🔷 4 | 🚀 Now | 🟢 Low | Important for enterprise-safe deployment of generative assistants and knowledge systems. |
| 🔎 Retrieval | Azure AI Search | Vector / hybrid retrieval engine for RAG grounding | ▫️ 2 | ⏳ Later | 🟢 Low | Foundry IQ already provides managed grounding/retrieval over the procedure library (built on Azure AI Search), so a standalone Azure AI Search instance is optional here — adopt only if you need custom retrieval control beyond Foundry IQ. |
| 📊 Data & analytics | Microsoft Fabric | Unified analytics foundation / OneLake / BI / data products | ⭐ 5 | 🚀 Now | 🟢 Low | Strong candidate for the enterprise analytics backbone and for grounding AI on trusted industrial data. |
| 📊 Data & analytics | Azure Databricks | Advanced data engineering / feature engineering / ML / time-series analytics | 🔷 4 | 🚫 Excluded | 🟡 Medium | Out of scope — **Microsoft Fabric** (Data Engineering + Data Science) is the single analytics stack; we do not run a second engine. |
| 📊 Data & analytics | Azure Data Factory | Batch ingestion from MES/ERP/LIMS/historians and cross-country plants | ⭐ 5 | 🚀 Now | 🟢 Low | Very useful for orchestrating plant and enterprise data ingestion pipelines. |
| 📊 Data & analytics | Azure Data Lake Storage / OneLake pattern | Central storage for telemetry, quality, maintenance, and emissions data | ⭐ 5 | 🚀 Now | 🟢 Low | Essential data foundation for prediction, optimization, and governance. |
| 📊 Data & analytics | Azure Stream Analytics | Real-time event processing for process control and anomaly pipelines | 🔹 3 | 🚫 Excluded | 🟡 Medium | Out of scope — **Fabric Real-Time Intelligence** (Eventstreams/KQL) is the hot path. |
| 📊 Data & analytics | Azure Data Explorer | High-scale time-series / telemetry exploration and operational analytics | 🔷 4 | 🚫 Excluded | 🟡 Medium | Out of scope as a standalone cluster — **Fabric Real-Time Intelligence** already embeds the ADX/Eventhouse engine. |
| 🗄️ Databases | Azure SQL Database | Transactional app data, operator workflows, operational metadata | 🔷 4 | 🚀 Now | 🟢 Low | Good for application state, rules, audit trails, and operational workflow persistence. |
| 🗄️ Databases | Azure Cosmos DB | Low-latency app/session/memory store for AI apps and agents | 🔷 4 | ⏭️ Next | 🟡 Medium | Useful if the solution uses conversational state, globally distributed app data, or agent memory; can be overkill if a relational store suffices. |
| 🗄️ Databases | Azure Database for PostgreSQL Flexible Server | Operational apps, structured engineering data, backend platforms | 🔷 4 | 🚀 Now | 🟢 Low | Strong general-purpose database option for platform services and engineering applications. |
| 🗄️ Databases | Azure Database for MySQL Flexible Server | Optional app backend database | ▫️ 2 | ⏳ Later | 🔴 High | Viable but redundant with SQL/PostgreSQL; adding it usually fragments the data estate without benefit. |
| 🗄️ Databases | Azure Cache for Redis / Azure Managed Redis | Low-latency caching, session handling, agent acceleration | 🔷 4 | ⏭️ Next | 🟡 Medium | Useful for performance optimization of AI apps and APIs, but only justify once latency is a real constraint. |
| ⚙️ Compute | Azure Kubernetes Service (AKS) | Core platform for industrial AI apps, APIs, digital services, custom inference | 🔹 3 | ⏭️ Next | 🔴 High | Powerful but heavy to operate; for this use case Container Apps + Functions cover the workloads, so adopt AKS only if scale/control genuinely require it. |
| ⚙️ Compute | Azure Container Apps | Lightweight hosting for agents, APIs, event-driven services | ⭐ 5 | 🚀 Now | 🟢 Low | Primary host for the energy-dispatch agent microservice and AI/API wrappers — delivers the solution's compute without full AKS complexity. |
| ⚙️ Compute | Azure Functions | Event-driven logic, alerts, scoring triggers, integration glue | ⭐ 5 | 🚀 Now | 🟢 Low | Very strong for rule execution, event processing, and low-overhead automation. |
| ⚙️ Compute | Azure App Service | UI / portal / simple business apps | 🔹 3 | ⏭️ Next | 🟢 Low | Useful for web portals, but less central than AKS/Functions for heavy industrial event-driven patterns. |
| ⚙️ Compute | Azure Virtual Machines | Legacy integration, industrial middleware, vendor software hosting | 🔹 3 | ⏭️ Next | 🟡 Medium | The platform is greenfield cloud-native; VMs are only needed for OT-adjacent or legacy components and add patching/operations burden versus managed services. |
| ⚙️ Compute | Azure Batch | Large simulations / optimization runs / heavy compute jobs | 🔹 3 | ⏭️ Next | 🟡 Medium | Can help with batch simulation and optimization, but only worth it for genuinely heavy compute jobs. |
| 🌐 Networking | Azure Virtual Network (VNet) | Network isolation for data, AI, and industrial services | ⭐ 5 | 🚀 Now | 🟢 Low | Mandatory for secure industrial landing zones and private service integration. |
| 🌐 Networking | Azure Private Link | Private access to PaaS services from plants and central platform | ⭐ 5 | 🚀 Now | 🟢 Low | Very important for protecting telemetry, AI endpoints, and regulated workloads. |
| 🌐 Networking | Azure ExpressRoute | Private connectivity from plants/data centers to Azure | ⭐ 5 | 🚀 Now | 🟡 Medium | Highly relevant for reliable private OT/IT connectivity, but costly; VPN may suffice for smaller sites or early phases. |
| 🌐 Networking | Azure Firewall | Central egress/ingress control and segmentation | 🔷 4 | 🚀 Now | 🟢 Low | Strong baseline security service for regulated multi-country industrial environments. |
| 🌐 Networking | Azure Front Door | Global entry point for external apps/portals/APIs | 🔹 3 | ⏭️ Next | 🟡 Medium | Useful for globally exposed portals/APIs, but unnecessary if traffic stays regional/internal. |
| 🌐 Networking | Azure Application Gateway | Internal web/API ingress and WAF | 🔷 4 | 🚀 Now | 🟢 Low | Good for protected enterprise applications and regional ingress patterns. |
| 🌐 Networking | Azure Load Balancer | Internal service balancing | 🔹 3 | ⏭️ Next | 🟢 Low | Useful infrastructure element, but not a differentiator for the use case itself. |
| 🔐 Security & governance | Microsoft Entra ID | Identity for users, admins, apps, and potentially agent governance | ⭐ 5 | 🚀 Now | 🟢 Low | Core enterprise identity and access control layer for cross-country deployment. |
| 🔐 Security & governance | Azure Key Vault | Secrets, keys, certificates for AI/data/integration services | ⭐ 5 | 🚀 Now | 🟢 Low | Essential for secure industrial platform operations. |
| 🔐 Security & governance | Microsoft Defender for Cloud | Security posture and cloud workload protection | ⭐ 5 | 🚀 Now | 🟢 Low | Strongly recommended for enterprise and regulated industrial platforms. |
| 🔐 Security & governance | Microsoft Sentinel | SOC/SIEM and threat monitoring | 🔷 4 | ⏭️ Next | 🟡 Medium | Very valuable when integrated with wider SOC operations, but heavy to run if there is no SOC to consume it. |
| 🔐 Security & governance | Azure Policy | Governance, guardrails, region controls, service restrictions | ⭐ 5 | 🚀 Now | 🟢 Low | Especially relevant for GDPR, AI governance, and multi-country policy enforcement. |
| 🔐 Security & governance | Microsoft Purview | Data governance, lineage, classification, compliance | ⭐ 5 | 🚀 Now | 🟡 Medium | Critical for regulated data and AI governance, but full deployment is heavy; scope to required domains first. |
| 📈 Observability | Azure Monitor / Application Insights / Log Analytics | Logs, metrics, distributed traces, alerts, KQL, model-drift monitoring | ⭐ 5 | 🚀 Now | 🟢 Low | Core observability for the platform, the dispatch agent and MLOps (drift/quality) — and the operational/audit evidence the regulated use case requires. |
| 💾 Storage | Azure Blob Storage | Raw files, reports, archives, model input/output | ⭐ 5 | 🚀 Now | 🟢 Low | Foundational storage for unstructured industrial and AI data. |
| 💾 Storage | Azure Files | Shared file storage for lift-and-shift or plant apps | 🔹 3 | ⏭️ Next | 🟢 Low | Useful for compatibility scenarios, not the strategic analytics core. |
| 💾 Storage | Azure Disk Storage | Persistent disks for VMs/AKS stateful workloads | 🔹 3 | 🚀 Now | 🟢 Low | Infrastructure necessity, but not business-differentiating. |
| 💾 Storage | Azure Archive Storage | Long-term industrial record retention / compliance retention | 🔷 4 | ⏭️ Next | 🟢 Low | Relevant for audit, emissions evidence, and long retention periods. |
| 💾 Storage | Azure Data Lake Storage Gen2 | Large-scale analytical storage for telemetry/history/quality data | ⭐ 5 | 🚀 Now | 🟢 Low | One of the most important services for this use case's data estate. |
| 🔄 Integration & events | Azure Event Hubs | High-throughput telemetry ingestion from plants and sensors | ⭐ 5 | 🚀 Now | 🟢 Low | Very strong fit for streaming plant data at scale. |
| 🔄 Integration & events | Azure Service Bus | Reliable business/event messaging between apps and workflows | 🔷 4 | 🚀 Now | 🟡 Medium | Useful for decoupling operational services, but can overlap with Event Hubs/Event Grid—pick per messaging pattern. |
| 🔄 Integration & events | Azure Event Grid | Event-driven orchestration between services | 🔷 4 | 🚀 Now | 🟢 Low | Good for lightweight event fan-out and automation patterns. |
| 🔄 Integration & events | Azure Logic Apps | Workflow automation, enterprise connectors, operational actions | ⭐ 5 | 🚀 Now | 🟢 Low | Very relevant for integrating AI decisions with business systems and approvals. |
| 🔄 Integration & events | Azure API Management | Secure API facade, governance, throttling, AI API exposure | ⭐ 5 | 🚀 Now | 🟡 Medium | Important for exposing APIs securely at scale, but heavyweight for a handful of internal APIs early on. |
| 📡 IoT & edge | Azure IoT Hub | Device onboarding and telemetry ingestion from plant equipment | ⭐ 5 | 🚀 Now | 🟢 Low | Core service for getting furnace, mill, and utility telemetry into Azure. |
| 📡 IoT & edge | Azure IoT Edge | Edge processing near equipment / local scoring / resilient processing | ⭐ 5 | � Excluded | 🟢 Low | Out of scope to limit footprint — ingestion is **cloud-direct via Azure IoT Hub**; revisit only if edge autonomy becomes a hard requirement. |
| 📡 IoT & edge | Azure Digital Twins | Semantic model of plants, assets, processes, dependencies | 🔹 3 | ⏭️ Next | 🔴 High | Useful for furnace/mill topology and what-if analysis, but the use case relies on physics-informed signatures, not a twin; high modeling/maintenance effort, so adopt only when a twin-driven scenario is committed. |
| 📡 IoT & edge | Azure Sphere | Securing specific IoT devices/microcontroller estates | ▫️ 2 | ⏳ Later | 🔴 High | Only fits greenfield microcontroller estates; usually overkill for existing industrial OT hardware. |
| 🛠️ DevOps & engineering | GitHub Actions | CI/CD for apps, ML pipelines, infra, prompt assets | 🔷 4 | 🚀 Now | 🟢 Low | Strong modern DevOps option for platform delivery and repeatability. |
| 🛠️ DevOps & engineering | Azure DevOps | Alternative enterprise delivery stack | 🔹 3 | ⏭️ Next | 🟡 Medium | Relevant if the client already standardizes on ADO, but redundant alongside GitHub Actions. |
| 🛠️ DevOps & engineering | Azure Pipelines | CI/CD in Azure DevOps | 🔹 3 | ⏭️ Next | 🟡 Medium | Useful in ADO-centric enterprises, but redundant if GitHub Actions is the chosen CI/CD. |
| 🛠️ DevOps & engineering | Azure Boards / Repos / Artifacts | Project, code, and artifact management | ▫️ 2 | ⏳ Later | 🟡 Medium | Useful engineering support tools, but redundant where GitHub already covers code and work tracking. |
| 🏢 Hybrid & sovereign | Azure Arc | Unified management across cloud, plant edge, on-prem, multi-site | ⭐ 5 | � Excluded | 🟡 Medium | Out of scope — this is a **cloud-first, Fabric-centric** scope with no edge/on-prem control plane to manage. |
| 🏢 Hybrid & sovereign | Azure Local | Local infrastructure option for plant-hosted workloads | 🔹 3 | ⏭️ Next | 🟡 Medium | Can matter where workloads must stay local, but adds hybrid operations overhead. |
| 🏢 Hybrid & sovereign | Azure Stack | Specialized hybrid deployment scenarios | ▫️ 2 | ⏳ Later | 🔴 High | Lower priority and high operational cost; only for very specific disconnected/sovereign requirements. |
| 🏢 Hybrid & sovereign | Foundry Local | On-device / local AI execution | 🔷 4 | ⏭️ Next | 🟡 Medium | Good complement for edge AI scenarios needing local AI execution, but unnecessary if cloud inference is acceptable. |
| 💬 Communications | Azure Communication Services | Notifications, alerts, operator comms, workflow messaging | 🔹 3 | ⏭️ Next | 🟢 Low | Useful for alerting and workflow interaction, but not core to optimization itself. |
| 🎮 Gaming/media | Azure PlayFab | Gaming backend | ⬜ 1 | ⏳ Later | 🔴 High | Not relevant for this industrial use case. |

## 🔒 Final Decision — Scoped Service Set for This Project

> **Principle:** the goal is to **solve NovaSteel's four challenges**, not to showcase
> the Azure catalog. We deliberately concentrate the solution inside **Microsoft
> Fabric** and **Microsoft Foundry**, with a small set of **IoT** and platform
> services, to keep one unified, governable platform and avoid scattering.

### ✅ In scope — the focused core

- **Microsoft Fabric** — the single data-and-analytics platform: OneLake, Data
  Factory, Data Engineering, **Data Science (ML in Fabric)**, **Real-Time
  Intelligence** (Eventstreams/KQL), Power BI. It absorbs streaming ingestion,
  time-series, feature engineering and model training.
- **Microsoft Foundry** — the AI platform: Foundry Agent Service, Foundry IQ
  (grounding), Azure OpenAI / Foundry Models, and AI Services (Speech, Language,
  Document Intelligence, Content Safety).
- **IoT (minimal)** — **Azure IoT Hub** + **Azure Event Hubs** for cloud-direct
  plant telemetry ingestion (no edge runtime).
- **App & integration** — Azure Functions and Azure Container Apps (host the
  energy-dispatch agent).
- **Security, governance & ops** — Microsoft Entra ID, Key Vault, Azure Policy,
  Microsoft Purview, Defender for Cloud, Azure Monitor / Application Insights,
  VNet + Private Link, and ADLS Gen2 / OneLake + Blob Storage.

### 🚫 Explicitly excluded (to avoid scattering)

| Excluded service | Covered instead by |
| --- | --- |
| Azure Databricks | Microsoft Fabric — Data Engineering + Data Science |
| Azure Machine Learning | Microsoft Fabric — Data Science (ML, experiments, model registry) |
| Azure IoT Edge / IoT Operations | Azure IoT Hub (cloud-direct ingestion); no edge runtime in scope |
| Azure IoT Central | Azure IoT Hub + Microsoft Fabric (custom solution, not the SaaS app) |
| Azure Data Explorer | Fabric Real-Time Intelligence (embeds the ADX / Eventhouse engine) |
| Azure Stream Analytics | Fabric Real-Time Intelligence (Eventstreams / KQL) |
| Azure Arc | Not used — cloud-first, Fabric-centric scope; no hybrid control plane |

> These services remain in the matrix above for transparency (their capability
> relevance is real), but they are marked **🚫 Excluded** and are **not part of
> the delivered architecture**.

## ⭐ Shortlist: The Most Important Services for UC12

If you want the top architecture core, prioritize these first:

### 🥇 Tier 1 — Absolutely Central

- 🤖 Microsoft Foundry
- 🤖 Foundry Agent Service
- 📚 Foundry IQ
- 🧠 Azure OpenAI / Foundry Models
- 🗣️ Azure AI Services (especially Speech, Language, Document Intelligence / Content Understanding)
- 📊 Microsoft Fabric (OneLake · Data Engineering · **Data Science / ML** · Real-Time Intelligence · Power BI)
- 💾 Azure Data Lake Storage Gen2 / OneLake
- 📡 Azure IoT Hub
- 🔄 Azure Event Hubs
- ⚙️ Azure Functions
- 📦 Azure Container Apps
- 📈 Azure Monitor / Application Insights
- 🌐 Azure Private Link / VNet
- 🪪 Microsoft Entra ID
- 🔑 Azure Key Vault
- 📜 Azure Policy
- 🛡️ Microsoft Purview

### 🥈 Tier 2 — Strong Supporting Services

- 🚪 Azure API Management
- 🌐 Azure ExpressRoute
- 🔄 Logic Apps
- 🛡️ Defender for Cloud
- 👁️ Sentinel
- 💾 Blob Storage
- 🗄️ Cosmos DB / Redis (depending on app design)
- 📍 Foundry Local

### 🥉 Tier 3 — Optional / Contextual

- ☸️ AKS (only if scale/control exceeds Container Apps + Functions)
- 🧩 Azure Digital Twins (only if a twin-driven scenario is committed)
- 🔎 Azure AI Search (optional — Foundry IQ already provides grounding/retrieval)
- 🌐 App Service
- 🗄️ Azure SQL
- 🏢 Azure Local
- 💬 Azure Communication Services
- 📁 Azure Files
- 🗃️ Azure Archive
- 🧮 Azure Batch

## 🧩 Recommended Interpretation for This Use Case

### 🎯 Best Architectural Fit by Business Objective

| Business Objective | Best-fit Azure / Foundry Services |
| --- | --- |
| ⚡ Reduce energy consumption | IoT Hub + Event Hubs + Microsoft Fabric (Real-Time Intelligence + Data Science) + Foundry Agent Service (on Container Apps / Functions) |
| 🔥 Predict furnace lining degradation | IoT Hub + OneLake + Microsoft Fabric Data Science (physics-informed RUL) + Functions |
| ✅ Improve steel quality consistency | OneLake + Microsoft Fabric + Foundry models/agents |
| 🧑‍🏭 Preserve retiring operator knowledge | Speech + Language + Document Intelligence/Content Understanding + Foundry IQ + Foundry Agent Service |
| 🔐 Meet governance and EU regulatory needs | Entra ID + Key Vault + Private Link + Azure Policy + Purview + Defender for Cloud + Azure Monitor |
| 🌍 Operate across 4 countries / hybrid plants | VNet + Private Link + Microsoft Foundry + Microsoft Fabric |

## ✅ Overall Recommendation

For UC12, the most coherent Microsoft stack is:

- **📡 Plant connectivity & ingestion:** Azure IoT Hub + Event Hubs (cloud-direct) behind Private Link / VNet
- **📊 Unified data & ML platform:** Microsoft Fabric — OneLake + Data Engineering + **Data Science (ML in Fabric)** + Real-Time Intelligence + Power BI
- **🤖 AI layer:** Microsoft Foundry — Foundry Agent Service + Foundry IQ + Azure OpenAI / Foundry Models + AI Services
- **📚 Knowledge preservation:** Speech + Language + Document Intelligence / Content Understanding + Foundry IQ
- **🔐 Governance & compliance:** Entra ID, Key Vault, Private Link, Purview, Azure Policy, Defender for Cloud, Azure Monitor

That combination is the strongest fit for:

- ⚡ Energy optimization
- 🔧 Predictive maintenance
- ✅ Quality/yield improvement
- 🧑‍🏭 Operator knowledge retention
- 🌍 Cross-country governance