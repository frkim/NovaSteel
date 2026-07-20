# 04 — Microsoft Fabric Fundamentals (for Newcomers)

This page explains **what Microsoft Fabric is** and the handful of core concepts you must know
before the deep dive in [05](05-fabric-components-deployed.md). No prior Fabric knowledge is
assumed.

> 🇫🇷 **FR :** Cette page explique **ce qu'est Microsoft Fabric** et la poignée de concepts
> essentiels à connaître avant la plongée détaillée du fichier [05](05-fabric-components-deployed.md).
> Aucune connaissance préalable de Fabric n'est requise.

---

## 4.1 What is Microsoft Fabric? / Qu'est-ce que Microsoft Fabric ?

Microsoft Fabric is an **all-in-one, SaaS analytics platform**. It bundles everything you
need to move, store, transform, analyze, and visualize data — plus do machine learning — in
**one product**, instead of stitching together many separate Azure services.

> 🇫🇷 **FR :** Microsoft Fabric est une **plateforme d'analytique tout-en-un, en mode SaaS**.
> Elle réunit tout ce qu'il faut pour déplacer, stocker, transformer, analyser et visualiser
> des données — et faire de l'apprentissage automatique — dans **un seul produit**, au lieu
> d'assembler de nombreux services Azure séparés.

> **Vocabulary — SaaS (Software as a Service):** software you use over the web without
> installing or managing servers; Microsoft runs the infrastructure for you. Fabric is SaaS,
> so there are **no clusters or VMs to manage** — you just use the workloads.
>
> 🇫🇷 **FR — SaaS (logiciel en tant que service) :** un logiciel utilisé via le web, sans
> installer ni gérer de serveurs ; Microsoft exploite l'infrastructure pour vous. Fabric est
> en SaaS : il n'y a **aucun cluster ni VM à gérer** — vous utilisez simplement les charges.

Fabric groups its capabilities into **workloads** (also called "experiences"): Data Factory,
Data Engineering, Data Science, Data Warehouse, Real-Time Intelligence, and Power BI. NovaSteel
uses all of them.

> 🇫🇷 **FR :** Fabric regroupe ses capacités en **charges de travail** (aussi appelées
> « expériences ») : Data Factory, Data Engineering, Data Science, Data Warehouse, Real-Time
> Intelligence et Power BI. NovaSteel les utilise toutes.

---

## 4.2 The four concepts that unlock everything / Les quatre concepts qui débloquent tout

### 1) Capacity (the engine) / La capacité (le moteur)

A **capacity** is the paid compute that powers Fabric, sold in **F-SKU** sizes (F2, F4, F8,
F16 …). The number is the amount of compute; higher = faster and more expensive. All
workspaces assigned to a capacity share its power. A capacity can be **paused** to stop
billing.

> 🇫🇷 **FR :** Une **capacité** est la puissance de calcul payante qui alimente Fabric, vendue
> en tailles **F-SKU** (F2, F4, F8, F16…). Le nombre correspond à la quantité de calcul ; plus
> il est élevé, plus c'est rapide et coûteux. Tous les espaces de travail rattachés à une
> capacité partagent sa puissance. Une capacité peut être **mise en pause** pour arrêter la
> facturation.

**NovaSteel note:** the capacity is `fabnovasteedevox26fi`. Spark notebooks need **at least
F4** (F2 refuses them with error 430). The capacity is paused nightly at 02:00 to save money.

> 🇫🇷 **FR : Note NovaSteel :** la capacité est `fabnovasteedevox26fi`. Les notebooks Spark
> exigent **au moins F4** (F2 les refuse avec l'erreur 430). La capacité est mise en pause
> chaque nuit à 02:00 pour économiser.

### 2) Workspace (the folder/team area) / L'espace de travail (le dossier/l'espace d'équipe)

A **workspace** is a collaborative container that holds your Fabric **items** (lakehouses,
notebooks, pipelines, reports…). Access is controlled by **workspace roles** (Admin, Member,
Contributor, Viewer). NovaSteel's workspace is **`novasteel-dev`**.

> 🇫🇷 **FR :** Un **espace de travail** est un conteneur collaboratif qui héberge vos
> **éléments** Fabric (lakehouses, notebooks, pipelines, rapports…). L'accès est contrôlé par
> des **rôles d'espace de travail** (Admin, Membre, Contributeur, Lecteur). L'espace de travail
> de NovaSteel est **`novasteel-dev`**.

> **Important:** workspace access is **separate** from Azure roles. Being an Azure subscription
> Owner or a tenant Global Admin does **not** grant workspace access — you must be added with a
> workspace role.
>
> 🇫🇷 **FR — Important :** l'accès à l'espace de travail est **distinct** des rôles Azure. Être
> Propriétaire d'un abonnement Azure ou Administrateur global du tenant ne donne **pas** accès
> à l'espace de travail — il faut y être ajouté avec un rôle d'espace de travail.

### 3) OneLake (the single lake) / OneLake (le lac unique)

**OneLake** is Fabric's built-in, tenant-wide **data lake** — "**OneDrive for data**." There
is **one logical copy** of your data, stored in open **Delta/Parquet** format, and **every**
Fabric engine reads it **without copying**. This is the heart of Fabric's value.

> 🇫🇷 **FR :** **OneLake** est le **lac de données** intégré de Fabric, à l'échelle du tenant —
> « **le OneDrive des données** ». Il existe **une seule copie logique** de vos données,
> stockée au format ouvert **Delta/Parquet**, et **chaque** moteur Fabric la lit **sans
> recopie**. C'est le cœur de la valeur de Fabric.

> **Vocabulary — Delta / Parquet:** *Parquet* is an efficient open columnar file format for
> analytics. *Delta Lake* adds reliability on top (transactions, versioning, "time travel").
>
> 🇫🇷 **FR — Delta / Parquet :** *Parquet* est un format de fichier colonne ouvert et efficace
> pour l'analytique. *Delta Lake* y ajoute la fiabilité (transactions, versionnage, « voyage
> dans le temps »).

Two OneLake superpowers used by NovaSteel:
- **Shortcuts** — point to data *in place* (e.g. an ERP export, or a KQL table) **without
  copying** it. Zero-copy virtualization.
- **Mirroring** — Fabric-managed **near-real-time replication** of an external database (SAP,
  Azure SQL…) into OneLake, with no custom ETL.

> 🇫🇷 **FR :** Deux super-pouvoirs de OneLake utilisés par NovaSteel :
> - **Shortcuts (raccourcis)** — pointent vers des données *sur place* (ex. un export ERP, ou
>   une table KQL) **sans les copier**. Virtualisation « zéro copie ».
> - **Mirroring (miroir)** — **réplication quasi temps réel** gérée par Fabric d'une base
>   externe (SAP, Azure SQL…) vers OneLake, sans ETL sur-mesure.

### 4) Items (the building blocks) / Les éléments (les briques)

Everything you create in a workspace is an **item**: a Lakehouse, a Notebook, an Eventstream,
a Data Pipeline, an ML Model, a Report, etc. The deployed items are the subject of
[file 05](05-fabric-components-deployed.md).

> 🇫🇷 **FR :** Tout ce que vous créez dans un espace de travail est un **élément** : un
> Lakehouse, un Notebook, un Eventstream, un pipeline de données, un modèle ML, un rapport,
> etc. Les éléments déployés font l'objet du [fichier 05](05-fabric-components-deployed.md).

---

## 4.3 Two ways data is stored: Lakehouse vs Eventhouse / Deux stockages : Lakehouse vs Eventhouse

Fabric offers different **stores** for different jobs. NovaSteel uses two:

> 🇫🇷 **FR :** Fabric propose différents **magasins** pour différents besoins. NovaSteel en
> utilise deux :

| Store | Best for | Query language | NovaSteel item |
|-------|----------|----------------|----------------|
| **Lakehouse** | Batch/analytical tables (medallion), files + tables together | Spark / T-SQL | `onelake_novasteel` |
| **Eventhouse (KQL DB)** | High-speed **time-series** streaming data | **KQL** | `novasteel_rti` |

> 🇫🇷 **FR :**
> | Magasin | Idéal pour | Langage de requête | Élément NovaSteel |
> |---------|-----------|--------------------|-------------------|
> | **Lakehouse** | Tables analytiques/par lots (médaillon), fichiers + tables ensemble | Spark / T-SQL | `onelake_novasteel` |
> | **Eventhouse (base KQL)** | Données de flux **séries temporelles** à grande vitesse | **KQL** | `novasteel_rti` |

> **Vocabulary — KQL (Kusto Query Language):** a fast query language for time-series/telemetry
> data. **T-SQL:** the SQL dialect for relational queries. **Spark:** a big-data engine for
> distributed processing (used in notebooks).
>
> 🇫🇷 **FR — KQL (langage de requête Kusto) :** un langage rapide pour interroger des données
> de séries temporelles/télémétrie. **T-SQL :** le dialecte SQL pour les requêtes
> relationnelles. **Spark :** un moteur big-data pour le traitement distribué (dans les
> notebooks).

---

## 4.4 How Power BI reads Gold instantly: Direct Lake / Direct Lake

**Power BI** is Fabric's dashboard tool. Normally BI tools either *import* data (fast but
stale) or *query live* (fresh but slower). **Direct Lake** mode reads Gold Delta tables
**directly from OneLake** — import-mode speed **with no import/refresh copy**. Fresh numbers,
one copy of data.

> 🇫🇷 **FR :** **Power BI** est l'outil de tableaux de bord de Fabric. Habituellement, les
> outils BI soit *importent* les données (rapide mais périmé), soit *interrogent en direct*
> (frais mais plus lent). Le mode **Direct Lake** lit les tables Gold Delta **directement
> depuis OneLake** — la vitesse du mode import **sans copie d'import/rafraîchissement**. Des
> chiffres frais, une seule copie des données.

---

## 4.5 Medallion recap / Rappel du médaillon

Inside the Lakehouse, data is refined in three zones — **Bronze** (raw), **Silver** (clean),
**Gold** (ready). See [02 §2.5](02-architecture-and-dataflow.md). This is where the "warm
path" lives, built by **Spark notebooks**.

> 🇫🇷 **FR :** Dans le Lakehouse, les données sont raffinées en trois zones — **Bronze**
> (brut), **Silver/Argent** (propre), **Gold/Or** (prêt). Voir [02 §2.5](02-architecture-and-dataflow.md).
> C'est là que vit le « chemin tiède », construit par des **notebooks Spark**.

---

## 4.6 Governance built in / Gouvernance intégrée

Fabric integrates **Purview** (lineage/catalog), **Entra ID** (identity), **Key Vault**
(secrets), **sensitivity labels**, and **Git/deployment pipelines** (Dev→Test→Prod). These make
NovaSteel's traceability and residency rules enforceable. Details in
[07-governance-security.md](07-governance-security.md).

> 🇫🇷 **FR :** Fabric intègre **Purview** (traçabilité/catalogue), **Entra ID** (identité),
> **Key Vault** (secrets), des **étiquettes de confidentialité**, et **Git/pipelines de
> déploiement** (Dev→Test→Prod). Cela rend applicables les règles de traçabilité et de résidence
> de NovaSteel. Détails dans [07-governance-security.md](07-governance-security.md).

**Next:** [05 — The Fabric components deployed (deep dive) »](05-fabric-components-deployed.md)

> 🇫🇷 **FR : Suite :** [05 — Les composants Fabric déployés (plongée détaillée) »](05-fabric-components-deployed.md)
