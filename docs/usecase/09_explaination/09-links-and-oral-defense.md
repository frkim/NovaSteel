# 09 — Links & Oral-Defense Preparation

Everything you need on hand for the defense: **live links**, **repository documents**, official
**learning resources**, and a **Q&A bank** with concise, defensible answers.

> 🇫🇷 **FR :** Tout ce qu'il faut sous la main pour la soutenance : **liens en direct**,
> **documents du dépôt**, **ressources d'apprentissage** officielles, et une **banque de
> questions/réponses** avec des réponses concises et défendables.

---

## 9.1 Live environment links / Liens de l'environnement en direct

| What | Link / Value |
|------|--------------|
| **Simulator + sensor chart (web UI)** | `https://sim-novastee-dev-ox26fi.thankfulbay-9247ccde.swedencentral.azurecontainerapps.io` |
| **Fabric workspace `novasteel-dev`** | `https://app.fabric.microsoft.com/groups/9a005c2a-169c-4cd7-af65-7f097bd0c5b8/list?ctid=9d94eb6e-d45e-4f05-bc1b-d0bbd2421561` |
| Azure resource group | `rg-novasteel-dev` (subscription *Contoso Fx*, `3377065c-bf76-4767-a982-32bce4ffb592`) |
| Tenant id (`ctid`) | `9d94eb6e-d45e-4f05-bc1b-d0bbd2421561` |
| Fabric capacity | `fabnovasteedevox26fi` (Sweden Central) |

> 🇫🇷 **FR :** Toujours conserver le paramètre **`?ctid=…`** sur les URL Fabric/Power BI si vous
> êtes un utilisateur invité, sinon le portail s'ouvre dans le mauvais tenant. La capacité est
> mise en pause chaque nuit à 02:00 — **réactivez-la** avant une démonstration.

> ⚠️ **Before a demo:** the Fabric capacity auto-pauses at **02:00**. **Resume it** (simulator
> Settings page, `az`, or Fabric admin) so notebooks and Power BI work.
>
> 🇫🇷 **FR — ⚠️ Avant une démo :** la capacité Fabric se met en pause à **02:00**. **Réactivez-la**
> (page Paramètres du simulateur, `az`, ou admin Fabric) pour que les notebooks et Power BI
> fonctionnent.

---

## 9.2 Key repository documents / Documents clés du dépôt

| Topic | Path |
|-------|------|
| Executive summary | [`../First_Proposal/00-executive-summary.md`](../First_Proposal/00-executive-summary.md) |
| Project charter | [`../First_Proposal/01-project-charter.md`](../First_Proposal/01-project-charter.md) |
| Solution architecture | [`../First_Proposal/02-solution-architecture.md`](../First_Proposal/02-solution-architecture.md) |
| **Fabric + IoT architecture (7 layers)** | [`../First_Proposal/02a-fabric-iot-architecture.md`](../First_Proposal/02a-fabric-iot-architecture.md) |
| Data & AI design | [`../First_Proposal/03-data-and-ai-design.md`](../First_Proposal/03-data-and-ai-design.md) |
| Implementation plan | [`../First_Proposal/04-implementation-plan.md`](../First_Proposal/04-implementation-plan.md) |
| Cost estimate & ROI | [`../First_Proposal/05-cost-estimate.md`](../First_Proposal/05-cost-estimate.md) |
| Security & compliance | [`../First_Proposal/06-security-compliance.md`](../First_Proposal/06-security-compliance.md) |
| Presentation deck | [`../First_Proposal/07-presentation-deck.md`](../First_Proposal/07-presentation-deck.md) |
| Demo script | [`../First_Proposal/08-demo-script.md`](../First_Proposal/08-demo-script.md) |
| Glossary (proposal) | [`../First_Proposal/11-glossary.md`](../First_Proposal/11-glossary.md) |
| **Constitution (principles)** | [`../0_specs/NovaSteel/.specify/memory/constitution.md`](../0_specs/NovaSteel/.specify/memory/constitution.md) |
| Principles explained | [`../../technical/architecture-principles.md`](../../technical/architecture-principles.md) |
| Platform (ingestion/medallion) | [`../../../platform/README.md`](../../../platform/README.md) |
| Infrastructure (Bicep) | [`../../../infrastructure/README.md`](../../../infrastructure/README.md) |
| Oral-defense rating grid | [`../10_oral_defense/rating_grid.md`](../10_oral_defense/rating_grid.md) |

> 🇫🇷 **FR :** Les documents ci-dessus sont la source de vérité ; ce guide (dossier 09) est une
> explication pédagogique qui s'appuie sur eux.

---

## 9.3 Official learning resources / Ressources d'apprentissage officielles

To learn Fabric from Microsoft directly (start here if a concept is unclear):

> 🇫🇷 **FR :** Pour apprendre Fabric directement chez Microsoft (commencez ici si un concept est
> flou) :

- Microsoft Fabric documentation — `https://learn.microsoft.com/fabric/`
- OneLake — `https://learn.microsoft.com/fabric/onelake/`
- Real-Time Intelligence (Eventhouse/KQL) — `https://learn.microsoft.com/fabric/real-time-intelligence/`
- Data Engineering (Lakehouse/Spark) — `https://learn.microsoft.com/fabric/data-engineering/`
- Data Science (MLflow) — `https://learn.microsoft.com/fabric/data-science/`
- Direct Lake (Power BI) — `https://learn.microsoft.com/fabric/fundamentals/direct-lake-overview`
- KQL — `https://learn.microsoft.com/kusto/query/`
- Microsoft Foundry — `https://learn.microsoft.com/azure/ai-foundry/`
- Azure IoT Hub — `https://learn.microsoft.com/azure/iot-hub/`
- Well-Architected Framework — `https://learn.microsoft.com/azure/well-architected/`

> 🇫🇷 **FR :** Ces liens pointent vers la documentation officielle Microsoft (en anglais par
> défaut ; la plupart des pages proposent un sélecteur de langue en haut à droite).

---

## 9.4 Oral-defense Q&A bank / Banque de questions-réponses

Short, defensible answers. Each is expanded in the referenced file.

> 🇫🇷 **FR :** Réponses courtes et défendables. Chacune est développée dans le fichier
> référencé.

**Q1. What is the project in one sentence?**
An AI decision-support platform on Microsoft Fabric + Foundry that helps NovaSteel predict
furnace failures, cut energy/CO₂, improve quality, and capture expertise across four EU sites.
🇫🇷 *Une plateforme d'aide à la décision par IA sur Microsoft Fabric + Foundry qui aide NovaSteel
à prévoir les défaillances de fours, réduire énergie/CO₂, améliorer la qualité et capturer
l'expertise sur quatre sites de l'UE.* (see [01](01-project-and-objectives.md))

**Q2. Why Microsoft Fabric and not many separate services?**
One SaaS data plane on OneLake — one copy of data, many engines (hot/warm/cold) — minimizes
cost, governance surface, and lineage fragmentation (Principle V).
🇫🇷 *Un seul plan de données SaaS sur OneLake — une copie, plusieurs moteurs — minimise le coût,
la surface de gouvernance et la fragmentation de la traçabilité (Principe V).* (see [04](04-fabric-fundamentals.md))

**Q3. How does data get from a sensor to a prediction?**
Sensor → IoT Hub → Eventstream → Eventhouse (KQL) → mirrored to OneLake → lakehouse shortcut →
Bronze→Silver→Gold notebooks → ML model/scoring → Power BI, with a human approving.
🇫🇷 *Capteur → IoT Hub → Eventstream → Eventhouse (KQL) → miroir OneLake → raccourci lakehouse →
notebooks Bronze→Argent→Or → modèle ML/scoring → Power BI, avec validation humaine.* (see [05 §5.9](05-fabric-components-deployed.md#59-how-they-all-connect--comment-tout-se-connecte))

**Q4. What's the difference between the Eventhouse and the Lakehouse?**
Eventhouse (KQL) = fast **time-series/streaming** store (hot path). Lakehouse = **batch/analytical**
Delta tables (medallion, warm/cold). A shortcut bridges KQL data into the lakehouse.
🇫🇷 *Eventhouse (KQL) = magasin **séries temporelles/flux** rapide (chemin chaud). Lakehouse =
tables Delta **analytiques/par lots** (médaillon). Un raccourci relie les données KQL au
lakehouse.* (see [04 §4.3](04-fabric-fundamentals.md), [05](05-fabric-components-deployed.md))

**Q5. How do you guarantee synthetic demo data is never mistaken for real?**
Every reading carries `origin=Synthetic` end-to-end; synthetic is bucketed separately and never
counted in a real KPI; a passing pytest gate enforces it (Principle IX).
🇫🇷 *Chaque relevé porte `origin=Synthetic` de bout en bout ; le synthétique est isolé et jamais
compté dans un KPI réel ; un test pytest qui passe l'impose (Principe IX).* (see [07](07-governance-security.md))

**Q6. How is safety guaranteed — can the AI control the furnace?**
No. Data flows one-way out of OT; there is no command path back (Principle IV). The AI only
proposes; a human approves (Principle I).
🇫🇷 *Non. Les données sortent de l'OT à sens unique ; aucun chemin de commande en retour
(Principe IV). L'IA ne fait que proposer ; un humain approuve (Principe I).* (see [02 §2.3](02-architecture-and-dataflow.md), [07](07-governance-security.md))

**Q7. Where does machine learning run, and why not Azure ML?**
Inside Fabric Data Science (MLflow experiments + model registry), to keep one governed stack;
Azure ML is intentionally excluded (Principle V).
🇫🇷 *Dans Fabric Data Science (expériences MLflow + registre de modèles), pour garder une pile
gouvernée unique ; Azure ML est exclu volontairement (Principe V).* (see [05 §5.6](05-fabric-components-deployed.md), [06](06-ai-workloads.md))

**Q8. How do you respect EU data residency?**
EU regions (Sweden Central / West Europe / Germany West Central / France Central) are the enforced
default via Azure Policy; IoT Hub moved to West Europe since it's unavailable in Sweden Central. A
non-EU region is used only as a documented, minimized last resort when no EU region supports a
required service (Principle III, EU-default with governed exceptions).
🇫🇷 *Les régions UE (Suède Centre / Europe de l'Ouest / Allemagne Centre-Ouest / France Centre) sont
la valeur par défaut imposée par Azure Policy ; IoT Hub est en Europe de l'Ouest car indisponible en
Suède Centre. Une région hors UE n'est utilisée qu'en dernier recours documenté et minimisé si aucune
région UE ne prend en charge un service requis (Principe III).* (see [03](03-azure-infrastructure.md), [07](07-governance-security.md))

**Q9. How do you control cost?**
The Fabric capacity is the main cost; a Logic App pauses it nightly at 02:00; Spark batch bumps
to F4 only for the run window then drops back.
🇫🇷 *La capacité Fabric est le coût principal ; une Logic App la met en pause à 02:00 ; le batch
Spark passe à F4 uniquement pendant la fenêtre puis rabaisse.* (see [03 §3.4](03-azure-infrastructure.md))

**Q10. What did the POC actually prove?**
Live: simulator → IoT Hub → Eventstream → Eventhouse (~7,000 rows/3 min), medallion runs green,
and P1 produces a `LiningFailureRisk` with `timeToFailureDays ≥ 21` (O3). P2/P3 exceed targets
on reference scenarios.
🇫🇷 *En direct : simulateur → IoT Hub → Eventstream → Eventhouse (~7 000 lignes/3 min), le
médaillon s'exécute correctement, et P1 produit un `LiningFailureRisk` avec `timeToFailureDays
≥ 21` (O3). P2/P3 dépassent les cibles sur les scénarios de référence.* (see [05](05-fabric-components-deployed.md), [06](06-ai-workloads.md))

**Q11. What are the three permission systems and why does it matter?**
Entra directory roles (identity), Azure RBAC (resources), Fabric workspace roles (Fabric items).
Being Azure Owner/Global Admin does not grant workspace access.
🇫🇷 *Rôles d'annuaire Entra (identité), Azure RBAC (ressources), rôles d'espace de travail Fabric
(éléments Fabric). Être Propriétaire Azure/Admin global ne donne pas accès au workspace.* (see [07 §7.5](07-governance-security.md))

**Q12. How does the GenAI assistant avoid making things up?**
It is grounded via Foundry IQ (RAG) with citations, declines when no source exists, and passes
Azure AI Content Safety (Principle VI).
🇫🇷 *Il est ancré via Foundry IQ (RAG) avec citations, refuse quand aucune source n'existe, et
passe Azure AI Content Safety (Principe VI).* (see [06 §6.4](06-ai-workloads.md))

---

## 9.5 The numbers to memorize / Les chiffres à mémoriser

- **−14 %** energy · **−22 %** CO₂ · **≥21-day** furnace warning · **+8 %** high-grade yield.
- **~€8M** per averted furnace failure.
- Reference results: P2 **17.3 %** energy / **51.8 %** CO₂; P3 yield **0.65 → 0.95**.
- **4** plants · **4** pillars · **1** OneLake data plane.

> 🇫🇷 **FR :**
> - **−14 %** énergie · **−22 %** CO₂ · alerte four **≥21 jours** · **+8 %** rendement premium.
> - **~8 M€** par défaillance de four évitée.
> - Résultats de référence : P2 **17,3 %** énergie / **51,8 %** CO₂ ; P3 rendement **0,65 → 0,95**.
> - **4** usines · **4** piliers · **1** plan de données OneLake.

---

## 9.6 Final tips / Derniers conseils

- Tell the **story of one data point** (a temperature reading) travelling the whole pipeline —
  it demonstrates you understand the architecture end-to-end.
- Anchor every technical choice to a **principle** and an **objective**.
- If asked something you don't know, say what you'd check (a doc in §9.2) — honesty beats
  fabrication (that's literally Principle VI!).

> 🇫🇷 **FR :**
> - Racontez **l'histoire d'un point de donnée** (un relevé de température) qui parcourt toute la
>   chaîne — cela prouve que vous comprenez l'architecture de bout en bout.
> - Rattachez chaque choix technique à un **principe** et à un **objectif**.
> - Si l'on vous pose une question dont vous ignorez la réponse, dites ce que vous iriez vérifier
>   (un document du §9.2) — l'honnêteté vaut mieux que l'invention (c'est justement le Principe
>   VI !).

**Back to:** [00 — Index](00-index.md)

> 🇫🇷 **FR : Retour :** [00 — Index](00-index.md)
