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
| 📊 Data & analytics | Azure Data Factory | Batch ingestion from MES/ERP/LIMS/historians and cross-country plants | ⭐ 5 | � Excluded | 🟢 Low | Out of scope as a standalone service — **Microsoft Fabric Data Factory** (pipelines / Dataflows Gen2) orchestrates ingestion inside the unified platform. |
| 📊 Data & analytics | Azure Data Lake Storage / OneLake pattern | Central storage for telemetry, quality, maintenance, and emissions data | ⭐ 5 | 🚀 Now | 🟢 Low | Essential data foundation for prediction, optimization, and governance. |
| 📊 Data & analytics | Azure Stream Analytics | Real-time event processing for process control and anomaly pipelines | 🔹 3 | 🚫 Excluded | 🟡 Medium | Out of scope — **Fabric Real-Time Intelligence** (Eventstreams/KQL) is the hot path. |
| 📊 Data & analytics | Azure Data Explorer | High-scale time-series / telemetry exploration and operational analytics | 🔷 4 | 🚫 Excluded | 🟡 Medium | Out of scope as a standalone cluster — **Fabric Real-Time Intelligence** already embeds the ADX/Eventhouse engine. |
| 🗄️ Databases | Azure SQL Database | Transactional app data, operator workflows, operational metadata | 🔷 4 | 🚀 Now | 🟢 Low | Good for application state, rules, audit trails, and operational workflow persistence. |
| 🗄️ Databases | Azure Cosmos DB | Low-latency app/session/memory store for AI apps and agents | 🔷 4 | ⏭️ Next | 🟡 Medium | Useful if the solution uses conversational state, globally distributed app data, or agent memory; can be overkill if a relational store suffices. |
| 🗄️ Databases | Azure Database for PostgreSQL Flexible Server | Operational apps, structured engineering data, backend platforms | 🔷 4 | 🚀 Now | 🟢 Low | Strong general-purpose database option for platform services and engineering applications. |
| 🗄️ Databases | Azure Database for MySQL Flexible Server | Optional app backend database | ▫️ 2 | ⏳ Later | 🔴 High | Viable but redundant with SQL/PostgreSQL; adding it usually fragments the data estate without benefit. |
| 🗄️ Databases | Azure Cache for Redis / Azure Managed Redis | Low-latency caching, session handling, agent acceleration | 🔷 4 | ⏭️ Next | 🟡 Medium | Useful for performance optimization of AI apps and APIs, but only justify once latency is a real constraint. |
| ⚙️ Compute | Azure Kubernetes Service (AKS) | Core platform for industrial AI apps, APIs, digital services, custom inference | 🔹 3 | 🚫 Excluded | 🔴 High | Out of scope — **Azure Container Apps + Functions** cover the workloads with no cluster to operate; adopt only if scale/control genuinely force it. |
| ⚙️ Compute | Azure Container Apps | Lightweight hosting for agents, APIs, event-driven services | ⭐ 5 | 🚀 Now | 🟢 Low | Primary host for the energy-dispatch agent microservice and AI/API wrappers — delivers the solution's compute without full AKS complexity. |
| ⚙️ Compute | Azure Functions | Event-driven logic, alerts, scoring triggers, integration glue | ⭐ 5 | 🚀 Now | 🟢 Low | Very strong for rule execution, event processing, and low-overhead automation. |
| ⚙️ Compute | Azure App Service | UI / portal / simple business apps | 🔹 3 | ⏭️ Next | 🟢 Low | Useful for web portals, but less central than AKS/Functions for heavy industrial event-driven patterns. |
| ⚙️ Compute | Azure Virtual Machines | Legacy integration, industrial middleware, vendor software hosting | 🔹 3 | 🚫 Excluded | 🟡 Medium | Out of scope — the platform is greenfield cloud-native on managed PaaS (Container Apps / Functions); no VMs to patch and operate. |
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
| 📡 IoT & edge | Azure IoT Edge | Edge processing near equipment / local scoring / resilient processing | ⭐ 5 | 🚫 Excluded | 🟢 Low | Out of scope to limit footprint — ingestion is **cloud-direct via Azure IoT Hub**; revisit only if edge autonomy becomes a hard requirement. |
| 📡 IoT & edge | Azure Digital Twins | Semantic model of plants, assets, processes, dependencies | 🔹 3 | ⏭️ Next | 🔴 High | Useful for furnace/mill topology and what-if analysis, but the use case relies on physics-informed signatures, not a twin; high modeling/maintenance effort, so adopt only when a twin-driven scenario is committed. |
| 📡 IoT & edge | Azure Sphere | Securing specific IoT devices/microcontroller estates | ▫️ 2 | 🚫 Excluded | 🔴 High | Out of scope — ingestion uses **Azure IoT Hub** on existing OT hardware; no greenfield microcontroller estate to secure. |
| 🛠️ DevOps & engineering | GitHub Actions | CI/CD for apps, ML pipelines, infra, prompt assets | 🔷 4 | 🚀 Now | 🟢 Low | Strong modern DevOps option for platform delivery and repeatability. |
| 🛠️ DevOps & engineering | Azure DevOps | Alternative enterprise delivery stack | 🔹 3 | 🚫 Excluded | 🟡 Medium | Out of scope — **GitHub** (Actions, Repos, Issues) is the single delivery stack; ADO would be redundant. |
| 🛠️ DevOps & engineering | Azure Pipelines | CI/CD in Azure DevOps | 🔹 3 | 🚫 Excluded | 🟡 Medium | Out of scope — **GitHub Actions** is the chosen CI/CD engine; Azure Pipelines would be redundant. |
| 🛠️ DevOps & engineering | Azure Boards / Repos / Artifacts | Project, code, and artifact management | ▫️ 2 | ⏳ Later | 🟡 Medium | Useful engineering support tools, but redundant where GitHub already covers code and work tracking. |
| 🏢 Hybrid & sovereign | Azure Arc | Unified management across cloud, plant edge, on-prem, multi-site | ⭐ 5 | 🚫 Excluded | 🟡 Medium | Out of scope — this is a **cloud-first, Fabric-centric** scope with no edge/on-prem control plane to manage. |
| 🏢 Hybrid & sovereign | Azure Local | Local infrastructure option for plant-hosted workloads | 🔹 3 | ⏭️ Next | 🟡 Medium | Can matter where workloads must stay local, but adds hybrid operations overhead. |
| 🏢 Hybrid & sovereign | Azure Stack | Specialized hybrid deployment scenarios | ▫️ 2 | 🚫 Excluded | 🔴 High | Out of scope — cloud-first scope with no disconnected/sovereign on-prem deployment. |
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
| Azure Data Factory | Microsoft Fabric — Data Factory (pipelines / Dataflows Gen2) inside the unified platform |
| Azure Kubernetes Service (AKS) | Azure Container Apps + Azure Functions (no cluster to operate) |
| Azure Virtual Machines | Managed PaaS (Container Apps / Functions); greenfield cloud-native, no VMs |
| Azure Sphere | Azure IoT Hub on existing OT hardware; no microcontroller estate to secure |
| Azure DevOps | GitHub (Actions, Repos, Issues) as the single delivery stack |
| Azure Pipelines | GitHub Actions as the single CI/CD engine |
| Azure Stack | Not used — cloud-first scope; no disconnected/sovereign on-prem deployment |

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
- 🏢 Azure Local
- 📍 Foundry Local

### 🥉 Tier 3 — Optional / Contextual

- 🧩 Azure Digital Twins (only if a twin-driven scenario is committed)
- 🔎 Azure AI Search (optional — Foundry IQ already provides grounding/retrieval)
- 🌐 App Service
- 🗄️ Azure SQL
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

## 📡 Focus — Azure IoT Services

UC12 is fundamentally an **IoT-driven** use case: furnace, mill and utility
telemetry is the raw material for every workload. The **must-have** core keeps
ingestion deliberately simple — **cloud-direct via Azure IoT Hub** — so the team
proves the AI value first without standing up edge infrastructure. This section
evaluates the broader Azure IoT family and sorts each service into a **must-have**,
**nice-to-have** or **not-retained** tier.

| Azure IoT service | Verdict | Tier |
| --- | :---: | --- |
| 📡 Azure IoT Hub | ✅ OK | 🟢 Must-have |
| 🧩 Azure Digital Twins | ✅ OK | 🟡 Nice-to-have |
| ⚙️ Azure IoT Operations | ✅ OK | 🟡 Nice-to-have |
| 📊 Azure IoT Central | 🚫 KO | ⚪ Not retained |
| 🔌 Azure IoT Edge | 🚫 KO | ⚪ Not retained |

### 🧭 How the project can be implemented — IoT tiers

The IoT scope can be delivered in **layers of commitment**, so the project starts
lean and earns each addition:

- 🟢 **Must-have (the foundation):** **Azure IoT Hub** — without it there is
  no telemetry and therefore no use case. It is the single, non-negotiable IoT
  service the pilot ships with (cloud-direct, no edge runtime).
- 🟡 **Nice-to-have (value-driven add-ons):** **Azure Digital Twins**
  and **Azure IoT Operations** — each unlocks real upside (a navigable furnace
  twin; resilient edge pre-processing at scale) but only becomes worthwhile once
  the cloud-direct pipeline is proven and a concrete scenario justifies the extra
  cost and operations. They are adopted **only if** a committed need appears.
- ⚪ **Not retained (out of scope):** **Azure IoT Central** (packaged SaaS with no
  clear roadmap) and **Azure IoT Edge** (legacy runtime superseded by IoT
  Operations) — neither fits UC12's open, custom, Fabric-and-Foundry architecture,
  and their useful capabilities are already covered by the must-have/nice-to-have
  services above.

> **Net:** the project is **fully implementable with the single must-have
> (IoT Hub)**; the nice-to-have services are **optional accelerators** to add
> later, and the not-retained services add nothing UC12 cannot already do.

### 📡 Azure IoT Hub — ✅ OK (must-have)

**What it is:** a managed cloud gateway for secure, bidirectional device-to-cloud
telemetry and cloud-to-device messaging, with per-device identity, authentication
and at-scale device management.

**Why it is relevant here:** it is the **front door** for furnace, mill and energy
telemetry into Azure — per-device security, EU-resident endpoints behind Private
Link, and native fan-out into **Fabric Real-Time Intelligence** and **Event Hubs**.

**Tier:** **must-have** — the single non-negotiable IoT service; the cloud-direct
ingestion path needs no edge runtime to start delivering AI value.

### 🧩 Azure Digital Twins — ✅ OK (nice-to-have)

**What it is:** a platform to build **live, queryable digital models** of physical
environments (assets, their properties, and relationships) updated from telemetry.

**Why it is relevant here:** modelling each **furnace / line** as a twin — with
campaign state, refractory context and live thermal data — enables richer
what-if analysis and a navigable plant topology on top of the RUL signals.

**Tier:** **nice-to-have** — the must-have core relies on **physics-informed
signatures** and the **Fabric RTI Digital Twin builder**, so a standalone Azure
Digital Twins instance is only justified once a committed twin-driven scenario
(e.g. cross-asset what-if) is on the roadmap.

### ⚙️ Azure IoT Operations — ✅ OK (nice-to-have)

**What it is:** the **next-generation, Arc-enabled edge data plane** — an MQTT
broker plus declarative data flows that normalize, filter and route OT telemetry
at the plant before it reaches the cloud.

**Why it is relevant here:** at four sites with high-frequency furnace sensors,
an edge layer can **pre-aggregate and buffer** telemetry (resilience to
connectivity loss), enforce the **one-way OT/IT boundary**, and cut egress. It is
also the **modern replacement** for the legacy IoT Edge runtime.

**Tier:** **nice-to-have** — deferred until the cloud-direct pipeline is proven
and a concrete need for edge autonomy/bandwidth control appears during multi-site
scale-out.

### 📊 Azure IoT Central — 🚫 KO (no evolution)

**What it is:** a fully managed **IoT SaaS application platform** (prebuilt
dashboards, rules and device templates) for building IoT solutions with minimal
custom development.

**Why it is *not* relevant here:** the decisive reason is lifecycle — Azure IoT
Central has **no clear forward roadmap and carries a real deprecation risk**, and
it is no longer attracting meaningful feature investment, so building UC12 on it
would risk a **dead-end dependency** the moment we shipped. Even setting the
roadmap risk aside, it is the **wrong architectural shape**: IoT Central is a
closed, low-code SaaS app optimised for quick device dashboards and simple rules,
whereas UC12 needs **open, custom data + ML + governance** — physics-informed RUL
models, OneLake medallion data, Purview lineage and EU AI Act traceability — none
of which fit a packaged SaaS surface. Its genuinely useful pieces (device
onboarding, rules, dashboards) are already covered, more flexibly, by **Azure IoT
Hub + Microsoft Fabric (Real-Time Intelligence + Power BI)**. The migration path
Microsoft itself points to off IoT Central is exactly **IoT Hub + a custom
solution**, which is the architecture UC12 already adopts.

**Tier:** **not retained** — its capability is covered by **Azure IoT
Hub + Microsoft Fabric** (a custom solution we fully control).

### 🔌 Azure IoT Edge — 🚫 KO (superseded)

**What it is:** the **first-generation edge runtime** that runs containerized
modules (including offline ML inference) on plant-side gateways managed from IoT
Hub.

**Why it is *not* relevant here:** there are two reasons. First, the must-have
core is **cloud-direct**, so there is no edge runtime to operate. Second — and
decisive for the longer term — **IoT Edge is effectively superseded by Azure IoT
Operations**, the Arc-based, declarative successor. If/when an edge layer is
needed, we would adopt **IoT Operations**, not IoT Edge.

**Tier:** **not retained** — any future edge requirement is met by
**Azure IoT Operations** instead.