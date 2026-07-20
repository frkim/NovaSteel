# NovaSteel "Project Ignition" — Explained (Learning Guide)

Welcome. This folder is a **from-scratch explanation** of the NovaSteel Proof-of-Concept
(POC): what it does, why, how it is built, and — in depth — **how every Microsoft Fabric
component works**. It is written for someone **new to Microsoft Fabric** who needs to
understand the whole project before an **oral defense**.

> 🇫🇷 **FR :** Bienvenue. Ce dossier est une **explication depuis zéro** de la preuve de
> concept (POC) NovaSteel : ce qu'elle fait, pourquoi, comment elle est construite, et — en
> détail — **comment fonctionne chaque composant Microsoft Fabric**. Il est écrit pour une
> personne **débutante sur Microsoft Fabric** qui doit comprendre l'ensemble du projet avant
> une **soutenance orale**.

Every paragraph is followed by its **French translation** (marked 🇫🇷 **FR :**). Industry
and technical terms are collected in the **[Glossary](08-glossary.md)** with French
equivalents.

> 🇫🇷 **FR :** Chaque paragraphe est suivi de sa **traduction française** (indiquée 🇫🇷
> **FR :**). Les termes métier et techniques sont regroupés dans le **[Glossaire](08-glossary.md)**
> avec leurs équivalents français.

---

## How to read this guide / Comment lire ce guide

Read the files in order. Each builds on the previous one, moving from *business* → *big
picture* → *infrastructure* → *Fabric deep-dive* → *AI* → *governance*.

> 🇫🇷 **FR :** Lisez les fichiers dans l'ordre. Chacun s'appuie sur le précédent, en allant du
> *métier* → *vue d'ensemble* → *infrastructure* → *plongée dans Fabric* → *IA* → *gouvernance*.

| # | File | What you will learn | 🇫🇷 Ce que vous apprendrez |
|---|------|---------------------|----------------------------|
| 00 | [00-index.md](00-index.md) | This page — map of the guide | Cette page — plan du guide |
| 01 | [01-project-and-objectives.md](01-project-and-objectives.md) | The business problem, the 4 objectives, POC scope | Le problème métier, les 4 objectifs, le périmètre du POC |
| 02 | [02-architecture-and-dataflow.md](02-architecture-and-dataflow.md) | End-to-end architecture; hot/warm/cold paths; OT→IT | L'architecture de bout en bout ; chemins chaud/tiède/froid ; OT→IT |
| 03 | [03-azure-infrastructure.md](03-azure-infrastructure.md) | Every Azure resource deployed and its role | Chaque ressource Azure déployée et son rôle |
| 04 | [04-fabric-fundamentals.md](04-fabric-fundamentals.md) | Fabric basics: SaaS, capacity, workspace, OneLake, medallion | Les bases de Fabric : SaaS, capacité, espace de travail, OneLake, médaillon |
| 05 | [05-fabric-components-deployed.md](05-fabric-components-deployed.md) | **Deep dive** on each deployed Fabric item | **Plongée détaillée** dans chaque élément Fabric déployé |
| 06 | [06-ai-workloads.md](06-ai-workloads.md) | The 4 AI pillars (maintenance, energy, quality, knowledge) | Les 4 piliers IA (maintenance, énergie, qualité, savoir) |
| 07 | [07-governance-security.md](07-governance-security.md) | The 10 principles, EU AI Act, GDPR, security | Les 10 principes, l'AI Act européen, le RGPD, la sécurité |
| 08 | [08-glossary.md](08-glossary.md) | EN→FR glossary of steel + tech + acronyms | Glossaire EN→FR acier + technique + acronymes |
| 09 | [09-links-and-oral-defense.md](09-links-and-oral-defense.md) | All links + likely defense questions & answers | Tous les liens + questions/réponses probables de soutenance |

---

## The 30-second summary / Le résumé en 30 secondes

NovaSteel is a fictional European steelmaker. **Project Ignition** is an **AI-powered
production-optimization platform** that helps NovaSteel **predict furnace failures, cut
energy and CO₂, improve steel quality, and capture expert knowledge** — across four EU
plants. It is **decision-support only**: the AI *advises*, humans *decide*. It is built on
**Microsoft Fabric** (the data + machine-learning platform) and **Microsoft Foundry** (the
generative-AI platform), fed by **Azure IoT Hub** for live sensor data.

> 🇫🇷 **FR :** NovaSteel est un sidérurgiste européen fictif. **Project Ignition** est une
> **plateforme d'optimisation de la production dopée à l'IA** qui aide NovaSteel à **prévoir
> les défaillances de fours, réduire l'énergie et le CO₂, améliorer la qualité de l'acier et
> capturer le savoir des experts** — sur quatre usines de l'UE. C'est une **aide à la décision
> uniquement** : l'IA *conseille*, les humains *décident*. Elle repose sur **Microsoft Fabric**
> (la plateforme de données + apprentissage automatique) et **Microsoft Foundry** (la
> plateforme d'IA générative), alimentée par **Azure IoT Hub** pour les données capteurs en
> temps réel.

**POC status:** the platform is deployed live in Azure (resource group `rg-novasteel-dev`,
Sweden Central) with a working Fabric workspace (`novasteel-dev`), a running telemetry
**simulator**, and the first AI pillar (predictive maintenance) producing predictions on
live data.

> 🇫🇷 **FR :** **État du POC :** la plateforme est déployée en réel sur Azure (groupe de
> ressources `rg-novasteel-dev`, Suède Centre) avec un espace de travail Fabric fonctionnel
> (`novasteel-dev`), un **simulateur** de télémétrie en marche, et le premier pilier IA
> (maintenance prédictive) qui produit des prédictions sur des données en direct.

---

## Key facts you can quote / Faits clés à citer

- **4 objectives:** −14 % energy, −22 % CO₂, ≥21-day furnace-failure warning, +8 % quality yield.
- **4 pillars:** P1 predictive maintenance → P2 energy dispatch → P3 quality → P4 knowledge capture.
- **1 data plane:** Microsoft Fabric + OneLake (one copy of data, many engines).
- **Non-negotiable:** human-in-the-loop, EU data residency (EU-default with governed exceptions), one-way OT→IT, full traceability.

> 🇫🇷 **FR :**
> - **4 objectifs :** −14 % d'énergie, −22 % de CO₂, alerte de défaillance de four ≥21 jours,
>   +8 % de rendement qualité.
> - **4 piliers :** P1 maintenance prédictive → P2 pilotage énergétique → P3 qualité →
>   P4 capture du savoir.
> - **1 plan de données :** Microsoft Fabric + OneLake (une seule copie des données,
>   plusieurs moteurs).
> - **Non négociable :** humain dans la boucle, résidence des données dans l'UE, flux
>   unidirectionnel OT→IT, traçabilité complète.
