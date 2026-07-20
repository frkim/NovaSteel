# 02 — Architecture & Data Flow

This page gives the **big picture**: how data travels from a sensor on the plant floor all
the way to a dashboard or an AI recommendation.

> 🇫🇷 **FR :** Cette page donne la **vue d'ensemble** : comment une donnée voyage d'un capteur
> sur le site industriel jusqu'à un tableau de bord ou une recommandation d'IA.

---

## 2.1 The one-paragraph mental model / Le modèle mental en un paragraphe

Sensors on the furnace send readings **one way, out of the plant**, into **Azure IoT Hub**
(the cloud front door for devices). From there the data enters **Microsoft Fabric**, where it
is stored in **OneLake** (the shared data lake), cleaned and refined in **three quality
layers** (Bronze → Silver → Gold), analyzed in real time, used to **train and run AI
models**, and finally shown in **Power BI dashboards** or answered by an **AI assistant** —
always with a **human approving** any recommended action.

> 🇫🇷 **FR :** Les capteurs du four envoient leurs relevés **dans un seul sens, hors de
> l'usine**, vers **Azure IoT Hub** (la porte d'entrée cloud des appareils). De là, les données
> entrent dans **Microsoft Fabric**, où elles sont stockées dans **OneLake** (le lac de données
> partagé), nettoyées et raffinées en **trois couches de qualité** (Bronze → Silver → Gold),
> analysées en temps réel, utilisées pour **entraîner et exécuter des modèles d'IA**, et enfin
> affichées dans des tableaux de bord **Power BI** ou restituées par un **assistant IA** —
> toujours avec un **humain qui valide** toute action recommandée.

---

## 2.2 End-to-end diagram / Schéma de bout en bout

```
 PLANT FLOOR (OT)          CLOUD INGESTION         MICROSOFT FABRIC (EU)                CONSUMPTION
┌───────────────┐         ┌──────────────┐        ┌───────────────────────────────┐   ┌─────────────┐
│ Sensors:      │         │ Azure IoT Hub│        │ Real-Time Intelligence        │   │ Power BI    │
│ thermal,      │  one    │  + Event Hubs│        │  Eventstream → Eventhouse(KQL) │   │ dashboards  │
│ vibration,    │  way    │              │──────► │            │         │         │   │             │
│ off-gas,      │ ──────► │ (device→     │        │            ▼         ▼         │   │ AI assistant│
│ energy meters │         │  cloud only) │        │        OneLake     Activator   │──►│ (Foundry)   │
└───────────────┘         └──────────────┘        │   Bronze→Silver→Gold  alerts   │   └─────────────┘
                                                  │            │                   │
 External feeds ─────────────────────────────────►│            ▼                   │
 (spot price, grid carbon)                        │      Data Science (ML)         │
                                                  │   P1 RUL · P2 energy · P3 QA   │
                                                  └───────────────────────────────┘
        ▲ Governance & security wrap everything: Entra ID, Key Vault, Purview, Azure Policy (EU-default)
```

> 🇫🇷 **FR :** Le schéma ci-dessus se lit de gauche à droite : **site industriel (OT)** →
> **ingestion cloud** (IoT Hub, sens unique) → **Microsoft Fabric** (temps réel, OneLake en
> couches Bronze/Silver/Gold, science des données) → **consommation** (Power BI, assistant IA).
> La **gouvernance et la sécurité** (Entra ID, Key Vault, Purview, Azure Policy « UE
> uniquement ») enveloppent l'ensemble.

---

## 2.3 OT vs IT, and the one-way boundary / OT vs IT, et la frontière à sens unique

**OT (Operational Technology)** is the plant-floor world: sensors, PLCs, SCADA — the systems
that physically control the furnace. **IT (Information Technology)** is the corporate/cloud
world: data, analytics, AI.

> 🇫🇷 **FR :** L'**OT (technologie opérationnelle)** est le monde de l'atelier : capteurs,
> automates (PLC), SCADA — les systèmes qui pilotent physiquement le four. L'**IT (technologie
> de l'information)** est le monde bureautique/cloud : données, analyse, IA.

Data flows **only outward**, from OT to IT. There is **no command path back** into the plant.
The AI can *observe and advise* but can **never send an instruction** to the furnace. This is
a hard safety rule (Principle IV) — a human operator is always the one who acts.

> 🇫🇷 **FR :** Les données circulent **uniquement vers l'extérieur**, de l'OT vers l'IT. Il
> n'existe **aucun chemin de commande en retour** vers l'usine. L'IA peut *observer et
> conseiller* mais ne peut **jamais envoyer d'instruction** au four. C'est une règle de sécurité
> stricte (Principe IV) — c'est toujours un opérateur humain qui agit.

> **Vocabulary — SCADA / PLC:** SCADA = *Supervisory Control And Data Acquisition* (the
> plant's control/monitoring system). PLC = *Programmable Logic Controller* (the industrial
> computer that drives a machine).
>
> 🇫🇷 **FR — SCADA / PLC (automate) :** SCADA = système de supervision et d'acquisition de
> données. PLC (API/automate programmable) = l'ordinateur industriel qui pilote une machine.

---

## 2.4 Three data "temperatures": hot, warm, cold / Trois « températures » de données

A single sensor stream is used three ways at once — a key Fabric idea.

> 🇫🇷 **FR :** Un même flux de capteurs est utilisé de trois façons simultanément — une idée
> clé de Fabric.

| Path | Speed | Purpose | Fabric engine |
|------|-------|---------|---------------|
| **Hot** | sub-second | Live furnace alerts, real-time dashboards | Real-Time Intelligence (Eventhouse/KQL, Activator) |
| **Warm** | minutes | Operational analytics, medallion refinement | Data Engineering (Spark notebooks), OneLake |
| **Cold** | hours/days | ML model training, BI history, back-testing | Data Science + OneLake Gold |

> 🇫🇷 **FR :**
> | Chemin | Vitesse | But | Moteur Fabric |
> |--------|---------|-----|---------------|
> | **Chaud** | infra-seconde | Alertes de four en direct, tableaux temps réel | Real-Time Intelligence (Eventhouse/KQL, Activator) |
> | **Tiède** | minutes | Analyse opérationnelle, raffinage médaillon | Data Engineering (notebooks Spark), OneLake |
> | **Froid** | heures/jours | Entraînement des modèles, historique BI, back-test | Data Science + OneLake Gold |

The power of Fabric is that all three read **one copy of the data** in OneLake — no copying
between separate systems.

> 🇫🇷 **FR :** La force de Fabric est que ces trois chemins lisent **une seule copie des
> données** dans OneLake — sans recopier entre des systèmes séparés.

---

## 2.5 The medallion (Bronze → Silver → Gold) / Le médaillon (Bronze → Argent → Or)

Data is refined in three named layers. Think of it as **raw → clean → ready-to-use**.

> 🇫🇷 **FR :** Les données sont raffinées en trois couches nommées. Pensez à **brut → propre →
> prêt à l'emploi**.

- **Bronze** = raw landing, kept **immutable** (never edited) for replay/audit.
- **Silver** = validated, deduplicated, freshness/quality flags added, partitioned by site.
- **Gold** = business-ready **features and marts** — the tables ML and dashboards consume.

> 🇫🇷 **FR :**
> - **Bronze** = arrivée brute, conservée **immuable** (jamais modifiée) pour rejeu/audit.
> - **Argent (Silver)** = validée, dédoublonnée, avec indicateurs de fraîcheur/qualité,
>   partitionnée par site.
> - **Or (Gold)** = **variables (features) et marts** prêts pour le métier — les tables
>   consommées par l'IA et les tableaux de bord.

Throughout, each reading keeps its **provenance** — where it came from (`sourceId`, `site`),
its `quality`, and its `origin` (real vs synthetic). Synthetic data is kept in a separate
bucket and **never counted in a real KPI**.

> 🇫🇷 **FR :** Tout au long, chaque relevé conserve sa **provenance** — d'où il vient
> (`sourceId`, `site`), sa `quality` (qualité), et son `origin` (réel vs synthétique). Les
> données synthétiques sont isolées et **jamais comptées dans un KPI réel**.

Details of every component are in [05-fabric-components-deployed.md](05-fabric-components-deployed.md).

> 🇫🇷 **FR :** Le détail de chaque composant se trouve dans
> [05-fabric-components-deployed.md](05-fabric-components-deployed.md).

---

## 2.6 Where the AI lives / Où se trouve l'IA

- **Predictive AI (P1/P2/P3)** trains and runs **inside Fabric Data Science** (MLflow
  experiments, model registry). The furnace hot-path alert can be served on live KQL data.
- **The energy optimizer (P2)** runs the heavy math (an optimization solver) **outside**
  Fabric, as an **Azure Functions / Container Apps** service, and reads Fabric's forecast.
- **Generative AI (P4)** runs in **Microsoft Foundry** (Azure OpenAI GPT models + Foundry IQ
  for grounding/retrieval), answering questions with **citations**.

> 🇫🇷 **FR :**
> - L'**IA prédictive (P1/P2/P3)** s'entraîne et s'exécute **dans Fabric Data Science**
>   (expériences MLflow, registre de modèles). L'alerte de four (chemin chaud) peut être servie
>   sur des données KQL en direct.
> - L'**optimiseur énergétique (P2)** exécute le calcul lourd (un solveur d'optimisation)
>   **hors** de Fabric, en tant que service **Azure Functions / Container Apps**, et lit la
>   prévision de Fabric.
> - L'**IA générative (P4)** s'exécute dans **Microsoft Foundry** (modèles GPT d'Azure OpenAI +
>   Foundry IQ pour l'ancrage/la recherche), en répondant avec des **citations**.

---

## 2.7 Design frameworks used / Cadres de conception utilisés

The architecture follows the **Azure Well-Architected Framework** (reliability, security,
cost, operational excellence, performance) and the **Cloud Adoption Framework**. It maps to a
**C4 model** (context → containers → components) in
[`First_Proposal/03-data-and-ai-design.md`](../First_Proposal/03-data-and-ai-design.md) and
[`3_c4model.md`](../0_preliminary%20analysis/3_c4model.md).

> 🇫🇷 **FR :** L'architecture suit le **Azure Well-Architected Framework** (fiabilité,
> sécurité, coût, excellence opérationnelle, performance) et le **Cloud Adoption Framework**.
> Elle se décline en un **modèle C4** (contexte → conteneurs → composants) dans les documents
> cités ci-dessus.

**Next:** [03 — Azure infrastructure »](03-azure-infrastructure.md)

> 🇫🇷 **FR : Suite :** [03 — Infrastructure Azure »](03-azure-infrastructure.md)
