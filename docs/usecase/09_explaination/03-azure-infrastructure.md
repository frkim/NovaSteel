# 03 — Azure Infrastructure (What Is Actually Deployed)

Before Fabric can do anything, a set of **Azure resources** must exist. This page lists the
**real resources deployed** in the POC and explains each in plain language. They live in one
resource group: **`rg-novasteel-dev`**, region **Sweden Central** (IoT Hub in West Europe).

> 🇫🇷 **FR :** Avant que Fabric puisse fonctionner, un ensemble de **ressources Azure** doit
> exister. Cette page liste les **ressources réellement déployées** dans le POC et explique
> chacune en langage simple. Elles se trouvent dans un seul groupe de ressources :
> **`rg-novasteel-dev`**, région **Suède Centre** (IoT Hub en Europe de l'Ouest).

> **Vocabulary — Resource group:** a folder in Azure that groups related resources so they
> share a lifecycle (deploy/delete together). **Region:** the physical datacenter location.
>
> 🇫🇷 **FR — Groupe de ressources :** un dossier dans Azure qui regroupe des ressources liées
> pour partager un cycle de vie (déploiement/suppression ensemble). **Région :** l'emplacement
> physique du datacenter.

---

## 3.1 How it's deployed: Infrastructure as Code / Comment c'est déployé : l'infra en code

Everything is defined in **Bicep** files under `infrastructure/` and deployed via **GitHub
Actions** (CI/CD). "Infrastructure as Code" means the cloud is described in text files you can
review, version, and re-run — no manual clicking. This makes deployments **repeatable and
auditable**.

> 🇫🇷 **FR :** Tout est défini dans des fichiers **Bicep** sous `infrastructure/` et déployé
> via **GitHub Actions** (CI/CD). « Infrastructure as Code » signifie que le cloud est décrit
> dans des fichiers texte que l'on peut relire, versionner et rejouer — sans clics manuels.
> Cela rend les déploiements **reproductibles et auditables**.

> **Vocabulary — Bicep:** Microsoft's language for describing Azure resources declaratively.
> **CI/CD:** Continuous Integration / Continuous Delivery — automated build & deploy pipelines.
>
> 🇫🇷 **FR — Bicep :** le langage de Microsoft pour décrire les ressources Azure de manière
> déclarative. **CI/CD :** intégration/livraison continue — chaînes automatisées de
> construction et de déploiement.

---

## 3.2 The deployed resources / Les ressources déployées

Grouped by purpose. Names ending in a random token (e.g. `ox26fi`) are globally unique.

> 🇫🇷 **FR :** Regroupées par fonction. Les noms se terminant par un jeton aléatoire (ex.
> `ox26fi`) sont uniques au niveau mondial.

### A. Data platform / Plateforme de données

| Resource (live name) | Type | Role |
|----------------------|------|------|
| `fabnovasteedevox26fi` | **Microsoft Fabric capacity** | The compute/billing engine that powers the whole Fabric workspace |
| `dlnovasteedevox26fi…` | **ADLS Gen2 storage** | Data lake storage (medallion files, general blob) |
| `evhns-novastee-dev-ox26fi` | **Event Hubs namespace** | High-throughput streaming buffer feeding Real-Time Intelligence |

> 🇫🇷 **FR :**
> | Ressource | Type | Rôle |
> |-----------|------|------|
> | `fabnovasteedevox26fi` | **Capacité Microsoft Fabric** | Le moteur de calcul/facturation qui alimente tout l'espace de travail Fabric |
> | `dlnovasteedevox26fi…` | **Stockage ADLS Gen2** | Stockage du lac de données (fichiers médaillon, blob) |
> | `evhns-novastee-dev-ox26fi` | **Espace de noms Event Hubs** | Tampon de flux à haut débit alimentant la Real-Time Intelligence |

> **What is a Fabric "capacity"?** It is the **paid compute** behind Fabric, sized as an
> **F-SKU** (F2, F4, F8 …). Bigger F = more power = more cost. It can be **paused** to stop
> billing. In this POC it is auto-paused nightly at 02:00 to save money. See
> [04-fabric-fundamentals.md](04-fabric-fundamentals.md).
>
> 🇫🇷 **FR — Qu'est-ce qu'une « capacité » Fabric ?** C'est la **puissance de calcul payante**
> derrière Fabric, dimensionnée en **F-SKU** (F2, F4, F8…). Plus le F est grand, plus c'est
> puissant et coûteux. Elle peut être **mise en pause** pour arrêter la facturation. Dans ce
> POC, elle est mise en pause automatiquement chaque nuit à 02:00 pour économiser.

### B. Ingestion (getting data in) / Ingestion (faire entrer les données)

| Resource | Type | Role |
|----------|------|------|
| `iot-novastee-dev-ox26fi` | **Azure IoT Hub** | Cloud front door for devices; the simulator publishes furnace telemetry here (device→cloud only) |

> 🇫🇷 **FR :**
> | Ressource | Type | Rôle |
> |-----------|------|------|
> | `iot-novastee-dev-ox26fi` | **Azure IoT Hub** | Porte d'entrée cloud des appareils ; le simulateur y publie la télémétrie du four (appareil→cloud uniquement) |

> **Why is IoT Hub in West Europe, not Sweden Central?** IoT Hub is **not available** in
> Sweden Central, so it is pinned to another **EU region** (West Europe) to respect EU data
> residency (Principle III).
>
> 🇫🇷 **FR — Pourquoi IoT Hub est-il en Europe de l'Ouest et non en Suède Centre ?** IoT Hub
> n'est **pas disponible** en Suède Centre ; il est donc placé dans une autre **région de
> l'UE** (Europe de l'Ouest) pour respecter la résidence des données (Principe III).

### C. AI / Generative AI / IA générative

| Resource | Type | Role |
|----------|------|------|
| `aif-novastee-dev-ox26fi` | **Microsoft Foundry (AI Services)** | Hosts GPT chat/reasoning models + embeddings for the P4 knowledge assistant |
| `aif-…/novasteel-knowledge` | **Foundry project** | The project workspace for the knowledge-capture assistant |

> 🇫🇷 **FR :**
> | Ressource | Type | Rôle |
> |-----------|------|------|
> | `aif-novastee-dev-ox26fi` | **Microsoft Foundry (AI Services)** | Héberge les modèles GPT (dialogue/raisonnement) + embeddings pour l'assistant savoir P4 |
> | `aif-…/novasteel-knowledge` | **Projet Foundry** | L'espace projet de l'assistant de capture du savoir |

### D. Application compute / Calcul applicatif

| Resource | Type | Role |
|----------|------|------|
| `cae-novastee-dev-ox26fi` | **Container Apps environment** | Managed home for containerized apps (no VMs) |
| `sim-novastee-dev-ox26fi` | **Container App — the simulator** | The steel-factory telemetry simulator + its web UI (the D3 sensor chart you saw) |
| `energy-dispatch` | **Container App** | The P2 energy-optimization microservice |
| `func-novastee-dev-ox26fi` (+ `plan-…`) | **Azure Function App** | Serverless compute for the energy-dispatch agent |
| `acrnovasteedevox26fi` | **Container Registry** | Stores the Docker images the container apps run |
| `fnsnovasteeox26fi…` | **Storage account** | Backing storage for the Function App |

> 🇫🇷 **FR :**
> | Ressource | Type | Rôle |
> |-----------|------|------|
> | `cae-novastee-dev-ox26fi` | **Environnement Container Apps** | Hébergement managé d'applications conteneurisées (pas de VM) |
> | `sim-novastee-dev-ox26fi` | **Container App — le simulateur** | Le simulateur de télémétrie de l'aciérie + son UI web (le graphique capteurs D3) |
> | `energy-dispatch` | **Container App** | Le micro-service d'optimisation énergétique P2 |
> | `func-novastee-dev-ox26fi` | **Azure Function App** | Calcul « serverless » pour l'agent de pilotage énergétique |
> | `acrnovasteedevox26fi` | **Container Registry** | Stocke les images Docker exécutées par les container apps |
> | `fnsnovasteeox26fi…` | **Compte de stockage** | Stockage de support de la Function App |

> **Vocabulary — Container / Container App / Serverless:** A *container* packages an app with
> everything it needs to run. *Azure Container Apps* runs containers without managing servers.
> *Serverless* (Functions) runs your code on demand, you pay per execution — no VM to manage.
>
> 🇫🇷 **FR — Conteneur / Container App / Serverless :** Un *conteneur* empaquette une
> application avec tout le nécessaire pour s'exécuter. *Azure Container Apps* exécute des
> conteneurs sans gérer de serveurs. *Serverless* (Functions) exécute votre code à la demande,
> vous payez par exécution — sans VM à gérer.

### E. Governance, security & operations / Gouvernance, sécurité et exploitation

| Resource | Type | Role |
|----------|------|------|
| `id-novasteel-dev` | **Managed Identity** | A password-less identity apps use to authenticate to Azure services |
| `kvnovasteedevox26fi` | **Key Vault** | Securely stores secrets/keys (no passwords in code) |
| `log-novasteel-dev` | **Log Analytics workspace** | Central log store for monitoring |
| `appi-novasteel-dev` | **Application Insights** | Application performance monitoring (APM) + failure detection |
| `ag-novasteel-dev` | **Action Group** | Who/how to notify when an alert fires |
| `alert-…-model-drift` | **Alert rule** | Fires when an ML model's accuracy drifts |
| `alert-…-telemetry-freshness` | **Alert rule** | Fires when sensor data goes stale/missing |
| `logic-novastee-fabricpause-dev` | **Logic App** | Automatically **pauses the Fabric capacity nightly at 02:00** (cost control) |

> 🇫🇷 **FR :**
> | Ressource | Type | Rôle |
> |-----------|------|------|
> | `id-novasteel-dev` | **Identité managée** | Identité sans mot de passe utilisée par les apps pour s'authentifier auprès des services Azure |
> | `kvnovasteedevox26fi` | **Key Vault (coffre-fort)** | Stocke secrets/clés de façon sécurisée (aucun mot de passe dans le code) |
> | `log-novasteel-dev` | **Espace Log Analytics** | Magasin central des journaux pour la supervision |
> | `appi-novasteel-dev` | **Application Insights** | Supervision de la performance applicative (APM) + détection des pannes |
> | `ag-novasteel-dev` | **Groupe d'actions** | Qui/comment notifier lorsqu'une alerte se déclenche |
> | `alert-…-model-drift` | **Règle d'alerte** | Se déclenche quand la précision d'un modèle dérive |
> | `alert-…-telemetry-freshness` | **Règle d'alerte** | Se déclenche quand les données capteurs deviennent périmées/absentes |
> | `logic-novastee-fabricpause-dev` | **Logic App** | **Met en pause la capacité Fabric chaque nuit à 02:00** (maîtrise des coûts) |

> **Vocabulary — Managed Identity:** an Azure-managed account for a service so it can log in
> to other services **without storing a password**. Best practice used throughout this project.
>
> 🇫🇷 **FR — Identité managée :** un compte géré par Azure pour un service, lui permettant de
> se connecter à d'autres services **sans stocker de mot de passe**. Bonne pratique utilisée
> partout dans ce projet.

---

## 3.3 What is NOT deployed (and why) / Ce qui n'est PAS déployé (et pourquoi)

The project deliberately **excludes** services like Azure Machine Learning and Azure AI
Search. Machine learning lives **inside Fabric Data Science**, and retrieval/RAG lives in
**Foundry IQ**. This keeps the stack **unified and governable** (Principle V — "Scoped,
Unified Stack").

> 🇫🇷 **FR :** Le projet **exclut** volontairement des services comme Azure Machine Learning et
> Azure AI Search. L'apprentissage automatique se fait **dans Fabric Data Science**, et la
> recherche/RAG dans **Foundry IQ**. Cela garde une pile **unifiée et gouvernable** (Principe V
> — « pile unifiée et à périmètre maîtrisé »).

---

## 3.4 Cost-control mechanism / Mécanisme de maîtrise des coûts

The most expensive resource is the **Fabric capacity**. A **Logic App** pauses it every night
at 02:00 (Sweden/W-Europe time). Pausing stops compute billing; the capacity must be
**resumed** before Fabric workloads run again. (The simulator's Settings page can resume it.)

> 🇫🇷 **FR :** La ressource la plus coûteuse est la **capacité Fabric**. Une **Logic App** la
> met en pause chaque nuit à 02:00 (heure Suède/Europe de l'Ouest). La pause arrête la
> facturation du calcul ; la capacité doit être **réactivée** avant de relancer les charges
> Fabric. (La page Paramètres du simulateur peut la réactiver.)

**Next:** [04 — Microsoft Fabric fundamentals »](04-fabric-fundamentals.md)

> 🇫🇷 **FR : Suite :** [04 — Les fondamentaux de Microsoft Fabric »](04-fabric-fundamentals.md)
