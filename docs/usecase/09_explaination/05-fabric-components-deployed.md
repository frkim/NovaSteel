# 05 — The Fabric Components Deployed (Deep Dive)

This is the **core** of the guide. It explains **every Fabric item actually deployed** in the
`novasteel-dev` workspace: what it is, **how it works**, how it connects to the others, and the
live NovaSteel specifics. Read it slowly — this is what you'll be asked about.

> 🇫🇷 **FR :** C'est le **cœur** du guide. Il explique **chaque élément Fabric réellement
> déployé** dans l'espace de travail `novasteel-dev` : ce que c'est, **comment ça marche**,
> comment ça se connecte aux autres, et les spécificités NovaSteel en direct. Lisez-le
> lentement — c'est là-dessus qu'on vous interrogera.

## 5.0 Inventory of live items / Inventaire des éléments en direct

| # | Item name | Fabric type | Section |
|---|-----------|-------------|---------|
| 1 | `onelake_novasteel` | **Lakehouse** (+ SQL analytics endpoint) | [5.1](#51-lakehouse--onelake_novasteel) |
| 2 | `novasteel_rti` | **Eventhouse** + **KQL Database** | [5.2](#52-eventhouse--kql-database--novasteel_rti) |
| 3 | `es_telemetry` | **Eventstream** | [5.3](#53-eventstream--es_telemetry) |
| 4 | `bronze_telemetry`, `silver_telemetry`, `gold_marts` | **Notebooks** (medallion) | [5.4](#54-notebooks--bronze_telemetry-silver_telemetry-gold_marts) |
| 5 | `df_mes_erp_eam` | **Data Pipeline** (Data Factory) | [5.5](#55-data-pipeline--df_mes_erp_eam) |
| 6 | `novasteel-p1-rul`, `novasteel-p3-quality` | **ML Experiments** + **ML Models** | [5.6](#56-ml-experiments--ml-models) |
| 7 | `p1_rul_scoring` | **Notebook** (scoring runner) | [5.7](#57-notebook--p1_rul_scoring) |
| 8 | `NovaSteel` | **Semantic Model** (Power BI) | [5.8](#58-semantic-model--novasteel) |

> 🇫🇷 **FR :** Le tableau ci-dessus liste tous les éléments Fabric déployés et la section qui
> les explique. Chaque type est détaillé ci-dessous.

---

## 5.1 Lakehouse — `onelake_novasteel`

**What it is.** A **Lakehouse** is a Fabric item that stores both **files** and **tables**
(Delta format) in OneLake, queryable with **Spark** *and* **T-SQL**. It is the home of the
**medallion** (Bronze/Silver/Gold) tables. Think of it as a database and a file folder merged
into one, sitting on the shared lake.

> 🇫🇷 **FR : Ce que c'est.** Un **Lakehouse** est un élément Fabric qui stocke à la fois des
> **fichiers** et des **tables** (format Delta) dans OneLake, interrogeable en **Spark** *et*
> **T-SQL**. C'est le foyer des tables **médaillon** (Bronze/Silver/Or). Voyez-le comme une base
> de données et un dossier de fichiers fusionnés, posés sur le lac partagé.

**How it works here.** The three medallion notebooks read and write Delta tables inside this
lakehouse. Notebooks reference tables by **bare name** (e.g. `spark.read.table("telemetry_raw_kql")`)
because the lakehouse is **bound as their default lakehouse**. It also holds a **shortcut**
(`telemetry_raw_kql`) that points at the live KQL telemetry table — zero-copy — so notebooks
can read streaming data as if it were a local table.

> 🇫🇷 **FR : Comment ça marche ici.** Les trois notebooks médaillon lisent et écrivent des
> tables Delta dans ce lakehouse. Les notebooks référencent les tables par **nom simple** (ex.
> `spark.read.table("telemetry_raw_kql")`) car le lakehouse est **rattaché comme leur lakehouse
> par défaut**. Il contient aussi un **shortcut** (`telemetry_raw_kql`) pointant vers la table
> de télémétrie KQL en direct — sans copie — pour que les notebooks lisent le flux comme une
> table locale.

**SQL analytics endpoint (`onelake_novasteel`).** Every Lakehouse automatically gets a
**read-only T-SQL endpoint**. Any SQL/BI tool can query the Gold Delta tables with standard
SQL — **no data movement**. This is how Power BI and analysts read Gold.

> 🇫🇷 **FR : Point de terminaison SQL analytique.** Chaque Lakehouse obtient automatiquement un
> **point de terminaison T-SQL en lecture seule**. N'importe quel outil SQL/BI peut interroger
> les tables Gold Delta en SQL standard — **sans déplacement de données**. C'est ainsi que Power
> BI et les analystes lisent la couche Gold.

> **Vocabulary — Endpoint:** a network address/service you connect to. Here, a SQL "front door"
> onto the lakehouse data.
>
> 🇫🇷 **FR — Point de terminaison (endpoint) :** une adresse/un service réseau auquel on se
> connecte. Ici, une « porte SQL » sur les données du lakehouse.

---

## 5.2 Eventhouse + KQL Database — `novasteel_rti`

**What it is.** An **Eventhouse** is Fabric's **Real-Time Intelligence** store for
**time-series / streaming** data. Inside it lives a **KQL Database** — a Kusto database
optimized for sub-second queries over **billions** of sensor readings. `RTI` stands for
**Real-Time Intelligence**.

> 🇫🇷 **FR : Ce que c'est.** Un **Eventhouse** est le magasin **Real-Time Intelligence** de
> Fabric pour les données **séries temporelles / de flux**. Il contient une **base KQL** — une
> base Kusto optimisée pour des requêtes infra-seconde sur des **milliards** de relevés de
> capteurs. `RTI` signifie **Real-Time Intelligence** (intelligence temps réel).

**How it works here.** Live simulator telemetry arrives (via the Eventstream) into a **staging
table** `TelemetryIngest`, because IoT Hub device messages are **batches**
(`SimulatorDeviceMessage.readings[]`). A KQL **update policy** called `ExpandTelemetry` uses
`mv-expand` to **fan each batch out** into flat rows in the `TelemetryRaw` table — preserving
provenance (`origin`, `sourceId`, `site`, `quality`). Verified live: ~7,000 rows every 3
minutes, all `origin = Synthetic`.

> 🇫🇷 **FR : Comment ça marche ici.** La télémétrie du simulateur en direct arrive (via
> l'Eventstream) dans une **table de préparation** `TelemetryIngest`, car les messages IoT Hub
> sont des **lots** (`SimulatorDeviceMessage.readings[]`). Une **politique de mise à jour** KQL
> nommée `ExpandTelemetry` utilise `mv-expand` pour **éclater chaque lot** en lignes plates dans
> la table `TelemetryRaw` — en préservant la provenance (`origin`, `sourceId`, `site`,
> `quality`). Vérifié en direct : ~7 000 lignes toutes les 3 minutes, toutes en
> `origin = Synthetic`.

**OneLake availability (mirroring to the lake).** The KQL table has **OneLake availability**
enabled, which **mirrors** it to OneLake as Delta files. A lakehouse **shortcut**
(`telemetry_raw_kql`) then exposes it to the Spark notebooks. This is the bridge from the
**hot path** (KQL) to the **warm path** (medallion).

> 🇫🇷 **FR : Disponibilité OneLake (miroir vers le lac).** La table KQL a la **disponibilité
> OneLake** activée, ce qui la **réplique** vers OneLake au format Delta. Un **shortcut** de
> lakehouse (`telemetry_raw_kql`) l'expose ensuite aux notebooks Spark. C'est le pont entre le
> **chemin chaud** (KQL) et le **chemin tiède** (médaillon).

**What else RTI can do.** Anomaly detection, thermal-drift trends, and **Activator** rules
(no-code alerts) that fire when a furnace crosses a wear threshold or energy/carbon spikes —
routed to operators (Teams/email).

> 🇫🇷 **FR : Ce que la RTI sait faire d'autre.** Détection d'anomalies, tendances de dérive
> thermique, et règles **Activator** (alertes sans code) qui se déclenchent quand un four
> dépasse un seuil d'usure ou que l'énergie/le carbone s'emballe — routées vers les opérateurs
> (Teams/e-mail).

> **Vocabulary — Time-series / telemetry:** measurements recorded over time (e.g. temperature
> every second). **Anomaly detection:** automatically spotting abnormal patterns.
>
> 🇫🇷 **FR — Séries temporelles / télémétrie :** des mesures enregistrées dans le temps (ex.
> température chaque seconde). **Détection d'anomalies :** repérage automatique de comportements
> anormaux.

---

## 5.3 Eventstream — `es_telemetry`

**What it is.** An **Eventstream** is a **no-code pipe** that ingests streaming events and
**routes** them to multiple destinations at once. It is the "T-junction" that fans one stream
out to several consumers.

> 🇫🇷 **FR : Ce que c'est.** Un **Eventstream** est un **tuyau sans code** qui ingère des
> événements de flux et les **route** vers plusieurs destinations à la fois. C'est le « raccord
> en T » qui distribue un flux vers plusieurs consommateurs.

**How it works here.** It connects **Azure IoT Hub** (`iot-novastee-dev-ox26fi`, consumer
group `fabric-rti`) as its source and delivers events to the **Eventhouse** (`TelemetryIngest`
staging table). The binding was automated via the Fabric **connections API** using connection
type **`IoTHub`** (exact casing) with a Key-Vault-sourced SAS credential.

> 🇫🇷 **FR : Comment ça marche ici.** Il connecte **Azure IoT Hub** (`iot-novastee-dev-ox26fi`,
> groupe de consommateurs `fabric-rti`) comme source et livre les événements à l'**Eventhouse**
> (table de préparation `TelemetryIngest`). La liaison a été automatisée via l'**API de
> connexions** de Fabric, type de connexion **`IoTHub`** (casse exacte), avec un identifiant SAS
> issu de Key Vault.

**The data path in one line:** `Simulator → IoT Hub → Eventstream (es_telemetry) →
Eventhouse TelemetryIngest → (ExpandTelemetry) → TelemetryRaw`.

> 🇫🇷 **FR : Le chemin des données en une ligne :** `Simulateur → IoT Hub → Eventstream
> (es_telemetry) → Eventhouse TelemetryIngest → (ExpandTelemetry) → TelemetryRaw`.

> **Vocabulary — Consumer group:** a named "read cursor" on IoT Hub so multiple readers
> (Fabric, monitoring…) can each read the stream independently. **SAS:** Shared Access
> Signature, a scoped access token.
>
> 🇫🇷 **FR — Groupe de consommateurs :** un « curseur de lecture » nommé sur IoT Hub permettant
> à plusieurs lecteurs (Fabric, supervision…) de lire le flux indépendamment. **SAS :** signature
> d'accès partagé, un jeton d'accès à portée limitée.

---

## 5.4 Notebooks — `bronze_telemetry`, `silver_telemetry`, `gold_marts`

**What they are.** **Notebooks** are interactive documents mixing code (here **PySpark**) and
text. They run on Fabric's **Spark** engine and are the **compute** of the medallion — they
transform data Bronze → Silver → Gold. They are scheduled **daily at 06:00 UTC**.

> 🇫🇷 **FR : Ce que c'est.** Les **notebooks** sont des documents interactifs mêlant code (ici
> **PySpark**) et texte. Ils s'exécutent sur le moteur **Spark** de Fabric et constituent le
> **calcul** du médaillon — ils transforment les données Bronze → Argent → Or. Ils sont
> planifiés **chaque jour à 06:00 UTC**.

| Notebook | Layer | What it does |
|----------|-------|--------------|
| `bronze_telemetry` | Bronze | Append-only landing of raw telemetry; **quarantines** readings missing provenance (never defaults them) |
| `silver_telemetry` | Silver | Deduplicates, adds **freshness/quality flags**, partitions by **site** |
| `gold_marts` | Gold | Builds **KPI marts** (real vs synthetic kept separate) and **furnace feature** tables for ML |

> 🇫🇷 **FR :**
> | Notebook | Couche | Ce qu'il fait |
> |----------|--------|---------------|
> | `bronze_telemetry` | Bronze | Atterrissage en ajout seul de la télémétrie brute ; **met en quarantaine** les relevés sans provenance (jamais de valeur par défaut) |
> | `silver_telemetry` | Argent | Dédoublonne, ajoute des **indicateurs de fraîcheur/qualité**, partitionne par **site** |
> | `gold_marts` | Or | Construit les **marts de KPI** (réel vs synthétique séparés) et les tables de **variables de four** pour l'IA |

**Key design rule.** A tested, Spark-free reference implementation
(`platform/medallion/transforms.py`) defines the exact semantics; the Spark notebooks
**mirror** it so their behavior matches a passing **pytest** provenance/data-quality gate
(`test_provenance_propagation.py`). This enforces **Principle VIII (test-first)** and
**Principle IX (synthetic integrity)**.

> 🇫🇷 **FR : Règle de conception clé.** Une implémentation de référence testée et sans Spark
> (`platform/medallion/transforms.py`) définit la sémantique exacte ; les notebooks Spark la
> **reproduisent** pour que leur comportement corresponde à un test **pytest** de
> provenance/qualité qui passe (`test_provenance_propagation.py`). Cela applique le **Principe
> VIII (test d'abord)** et le **Principe IX (intégrité du synthétique)**.

> **Vocabulary — Spark / PySpark:** Spark is a distributed engine that processes large data in
> parallel; PySpark is its Python interface. **pytest:** a Python testing framework.
>
> 🇫🇷 **FR — Spark / PySpark :** Spark est un moteur distribué qui traite de gros volumes en
> parallèle ; PySpark est son interface Python. **pytest :** un cadre de test Python.

> ⚠️ **Capacity note:** Spark notebooks need **≥ F4**. On F2 they fail with HTTP 430
> `TooManyRequestsForCapacity`. The capacity is bumped to F4 for the batch window, then dropped
> back.
>
> 🇫🇷 **FR — ⚠️ Note capacité :** les notebooks Spark exigent **≥ F4**. En F2 ils échouent avec
> l'erreur HTTP 430 `TooManyRequestsForCapacity`. La capacité est augmentée à F4 pour la fenêtre
> de traitement, puis rabaissée.

---

## 5.5 Data Pipeline — `df_mes_erp_eam`

**What it is.** A **Data Pipeline** (Fabric **Data Factory**) is a **no-code orchestrator** —
it copies and moves data on a schedule using 100+ connectors. It complements notebooks:
**pipelines orchestrate; notebooks compute**.

> 🇫🇷 **FR : Ce que c'est.** Un **pipeline de données** (Fabric **Data Factory**) est un
> **orchestrateur sans code** — il copie et déplace des données selon un planning via plus de
> 100 connecteurs. Il complète les notebooks : **les pipelines orchestrent ; les notebooks
> calculent**.

**How it works here.** `df_mes_erp_eam` batches **MES / ERP / EAM** business systems plus a
**market feed** (energy spot price, grid carbon) into Bronze. Crucially it is **read/propose
only** — it *reads* the systems of record and proposes; there is **no write-back** path,
honoring the one-way OT→IT boundary (Principle IV).

> 🇫🇷 **FR : Comment ça marche ici.** `df_mes_erp_eam` importe par lots les systèmes métier
> **MES / ERP / EAM** ainsi qu'un **flux de marché** (prix spot de l'énergie, carbone réseau)
> vers Bronze. Point crucial : il est **en lecture/proposition seule** — il *lit* les systèmes
> de référence et propose ; il n'y a **aucun** chemin d'écriture en retour, respectant la
> frontière unidirectionnelle OT→IT (Principe IV).

> **Vocabulary — MES / ERP / EAM:** *MES* = Manufacturing Execution System (shop-floor
> production execution). *ERP* = Enterprise Resource Planning (finance, orders, inventory).
> *EAM* = Enterprise Asset Management (maintenance, equipment).
>
> 🇫🇷 **FR — MES / ERP / EAM :** *MES* = système d'exécution de la fabrication (pilotage de la
> production en atelier). *ERP* = progiciel de gestion intégré (finance, commandes, stocks).
> *EAM* = gestion des actifs d'entreprise (maintenance, équipements).

---

## 5.6 ML Experiments + ML Models

**What they are.** In **Fabric Data Science**, an **ML Experiment** is a tracked series of
training runs (backed by **MLflow**); an **ML Model** is a **registered, versioned** trained
model you can promote and score with. Together they cover the whole ML lifecycle **inside
Fabric** — no separate Azure ML service (Principle V).

> 🇫🇷 **FR : Ce que c'est.** Dans **Fabric Data Science**, une **expérience ML** est une série
> suivie d'entraînements (via **MLflow**) ; un **modèle ML** est un modèle entraîné
> **enregistré et versionné** que l'on peut promouvoir et utiliser pour scorer. Ensemble, ils
> couvrent tout le cycle de vie ML **dans Fabric** — sans service Azure ML séparé (Principe V).

| Experiment / Model | Pillar | Purpose |
|--------------------|--------|---------|
| `novasteel-p1-rul` | P1 | Furnace-lining **Remaining Useful Life** regression + "fails within 21 days" classifier |
| `novasteel-p3-quality` | P3 | High-grade **quality/yield** model |

> 🇫🇷 **FR :**
> | Expérience / Modèle | Pilier | But |
> |---------------------|--------|-----|
> | `novasteel-p1-rul` | P1 | Régression de la **durée de vie résiduelle** du revêtement + classifieur « défaillance sous 21 jours » |
> | `novasteel-p3-quality` | P3 | Modèle **qualité/rendement** haut de gamme |

> **Vocabulary — MLflow:** an open-source tool to track experiments, parameters, metrics and
> register models. **Regression vs classifier:** regression predicts a number (days left); a
> classifier predicts a category (will/won't fail in 21 days).
>
> 🇫🇷 **FR — MLflow :** un outil open-source pour suivre les expériences, paramètres, métriques
> et enregistrer les modèles. **Régression vs classifieur :** la régression prédit un nombre
> (jours restants) ; le classifieur prédit une catégorie (défaillance sous 21 jours ou non).

---

## 5.7 Notebook — `p1_rul_scoring`

**What it is.** A dedicated notebook that **scores** the P1 model on **live features**. In the
POC it doubles as a **runner**: a validation script sets its body per pillar and runs it on
live Spark to produce and report predictions.

> 🇫🇷 **FR : Ce que c'est.** Un notebook dédié qui **score** le modèle P1 sur des **variables
> en direct**. Dans le POC, il sert aussi de **lanceur** : un script de validation ajuste son
> contenu par pilier et l'exécute sur Spark en direct pour produire et restituer des
> prédictions.

**Proven live (SC-003).** It ingests a **degrading-furnace** series, queries it back from the
Eventhouse, and produces a `LiningFailureRisk` prediction with **`timeToFailureDays ≥ 21`** —
demonstrating objective **O3** end-to-end.

> 🇫🇷 **FR : Démontré en direct (SC-003).** Il ingère une série de **four en dégradation**, la
> relit depuis l'Eventhouse, et produit une prédiction `LiningFailureRisk` avec
> **`timeToFailureDays ≥ 21`** — démontrant l'objectif **O3** de bout en bout.

---

## 5.8 Semantic Model — `NovaSteel`

**What it is.** A **Semantic Model** (formerly "Power BI dataset") is the **business layer**
over the data: it defines tables, relationships, and measures (KPIs) so dashboards and the AI
assistant all speak the **same certified definitions**. Power BI reports read it — ideally in
**Direct Lake** mode over Gold.

> 🇫🇷 **FR : Ce que c'est.** Un **modèle sémantique** (ancien « jeu de données Power BI ») est
> la **couche métier** au-dessus des données : il définit les tables, relations et mesures
> (KPI) pour que les tableaux de bord et l'assistant IA parlent tous les **mêmes définitions
> certifiées**. Les rapports Power BI le lisent — idéalement en mode **Direct Lake** sur Gold.

> **Vocabulary — Measure / KPI:** a calculated metric (e.g. "energy per ton"). **Semantic
> model:** the shared, governed definition of tables + measures used by all reports.
>
> 🇫🇷 **FR — Mesure / KPI :** un indicateur calculé (ex. « énergie par tonne »). **Modèle
> sémantique :** la définition partagée et gouvernée des tables + mesures utilisée par tous les
> rapports.

---

## 5.9 How they all connect / Comment tout se connecte

```
IoT Hub ──► Eventstream(es_telemetry) ──► Eventhouse KQL(novasteel_rti: TelemetryIngest→TelemetryRaw)
                                                   │  (OneLake availability = mirror to Delta)
                                                   ▼
                                    Lakehouse(onelake_novasteel) shortcut: telemetry_raw_kql
                                                   │
                 Notebooks: bronze_telemetry ─► silver_telemetry ─► gold_marts  (daily 06:00 UTC)
                                                   │  (Gold features + marts)
                        ┌──────────────────────────┼───────────────────────────┐
                        ▼                          ▼                            ▼
        ML Experiments/Models (P1,P3)     Semantic Model(NovaSteel)     SQL analytics endpoint
        + p1_rul_scoring (live RUL)         → Power BI (Direct Lake)     → any SQL/BI tool
 Data Pipeline(df_mes_erp_eam): MES/ERP/EAM + market ──► Bronze (read/propose only)
```

> 🇫🇷 **FR :** Le schéma ci-dessus montre l'enchaînement : IoT Hub → Eventstream → Eventhouse
> (KQL) → miroir OneLake → shortcut du Lakehouse → notebooks médaillon (Bronze→Argent→Or) → puis
> Gold alimente les modèles ML (P1/P3), le modèle sémantique (→ Power BI en Direct Lake) et le
> point de terminaison SQL. En parallèle, le pipeline de données importe MES/ERP/EAM + marché
> vers Bronze, en lecture/proposition seule.

**Next:** [06 — The AI workloads (pillars) »](06-ai-workloads.md)

> 🇫🇷 **FR : Suite :** [06 — Les charges de travail IA (piliers) »](06-ai-workloads.md)
