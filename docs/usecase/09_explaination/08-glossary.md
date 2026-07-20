# 08 — Glossary (English → French)

A reference of the **industry (steel)**, **cloud/Fabric**, and **AI** vocabulary used in this
project, with French equivalents and a short definition. Use it while reading the other files.

> 🇫🇷 **FR :** Un référentiel du vocabulaire **métier (acier)**, **cloud/Fabric** et **IA**
> utilisé dans ce projet, avec les équivalents français et une courte définition. À utiliser en
> lisant les autres fichiers.

---

## 8.1 Steel & industry / Acier et industrie

| English | 🇫🇷 Français | Definition / Définition |
|---------|-------------|--------------------------|
| Blast furnace | Haut-fourneau | Large furnace that smelts iron ore into molten iron/steel. |
| Rolling mill | Laminoir | Machinery that shapes metal by passing it through rollers. |
| Furnace lining (refractory) | Revêtement réfractaire | Heat-resistant inner wall of the furnace that wears out over time. |
| Heat (a heat) | Coulée | One batch/melt of steel produced by a furnace. |
| Tapping temperature | Température de coulée | The temperature when molten steel is tapped/poured. |
| High-grade yield | Rendement haut de gamme | Share of output meeting premium (e.g. automotive) grade. |
| DP800 | DP800 | A dual-phase high-strength automotive steel grade. |
| Sulphur / inclusion | Soufre / inclusion | Impurities that affect steel quality. |
| Off-gas | Gaz de procédé / effluents gazeux | Gases emitted by the furnace, monitored for process/quality. |
| Vibration signature | Signature vibratoire | Vibration pattern used to detect equipment wear. |
| Heat flux | Flux thermique | Rate of heat transfer; a wear indicator for the lining. |
| OT (Operational Technology) | Technologie opérationnelle | Plant-floor control systems (sensors, PLC, SCADA). |
| SCADA | SCADA (supervision) | Supervisory Control And Data Acquisition system. |
| PLC | Automate programmable (API) | Programmable Logic Controller driving a machine. |
| Historian | Historian (base d'historisation) | Time-series database of plant process data. |
| Purdue model | Modèle de Purdue | Reference model layering OT/IT security zones. |

> 🇫🇷 **FR :** Le tableau ci-dessus donne, pour chaque terme métier anglais, l'équivalent
> français et une définition brève.

---

## 8.2 Objectives & KPIs / Objectifs et indicateurs

| English | 🇫🇷 Français | Definition / Définition |
|---------|-------------|--------------------------|
| Energy intensity | Intensité énergétique | Energy used per ton of steel (kWh/t, €/t). |
| Emissions (tCO₂/t) | Émissions (tCO₂/t) | Tonnes of CO₂ per ton of steel. |
| Lead time | Délai d'anticipation | How far ahead an alert warns before an event. |
| RUL (Remaining Useful Life) | DVR (Durée de Vie Résiduelle) | Estimated time before a component must be replaced. |
| SPC (Statistical Process Control) | MSP (Maîtrise Statistique des Procédés) | Using control charts to detect process drift. |
| Cp / Cpk | Cp / Cpk | Process capability indices (staying within spec). |
| KPI | ICP (indicateur clé de performance) | Key Performance Indicator. |
| Baseline | Référence / base de comparaison | The "do nothing" case used to measure improvement. |

> 🇫🇷 **FR :** Objectifs et indicateurs traduits ci-dessus.

---

## 8.3 Cloud, Azure & Fabric / Cloud, Azure et Fabric

| English | 🇫🇷 Français | Definition / Définition |
|---------|-------------|--------------------------|
| SaaS | SaaS (logiciel en tant que service) | Software run for you over the web; no servers to manage. |
| Resource group | Groupe de ressources | An Azure folder grouping related resources. |
| Region | Région | Physical datacenter location. |
| Capacity (F-SKU) | Capacité (F-SKU) | Paid compute powering Fabric (F2, F4, F8…). |
| Workspace | Espace de travail | Collaborative container for Fabric items. |
| Item | Élément | Any object in a workspace (lakehouse, notebook…). |
| OneLake | OneLake | Fabric's single, tenant-wide data lake ("OneDrive for data"). |
| Lakehouse | Lakehouse | Store combining files + Delta tables, queried by Spark/T-SQL. |
| Eventhouse / KQL DB | Eventhouse / base KQL | Real-time time-series store queried with KQL. |
| Eventstream | Eventstream | No-code pipe routing streaming events to destinations. |
| Activator | Activator | No-code rules that trigger alerts/actions on streams. |
| Notebook | Notebook | Interactive code+text document (here PySpark) run on Spark. |
| Data Pipeline / Data Factory | Pipeline de données / Data Factory | No-code orchestration of data movement. |
| Dataflow Gen2 | Dataflow Gen2 | Low-code data cleansing/transformation. |
| Medallion (Bronze/Silver/Gold) | Médaillon (Bronze/Argent/Or) | Raw → clean → ready refinement layers. |
| Shortcut | Raccourci (shortcut) | Zero-copy pointer to data in place. |
| Mirroring | Réplication (mirroring) | Managed near-real-time replication into OneLake. |
| Delta / Parquet | Delta / Parquet | Open table/file formats for analytics. |
| Direct Lake | Direct Lake | Power BI mode reading Gold directly, fast and fresh. |
| SQL analytics endpoint | Point de terminaison SQL analytique | Read-only T-SQL access over a lakehouse. |
| Semantic model | Modèle sémantique | Governed tables + measures behind reports. |
| Power BI | Power BI | Fabric's dashboard/reporting tool. |
| Spark / PySpark | Spark / PySpark | Distributed big-data engine / its Python API. |
| KQL | KQL | Kusto Query Language for time-series data. |
| T-SQL | T-SQL | SQL dialect for relational queries. |
| Purview | Purview | Data governance: lineage, catalog, classification. |
| Entra ID | Entra ID | Microsoft's identity service (formerly Azure AD). |
| Managed Identity | Identité managée | Password-less service identity. |
| Key Vault | Key Vault (coffre-fort) | Secure secret/key store. |
| Azure Policy | Azure Policy | Policy-as-code guardrails (e.g. allowed regions). |
| Bicep | Bicep | Language to describe Azure resources (IaC). |
| IaC | Infra en tant que code | Infrastructure as Code. |
| CI/CD | CI/CD (intégration/livraison continue) | Automated build & deploy pipelines. |
| Container / Container App | Conteneur / Container App | Packaged app / managed container runtime. |
| Serverless (Functions) | Serverless (Functions) | Run code on demand, pay per execution. |
| IoT Hub | IoT Hub | Cloud gateway for device telemetry. |
| Event Hubs | Event Hubs | High-throughput event streaming service. |
| Consumer group | Groupe de consommateurs | Independent read cursor on a stream. |
| SAS | SAS (signature d'accès partagé) | Scoped access token. |
| Endpoint | Point de terminaison | A network address/service you connect to. |
| tenant | tenant (locataire) | An organization's isolated instance in Microsoft cloud. |
| ctid | ctid | The tenant id passed in a URL to open the right tenant. |

> 🇫🇷 **FR :** Vocabulaire cloud/Azure/Fabric traduit ci-dessus ; ce sont les termes qui
> reviennent le plus dans les fichiers 03, 04 et 05.

---

## 8.4 AI & data science / IA et science des données

| English | 🇫🇷 Français | Definition / Définition |
|---------|-------------|--------------------------|
| Machine Learning (ML) | Apprentissage automatique | Models that learn patterns from data. |
| Feature | Variable / caractéristique (feature) | An input signal computed for a model. |
| Regression | Régression | Predicts a number (e.g. days to failure). |
| Classifier | Classifieur | Predicts a category (e.g. fail/not-fail). |
| Physics-informed model | Modèle guidé par la physique | Model grounded in known physical laws. |
| MLflow | MLflow | Tool to track experiments and register models. |
| Experiment | Expérience | Tracked series of training runs. |
| Model registry | Registre de modèles | Versioned store of trained models. |
| Batch scoring | Scoring par lots | Running a model over many rows at once. |
| Model drift | Dérive de modèle | Accuracy degrading over time as data changes. |
| GenAI | IA générative | Models that generate text/content. |
| LLM | LLM (grand modèle de langage) | Large Language Model (e.g. GPT). |
| RAG | RAG (génération augmentée par récupération) | Answering from retrieved documents. |
| Grounding | Ancrage | Anchoring answers to real sources. |
| Citation | Citation | The source reference an answer points to. |
| Content Safety | Content Safety | Service filtering harmful generative output. |
| Embedding | Embedding (plongement) | Numeric vector representing text meaning for search. |
| Foundry / Foundry IQ | Foundry / Foundry IQ | Microsoft's GenAI platform / its grounding-RAG layer. |
| MILP | MILP (programmation linéaire en nombres entiers) | Exact optimization method. |
| Heuristic | Heuristique | Fast "good enough" optimization method. |
| Solver | Solveur | Engine that computes an optimization solution. |
| Provenance / origin | Provenance / origine | Where a data point came from (real vs synthetic). |
| Golden fixture | Fixture « golden » | Frozen reference output guarding against regressions. |
| Audit record | Enregistrement d'audit | Immutable log of a prediction/decision. |

> 🇫🇷 **FR :** Vocabulaire IA/data science traduit ci-dessus ; indispensable pour les fichiers
> 05 et 06.

---

## 8.5 Acronyms quick list / Liste rapide des acronymes

`POC` proof of concept · `OT/IT` operational/information technology · `MES` manufacturing
execution system · `ERP` enterprise resource planning · `EAM` enterprise asset management ·
`RUL` remaining useful life · `SPC` statistical process control · `KQL` Kusto query language ·
`RTI` real-time intelligence · `RBAC` role-based access control · `GDPR` general data
protection regulation · `EU AI Act` EU artificial-intelligence regulation · `EU-ETS` EU
emissions trading system · `SKU` stock-keeping unit (here a capacity size) · `SAS` shared
access signature · `RAG` retrieval-augmented generation · `LLM` large language model · `MILP`
mixed-integer linear programming · `APM` application performance monitoring · `IaC`
infrastructure as code.

> 🇫🇷 **FR :** Liste condensée des acronymes du projet — à relire juste avant la soutenance.

**Next:** [09 — Links & oral-defense prep »](09-links-and-oral-defense.md)

> 🇫🇷 **FR : Suite :** [09 — Liens et préparation à la soutenance »](09-links-and-oral-defense.md)
