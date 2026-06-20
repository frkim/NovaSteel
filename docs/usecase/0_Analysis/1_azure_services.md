# 🏭 UC12 – AI-Powered Steel Production Optimisation Platform

A practical scoring matrix for the AI-Powered Steel Production Optimisation Platform.

## 🎯 Scoring Method

Score **5** = critical, **4** = highly relevant, **3** = useful/selective, **2** = niche/optional, **1** = low relevance.

The score is an architecture recommendation for this use case, while the factual positioning of services (for example Microsoft Foundry being the unified AI platform, AI Services being exposed in Foundry, manufacturing focus on intelligent factories, and Foundry/Fabric/IoT alignment) is grounded in Microsoft sources and enterprise materials.

## 🧭 UC12 Azure Service Relevance Matrix

| Category | Azure / Microsoft Service | Main Role in UC12 | Relevance Score | Priority | Why it matters for steel production optimization |
| --- | --- | --- | :---: | :---: | --- |
| 🤖 AI platform | Microsoft Foundry | Core AI platform for agents, models, orchestration, grounding, observability | 5 | Now | Best fit for the AI control layer: production AI agents, model management, enterprise governance, evaluation, and grounded AI apps. |
| 🤖 AI platform | Foundry Agent Service | Energy optimization agent, knowledge agents, maintenance copilots | 5 | Now | Directly relevant for action-oriented agents that automate or assist production, maintenance, and operations workflows. |
| 🤖 AI platform | Foundry IQ | Grounding on procedures, maintenance docs, operator knowledge, reports | 5 | Now | Highly relevant for searchable operational knowledge, retrieval, and grounded responses for technicians/operators. |
| 🤖 AI platform | Foundry Tools / AI Services in Foundry | Speech, language, document, content tools for knowledge capture and industrial workflows | 5 | Now | Strong fit for operator interview capture, multilingual knowledge extraction, document understanding, and AI enrichment. |
| 🤖 AI platform | Foundry Local | Offline / plant-edge AI inference when connectivity or sovereignty constraints apply | 4 | Next | Relevant where industrial sites require local inference, resilience, or limited connectivity. |
| 🧠 Models | Azure OpenAI / Foundry Models | LLMs for copilots, knowledge capture, reasoning, summarization, recommendations | 5 | Now | Core for GenAI use cases and agent reasoning on operational and knowledge workflows. |
| 🧠 Models | Third-party / OSS models in Foundry | Specialized models for optimized cost/performance or multilingual/edge scenarios | 4 | Next | Useful when you want model choice optimization, cost control, or specialized domain behavior. |
| 🗣️ AI API layer | Azure AI Services (suite) | Unified API layer for speech, language, vision, document, safety | 5 | Now | Direct enabler for knowledge capture, OCR, multilingual operations, safety and extraction scenarios. |
| 🗣️ AI API layer | Speech | Capture and transcribe operator interviews, voice procedures, multilingual support | 5 | Now | Excellent fit for preserving retiring operator know-how and turning voice into searchable content. |
| 🗣️ AI API layer | Language | Summarization, entity extraction, procedural structuring, multilingual normalization | 5 | Now | Very relevant for transforming tacit knowledge into structured operational guidance. |
| 🗣️ AI API layer | Document Intelligence / Content Understanding | Parsing SOPs, maintenance reports, inspection forms, PDFs, logs | 5 | Now | Strong fit for extracting structured data from industrial and compliance documents. |
| 🗣️ AI API layer | Vision / OCR | Reading gauges, images, labels, scanned forms, visual process evidence | 4 | Next | Useful for inspection and image-based process support if the program expands into visual QA. |
| 🗣️ AI API layer | Content Safety | Governance and safety filtering for GenAI interactions | 4 | Now | Important for enterprise-safe deployment of generative assistants and knowledge systems. |
| 📊 Data & analytics | Microsoft Fabric | Unified analytics foundation / OneLake / BI / data products | 5 | Now | Strong candidate for the enterprise analytics backbone and for grounding AI on trusted industrial data. |
| 📊 Data & analytics | Azure Databricks | Advanced data engineering / feature engineering / ML / time-series analytics | 5 | Now | Highly relevant for industrial telemetry processing, model engineering, and large-scale historical analysis. |
| 📊 Data & analytics | Azure Data Factory | Batch ingestion from MES/ERP/LIMS/historians and cross-country plants | 5 | Now | Very useful for orchestrating plant and enterprise data ingestion pipelines. |
| 📊 Data & analytics | Azure Data Lake Storage / OneLake pattern | Central storage for telemetry, quality, maintenance, and emissions data | 5 | Now | Essential data foundation for prediction, optimization, and governance. |
| 📊 Data & analytics | Azure Stream Analytics | Real-time event processing for process control and anomaly pipelines | 5 | Now | Strong fit for near-real-time optimization and anomaly detection from plant telemetry. |
| 📊 Data & analytics | Azure Data Explorer | High-scale time-series / telemetry exploration and operational analytics | 5 | Now | Very relevant for sensor-heavy industrial workloads and fast analysis of process signals. |
| 🗄️ Databases | Azure SQL Database | Transactional app data, operator workflows, operational metadata | 4 | Now | Good for application state, rules, audit trails, and operational workflow persistence. |
| 🗄️ Databases | Azure Cosmos DB | Low-latency app/session/memory store for AI apps and agents | 4 | Next | Useful if the solution uses conversational state, globally distributed app data, or agent memory. |
| 🗄️ Databases | Azure Database for PostgreSQL Flexible Server | Operational apps, structured engineering data, backend platforms | 4 | Now | Strong general-purpose database option for platform services and engineering applications. |
| 🗄️ Databases | Azure Database for MySQL Flexible Server | Optional app backend database | 2 | Later | Viable but usually less central than SQL/PostgreSQL for this industrial architecture. |
| 🗄️ Databases | Azure Cache for Redis / Azure Managed Redis | Low-latency caching, session handling, agent acceleration | 4 | Next | Useful for performance optimization of AI apps, APIs, and interactive experiences. |
| ⚙️ Compute | Azure Kubernetes Service (AKS) | Core platform for industrial AI apps, APIs, digital services, custom inference | 5 | Now | Best fit if you need scalable, production-grade, multi-service industrial platforms. |
| ⚙️ Compute | Azure Container Apps | Lightweight hosting for agents, APIs, event-driven services | 4 | Now | Good for fast delivery of microservices and AI wrappers without full AKS complexity. |
| ⚙️ Compute | Azure Functions | Event-driven logic, alerts, scoring triggers, integration glue | 5 | Now | Very strong for rule execution, event processing, and low-overhead automation. |
| ⚙️ Compute | Azure App Service | UI / portal / simple business apps | 3 | Next | Useful for web portals, but less central than AKS/Functions for heavy industrial event-driven patterns. |
| ⚙️ Compute | Azure Virtual Machines | Legacy integration, industrial middleware, vendor software hosting | 4 | Now | Often necessary for OT-adjacent or legacy manufacturing components. |
| ⚙️ Compute | Azure Batch | Large simulations / optimization runs / heavy compute jobs | 3 | Next | Can be helpful for batch simulation and optimization, but not always first choice. |
| 🌐 Networking | Azure Virtual Network (VNet) | Network isolation for data, AI, and industrial services | 5 | Now | Mandatory for secure industrial landing zones and private service integration. |
| 🌐 Networking | Azure Private Link | Private access to PaaS services from plants and central platform | 5 | Now | Very important for protecting telemetry, AI endpoints, and regulated workloads. |
| 🌐 Networking | Azure ExpressRoute | Private connectivity from plants/data centers to Azure | 5 | Now | Highly relevant where steel plants need reliable private connectivity between OT/IT and cloud. |
| 🌐 Networking | Azure Firewall | Central egress/ingress control and segmentation | 4 | Now | Strong baseline security service for regulated multi-country industrial environments. |
| 🌐 Networking | Azure Front Door | Global entry point for external apps/portals/APIs | 3 | Next | Useful if you expose central portals or API layers globally, but not the core of plant ingestion. |
| 🌐 Networking | Azure Application Gateway | Internal web/API ingress and WAF | 4 | Now | Good for protected enterprise applications and regional ingress patterns. |
| 🌐 Networking | Azure Load Balancer | Internal service balancing | 3 | Next | Useful infrastructure element, but not a differentiator for the use case itself. |
| 🔐 Security & governance | Microsoft Entra ID | Identity for users, admins, apps, and potentially agent governance | 5 | Now | Core enterprise identity and access control layer for cross-country deployment. |
| 🔐 Security & governance | Azure Key Vault | Secrets, keys, certificates for AI/data/integration services | 5 | Now | Essential for secure industrial platform operations. |
| 🔐 Security & governance | Microsoft Defender for Cloud | Security posture and cloud workload protection | 5 | Now | Strongly recommended for enterprise and regulated industrial platforms. |
| 🔐 Security & governance | Microsoft Sentinel | SOC/SIEM and threat monitoring | 4 | Next | Very valuable if the platform is business-critical and integrated with wider SOC operations. |
| 🔐 Security & governance | Azure Policy | Governance, guardrails, region controls, service restrictions | 5 | Now | Especially relevant for GDPR, AI governance, and multi-country policy enforcement. |
| 🔐 Security & governance | Microsoft Purview | Data governance, lineage, classification, compliance | 5 | Now | Critical for regulated industrial data and AI governance across countries and functions. |
| 💾 Storage | Azure Blob Storage | Raw files, reports, archives, model input/output | 5 | Now | Foundational storage for unstructured industrial and AI data. |
| 💾 Storage | Azure Files | Shared file storage for lift-and-shift or plant apps | 3 | Next | Useful for compatibility scenarios, not the strategic analytics core. |
| 💾 Storage | Azure Disk Storage | Persistent disks for VMs/AKS stateful workloads | 3 | Now | Infrastructure necessity, but not business-differentiating. |
| 💾 Storage | Azure Archive Storage | Long-term industrial record retention / compliance retention | 4 | Next | Relevant for audit, emissions evidence, and long retention periods. |
| 💾 Storage | Azure Data Lake Storage Gen2 | Large-scale analytical storage for telemetry/history/quality data | 5 | Now | One of the most important services for this use case's data estate. |
| 🔄 Integration & events | Azure Event Hubs | High-throughput telemetry ingestion from plants and sensors | 5 | Now | Very strong fit for streaming plant data at scale. |
| 🔄 Integration & events | Azure Service Bus | Reliable business/event messaging between apps and workflows | 4 | Now | Useful for decoupling operational services and maintenance/quality workflows. |
| 🔄 Integration & events | Azure Event Grid | Event-driven orchestration between services | 4 | Now | Good for lightweight event fan-out and automation patterns. |
| 🔄 Integration & events | Azure Logic Apps | Workflow automation, enterprise connectors, operational actions | 5 | Now | Very relevant for integrating AI decisions with business systems and approvals. |
| 🔄 Integration & events | Azure API Management | Secure API facade, governance, throttling, AI API exposure | 5 | Now | Important when exposing optimization APIs, plant services, and AI tools securely at scale. |
| 📡 IoT & edge | Azure IoT Hub | Device onboarding and telemetry ingestion from plant equipment | 5 | Now | Core service for getting furnace, mill, and utility telemetry into Azure. |
| 📡 IoT & edge | Azure IoT Edge | Edge processing near equipment / local scoring / resilient processing | 5 | Now | Very relevant where latency, autonomy, or intermittent connectivity matter on the shop floor. |
| 📡 IoT & edge | Azure Digital Twins | Semantic model of plants, assets, processes, dependencies | 5 | Now | Excellent fit for furnace/mill topology, process context, and what-if optimization. |
| 📡 IoT & edge | Azure Sphere | Securing specific IoT devices/microcontroller estates | 2 | Later | Potentially helpful for certain device classes, but not usually central to large steel OT architecture. |
| 🛠️ DevOps & engineering | GitHub Actions | CI/CD for apps, ML pipelines, infra, prompt assets | 4 | Now | Strong modern DevOps option for platform delivery and repeatability. |
| 🛠️ DevOps & engineering | Azure DevOps | Alternative enterprise delivery stack | 3 | Next | Relevant if the client already standardizes on ADO. |
| 🛠️ DevOps & engineering | Azure Pipelines | CI/CD in Azure DevOps | 3 | Next | Useful in ADO-centric enterprises. |
| 🛠️ DevOps & engineering | Azure Boards / Repos / Artifacts | Project, code, and artifact management | 2 | Later | Useful engineering support tools, but not architecture-critical. |
| 🏢 Hybrid & sovereign | Azure Arc | Unified management across cloud, plant edge, on-prem, multi-site | 5 | Now | Very relevant for distributed steel plants and hybrid OT/IT estates across several countries. |
| 🏢 Hybrid & sovereign | Azure Local | Local infrastructure option for plant-hosted workloads | 3 | Next | Can matter where some workloads must stay local, but not always the primary platform choice. |
| 🏢 Hybrid & sovereign | Azure Stack | Specialized hybrid deployment scenarios | 2 | Later | Lower priority unless there is a very specific disconnected or sovereign requirement. |
| 🏢 Hybrid & sovereign | Foundry Local | On-device / local AI execution | 4 | Next | Good complement for edge AI scenarios needing local AI execution. |
| 💬 Communications | Azure Communication Services | Notifications, alerts, operator comms, workflow messaging | 3 | Next | Useful for alerting and workflow interaction, but not core to optimization itself. |
| 🎮 Gaming/media | Azure PlayFab | Gaming backend | 1 | Later | Not relevant for this industrial use case. |

## ⭐ Shortlist: The Most Important Services for UC12

If you want the top architecture core, prioritize these first:

### 🥇 Tier 1 — Absolutely Central

- 🤖 Microsoft Foundry
- 🤖 Foundry Agent Service
- 📚 Foundry IQ
- 🧠 Azure OpenAI / Foundry Models
- 🗣️ Azure AI Services (especially Speech, Language, Document Intelligence / Content Understanding)
- 📊 Microsoft Fabric
- 💾 Azure Data Lake Storage Gen2
- 🔬 Azure Databricks
- ⚡ Azure Stream Analytics
- 📈 Azure Data Explorer
- 📡 Azure IoT Hub
- 🏭 Azure IoT Edge
- 🧩 Azure Digital Twins
- ⚙️ Azure Functions
- 🚪 Azure API Management
- 🌐 Azure Private Link / VNet / ExpressRoute
- 🪪 Microsoft Entra ID
- 🔑 Azure Key Vault
- 📜 Azure Policy
- 🛡️ Microsoft Purview
- 🏢 Azure Arc

### 🥈 Tier 2 — Strong Supporting Services

- ☸️ AKS
- 📦 Container Apps
- 🔄 Logic Apps
- 🛡️ Defender for Cloud
- 👁️ Sentinel
- 💾 Blob Storage
- 🗄️ Cosmos DB / Redis (depending on app design)
- 📍 Foundry Local

### 🥉 Tier 3 — Optional / Contextual

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
| ⚡ Reduce energy consumption | IoT Hub + Event Hubs + Stream Analytics + Data Explorer + Databricks/Fabric + Foundry Agent Service |
| 🔥 Predict furnace lining degradation | IoT Edge + IoT Hub + Data Lake + Databricks/Azure ML pattern + Digital Twins + Functions |
| ✅ Improve steel quality consistency | Data Lake + Databricks + Fabric + Data Explorer + Foundry models/agents |
| 🧑‍🏭 Preserve retiring operator knowledge | Speech + Language + Document Intelligence/Content Understanding + Foundry IQ + Foundry Agent Service |
| 🔐 Meet governance and EU regulatory needs | Entra ID + Key Vault + Private Link + Azure Policy + Purview + Defender for Cloud |
| 🌍 Operate across 4 countries / hybrid plants | Azure Arc + ExpressRoute + VNet + Private Link + Foundry + Fabric |

## ✅ Overall Recommendation

For UC12, the most coherent Microsoft stack is:

- **📡 Edge + plant connectivity:** Azure IoT Hub, IoT Edge, Arc, ExpressRoute
- **📊 Industrial data platform:** ADLS Gen2 + Fabric + Databricks + Data Explorer + Stream Analytics
- **🤖 AI layer:** Microsoft Foundry + Foundry Agent Service + Foundry IQ + Azure OpenAI / Foundry Models
- **📚 Knowledge preservation:** Speech + Language + Document Intelligence / Content Understanding
- **🧩 Industrial semantics / process context:** Azure Digital Twins
- **🔐 Governance & compliance:** Entra ID, Key Vault, Private Link, Purview, Azure Policy, Defender for Cloud

That combination is the strongest fit for:

- ⚡ Energy optimization
- 🔧 Predictive maintenance
- ✅ Quality/yield improvement
- 🧑‍🏭 Operator knowledge retention
- 🌍 Cross-country governance