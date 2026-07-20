# 01 — The Project & Its Objectives

## 1.1 Who is NovaSteel? / Qui est NovaSteel ?

NovaSteel is a (fictional) European steel manufacturer operating **blast furnaces** and
**rolling mills** across **four plants in four EU countries**. It produces **high-grade
automotive steel** — a premium product where quality and consistency command higher prices.

> 🇫🇷 **FR :** NovaSteel est un fabricant d'acier européen (fictif) qui exploite des
> **hauts-fourneaux** et des **laminoirs** sur **quatre usines dans quatre pays de l'UE**. Il
> produit de l'**acier automobile haut de gamme** — un produit premium où la qualité et la
> régularité justifient des prix plus élevés.

Steelmaking is **energy-intensive, safety-critical, and capital-heavy**. Small percentage
improvements in energy, emissions, uptime, or yield translate into **millions of euros** and
tonnes of CO₂ saved.

> 🇫🇷 **FR :** La sidérurgie est **gourmande en énergie, critique pour la sécurité et très
> capitalistique**. De petites améliorations en pourcentage sur l'énergie, les émissions, la
> disponibilité ou le rendement se traduisent par des **millions d'euros** et des tonnes de
> CO₂ économisées.

---

## 1.2 The four problems / Les quatre problèmes

1. **Furnace-lining failures** are unpredictable and cost **~€8M per event** (unplanned
   outage + damage + lost production).
2. **Energy and CO₂ costs** are high and volatile (electricity prices, EU emissions trading).
3. **High-grade yield** varies — some heats miss premium quality and are downgraded.
4. **Retiring expertise** — senior operators' know-how leaves with them.

> 🇫🇷 **FR :**
> 1. Les **défaillances du revêtement réfractaire des fours** sont imprévisibles et coûtent
>    **~8 M€ par événement** (arrêt non planifié + dommages + production perdue).
> 2. Les **coûts d'énergie et de CO₂** sont élevés et volatils (prix de l'électricité, marché
>    européen des quotas d'émission).
> 3. Le **rendement haut de gamme** varie — certaines coulées ratent la qualité premium et
>    sont déclassées.
> 4. Le **départ des experts** — le savoir-faire des opérateurs seniors part avec eux.

> **Vocabulary — "heat":** in steelmaking, a *heat* is one batch/melt of steel produced by a
> furnace. "Ruining a heat" means spoiling a full batch.
>
> 🇫🇷 **FR — « coulée » (heat) :** en sidérurgie, une *coulée* est un lot/une fusion d'acier
> produit par un four. « Gâcher une coulée » signifie perdre un lot complet.

---

## 1.3 The four objectives (O1–O4) / Les quatre objectifs (O1–O4)

These are the measurable targets the platform must help achieve. They are the headline
numbers to remember for the defense.

> 🇫🇷 **FR :** Ce sont les cibles mesurables que la plateforme doit aider à atteindre. Ce sont
> les chiffres phares à retenir pour la soutenance.

| ID | Objective | Metric | Target | Owner |
|----|-----------|--------|--------|-------|
| **O1** | Cut energy intensity | Energy per ton (kWh/t, €/t) | **−14 %** | COO / Energy |
| **O2** | Cut emissions | CO₂ per ton (tCO₂/t) | **−22 %** | Head of Sustainability / ESG |
| **O3** | Prevent furnace failures | Lead time of lining-failure alert | **≥ 21 days** | COO / Maintenance |
| **O4** | Improve quality | High-grade yield; Cp/Cpk | **+8 %** yield | Head of Quality |

> 🇫🇷 **FR :**
> | ID | Objectif | Indicateur | Cible | Responsable |
> |----|----------|-----------|-------|-------------|
> | **O1** | Réduire l'intensité énergétique | Énergie par tonne (kWh/t, €/t) | **−14 %** | COO / Énergie |
> | **O2** | Réduire les émissions | CO₂ par tonne (tCO₂/t) | **−22 %** | Resp. Durabilité / ESG |
> | **O3** | Éviter les défaillances de four | Délai d'anticipation de l'alerte | **≥ 21 jours** | COO / Maintenance |
> | **O4** | Améliorer la qualité | Rendement haut de gamme ; Cp/Cpk | **+8 %** de rendement | Resp. Qualité |

**Why 21 days?** A furnace lining takes ~3 weeks to plan and execute a controlled repair. A
warning **≥21 days** ahead turns a catastrophic ~€8M failure into a **planned maintenance
stop**.

> 🇫🇷 **FR : Pourquoi 21 jours ?** Le revêtement d'un four demande ~3 semaines pour planifier
> et réaliser une réparation contrôlée. Une alerte **≥21 jours** à l'avance transforme une
> défaillance catastrophique à ~8 M€ en un **arrêt de maintenance planifié**.

---

## 1.4 The four pillars (P1–P4) / Les quatre piliers (P1–P4)

The objectives are delivered by four **workloads** ("pillars"), each independently
shippable, delivered in priority order.

> 🇫🇷 **FR :** Les objectifs sont atteints par quatre **charges de travail** (« piliers »),
> chacune livrable indépendamment, dans l'ordre de priorité.

| Pillar | Name | What it does | Serves |
|--------|------|--------------|--------|
| **P1** | Predictive maintenance | Predicts furnace-lining **remaining useful life** and a "fails within 21 days" flag | O3 |
| **P2** | Energy dispatch | Forecasts demand and **optimizes when to run energy-hungry steps** (price + carbon) | O1, O2 |
| **P3** | Quality optimization | **Statistical process control** + models to raise high-grade yield | O4 |
| **P4** | Knowledge capture | **GenAI assistant** that captures & serves expert know-how (grounded, cited) | O4 enabler |

> 🇫🇷 **FR :**
> | Pilier | Nom | Ce qu'il fait | Sert |
> |--------|-----|---------------|------|
> | **P1** | Maintenance prédictive | Prédit la **durée de vie résiduelle** du revêtement et un indicateur « défaillance sous 21 jours » | O3 |
> | **P2** | Pilotage énergétique | Prévoit la demande et **optimise le moment de lancer les étapes énergivores** (prix + carbone) | O1, O2 |
> | **P3** | Optimisation qualité | **Maîtrise statistique des procédés** + modèles pour augmenter le rendement haut de gamme | O4 |
> | **P4** | Capture du savoir | **Assistant d'IA générative** qui capte et restitue le savoir-faire (sourcé, cité) | Levier O4 |

> **Vocabulary — RUL (Remaining Useful Life):** the estimated time before a component (here
> the furnace lining) must be replaced. Details in [06-ai-workloads.md](06-ai-workloads.md).
>
> 🇫🇷 **FR — DVR (Durée de Vie Résiduelle) :** le temps estimé avant qu'un composant (ici le
> revêtement du four) doive être remplacé. Détails dans [06-ai-workloads.md](06-ai-workloads.md).

---

## 1.5 What "POC" means here / Ce que « POC » signifie ici

A **Proof of Concept** proves the idea works on **real data at one pilot line** before a
four-country rollout. The POC's job is to **de-risk** the program and justify the investment.

> 🇫🇷 **FR :** Une **preuve de concept** démontre que l'idée fonctionne sur **des données
> réelles, sur une ligne pilote** avant un déploiement dans quatre pays. Le rôle du POC est de
> **réduire les risques** du programme et de justifier l'investissement.

In this POC, real plant sensors are replaced by a **synthetic telemetry simulator** (a
program that emits realistic furnace sensor readings). Crucially, every synthetic reading is
**tagged as synthetic** end-to-end, so it can **never be mistaken for real plant data** — a
strict project rule (Principle IX, see [07-governance-security.md](07-governance-security.md)).

> 🇫🇷 **FR :** Dans ce POC, les vrais capteurs de l'usine sont remplacés par un **simulateur
> de télémétrie synthétique** (un programme qui émet des relevés de capteurs de four
> réalistes). Point crucial : chaque relevé synthétique est **étiqueté comme synthétique** de
> bout en bout, afin de ne **jamais** être confondu avec des données réelles — une règle
> stricte du projet (Principe IX, voir [07-governance-security.md](07-governance-security.md)).

---

## 1.6 Business value (why it pays) / Valeur métier (pourquoi c'est rentable)

The financial case rests mainly on **avoided €8M furnace failures**, plus energy/CO₂ savings
and higher premium yield. The full model lives in the proposal's cost/ROI document
([`First_Proposal/05-cost-estimate.md`](../First_Proposal/05-cost-estimate.md)).

> 🇫🇷 **FR :** Le dossier financier repose surtout sur les **défaillances de four à 8 M€
> évitées**, plus les économies d'énergie/CO₂ et un rendement premium supérieur. Le modèle
> complet se trouve dans le document coût/ROI de la proposition
> ([`First_Proposal/05-cost-estimate.md`](../First_Proposal/05-cost-estimate.md)).

**Next:** [02 — Architecture & data flow »](02-architecture-and-dataflow.md)

> 🇫🇷 **FR : Suite :** [02 — Architecture et flux de données »](02-architecture-and-dataflow.md)
