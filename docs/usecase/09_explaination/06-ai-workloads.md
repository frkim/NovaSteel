# 06 — The AI Workloads (The Four Pillars)

Each pillar solves one problem and serves one or more objectives. All four share the same
iron rule: **the AI proposes, a human decides** (Principle I), and every decision is **audited**
(Principle II).

> 🇫🇷 **FR :** Chaque pilier résout un problème et sert un ou plusieurs objectifs. Les quatre
> partagent la même règle d'or : **l'IA propose, un humain décide** (Principe I), et chaque
> décision est **auditée** (Principe II).

> **Vocabulary — "decision-support only":** the system gives advice; it never acts on the
> plant by itself. Every recommendation is emitted as **`Proposed`** and waits for a human to
> **Approve / Adjust / Reject**.
>
> 🇫🇷 **FR — « aide à la décision uniquement » :** le système donne un avis ; il n'agit jamais
> sur l'usine de lui-même. Chaque recommandation est émise en **`Proposed`** (proposée) et
> attend qu'un humain **Approuve / Ajuste / Rejette**.

---

## 6.1 P1 — Predictive Maintenance (furnace-lining RUL) → O3

**The problem.** A blast-furnace lining wears out. If it fails unexpectedly, it costs ~€8M.

> 🇫🇷 **FR : Le problème.** Le revêtement d'un haut-fourneau s'use. S'il lâche à l'improviste,
> cela coûte ~8 M€.

**How it works.** The workload is **physics-informed**: from the telemetry it extracts
**heat-flux wear features** (thermal signals that reveal lining erosion), then **extrapolates**
the **Remaining Useful Life (RUL)** toward the failure threshold. It raises a
`Prediction(kind=LiningFailureRisk)` **only when degradation is actionable** — avoiding false
alarms. Proven live with a **`timeToFailureDays ≥ 21`** warning (objective O3).

> 🇫🇷 **FR : Comment ça marche.** La charge est **guidée par la physique** : à partir de la
> télémétrie, elle extrait des **variables d'usure de flux thermique** (signaux thermiques qui
> révèlent l'érosion du revêtement), puis **extrapole** la **durée de vie résiduelle (DVR)**
> vers le seuil de défaillance. Elle lève une prédiction `LiningFailureRisk` **seulement quand
> la dégradation est actionnable** — évitant les fausses alertes. Démontré en direct avec une
> alerte **`timeToFailureDays ≥ 21`** (objectif O3).

**Human-in-the-loop.** Maintenance decisions **propose a work-order id** but **never actuate**
equipment. Every prediction carries **evidence, confidence, and model version** (Principle VI).

> 🇫🇷 **FR : Humain dans la boucle.** Les décisions de maintenance **proposent un numéro d'ordre
> de travail** mais **n'actionnent jamais** l'équipement. Chaque prédiction porte des
> **preuves, une confiance et une version de modèle** (Principe VI).

> **Vocabulary — Physics-informed model:** a model whose features/logic are grounded in known
> physics (heat flux, thermal gradients), not a pure black box — more trustworthy and
> explainable.
>
> 🇫🇷 **FR — Modèle guidé par la physique :** un modèle dont les variables/la logique reposent
> sur une physique connue (flux thermique, gradients), pas une boîte noire — plus fiable et
> explicable.

---

## 6.2 P2 — Energy Dispatch Optimization → O1 & O2

**The problem.** Running energy-hungry furnace steps at the wrong time wastes money (peak
electricity prices) and emits more CO₂ (dirtier grid).

> 🇫🇷 **FR : Le problème.** Lancer les étapes énergivores du four au mauvais moment gaspille de
> l'argent (prix de pointe de l'électricité) et émet plus de CO₂ (réseau plus « sale »).

**How it works.** It **shifts and batches** flexible furnace "heats" into the **cheapest,
lowest-carbon** time slots **before their deadlines**. It compares a **baseline** (run each
heat on arrival) against an **optimized** plan (one batched campaign in the greenest feasible
window). On the reference scenario it achieves **17.3 % energy** and **51.8 % CO₂** reduction
— above the O1 (−14 %) / O2 (−22 %) targets.

> 🇫🇷 **FR : Comment ça marche.** Il **décale et regroupe** les coulées flexibles du four dans
> les créneaux **les moins chers et les moins carbonés**, **avant leurs échéances**. Il compare
> une **référence** (chaque coulée dès son arrivée) à un plan **optimisé** (une campagne
> regroupée dans la fenêtre la plus verte possible). Sur le scénario de référence, il atteint
> **17,3 % d'énergie** et **51,8 % de CO₂** en moins — au-dessus des cibles O1 (−14 %) / O2
> (−22 %).

**Where it runs.** The heavy optimization math runs **outside Fabric**, as an **Azure
Functions / Container Apps** service (`energy-dispatch`). By default it uses a **heuristic**
solver; a **MILP** (mathematical optimization) refinement can replace it without changing the
data contract. It reads Fabric Gold tables (`gold_energy_jobs`, `gold_market_signals`) and
writes `p2_energy_plans`.

> 🇫🇷 **FR : Où il s'exécute.** Le calcul lourd d'optimisation s'exécute **hors de Fabric**, en
> service **Azure Functions / Container Apps** (`energy-dispatch`). Par défaut il utilise un
> solveur **heuristique** ; un raffinement **MILP** (optimisation mathématique) peut le
> remplacer sans changer le contrat de données. Il lit les tables Gold de Fabric
> (`gold_energy_jobs`, `gold_market_signals`) et écrit `p2_energy_plans`.

**Safety.** Never starts a heat before its charge is ready or after its deadline; infeasible
batches are **flagged** (`deadline_breaches`), never silently dropped or forced. Plans stay
**`Proposed`** for an energy manager, producing an **EU-ETS audit trail**.

> 🇫🇷 **FR : Sécurité.** Ne démarre jamais une coulée avant que sa charge soit prête ni après
> son échéance ; les lots infaisables sont **signalés** (`deadline_breaches`), jamais
> supprimés en silence ni forcés. Les plans restent **`Proposed`** pour un responsable énergie,
> produisant une **piste d'audit EU-ETS**.

> **Vocabulary — MILP / Heuristic / Solver:** *MILP* = Mixed-Integer Linear Programming, an
> exact optimization method. A *heuristic* finds a good-enough answer fast. A *solver* is the
> engine that computes the solution. **EU-ETS:** EU Emissions Trading System (carbon market).
>
> 🇫🇷 **FR — MILP / Heuristique / Solveur :** *MILP* = programmation linéaire en nombres
> entiers, une méthode d'optimisation exacte. Une *heuristique* trouve rapidement une solution
> « assez bonne ». Un *solveur* est le moteur qui calcule la solution. **EU-ETS :** système
> d'échange de quotas d'émission de l'UE (marché carbone).

---

## 6.3 P3 — Quality Optimization (prediction + SPC) → O4

**The problem.** Some heats miss premium **automotive-grade (DP800)** quality and get
downgraded, losing margin.

> 🇫🇷 **FR : Le problème.** Certaines coulées ratent la qualité premium **automobile (DP800)**
> et sont déclassées, ce qui érode la marge.

**How it works.** It **predicts the grade outcome** per heat from process features, links
**predicted-vs-actual**, and proposes **reviewable corrective adjustments** for *recoverable*
excursions (e.g. sulphur/inclusion issues that can still be fixed in-run). It also runs
**Statistical Process Control (SPC)** — 3-sigma control charts + Western Electric rules — to
raise **early drift warnings** before the grade band is breached. On the reference batch it
lifts high-grade yield **0.65 → 0.95**.

> 🇫🇷 **FR : Comment ça marche.** Il **prédit le résultat de grade** par coulée à partir des
> variables de procédé, relie **prédit-vs-réel**, et propose des **ajustements correctifs
> révisables** pour les écarts *récupérables* (ex. problèmes de soufre/inclusions corrigeables
> en cours). Il fait aussi de la **maîtrise statistique des procédés (SPC)** — cartes de
> contrôle 3-sigma + règles de Western Electric — pour lever des **alertes de dérive précoces**
> avant que la bande de grade ne soit franchie. Sur le lot de référence, il fait passer le
> rendement haut de gamme de **0,65 à 0,95**.

**Safety.** Non-recoverable excursions are **flagged but get no auto-fix**. A **metallurgist**
reviews and approves; nothing is actuated. Every prediction carries **per-metric evidence and
confidence**.

> 🇫🇷 **FR : Sécurité.** Les écarts non récupérables sont **signalés mais sans correction
> automatique**. Un **métallurgiste** examine et approuve ; rien n'est actionné. Chaque
> prédiction porte des **preuves par métrique et une confiance**.

> **Vocabulary — SPC / Cp-Cpk / DP800:** *SPC* = Statistical Process Control (using control
> charts to detect drift). *Cp/Cpk* = process capability indices (how well a process stays
> within spec). *DP800* = a dual-phase high-strength automotive steel grade.
>
> 🇫🇷 **FR — SPC / Cp-Cpk / DP800 :** *SPC* = maîtrise statistique des procédés (cartes de
> contrôle pour détecter la dérive). *Cp/Cpk* = indices de capabilité du procédé (aptitude à
> rester dans les tolérances). *DP800* = un acier automobile haute résistance « dual-phase ».

---

## 6.4 P4 — Knowledge Capture (GenAI assistant) → O4 enabler

**The problem.** Senior operators' expertise retires with them.

> 🇫🇷 **FR : Le problème.** L'expertise des opérateurs seniors part à la retraite avec eux.

**How it works.** Operator interviews, **SOPs** and shift logs land in a Knowledge lakehouse;
a **generative-AI assistant** (Microsoft **Foundry** + **Foundry IQ** for grounding/RAG)
answers operators' questions in natural language — **grounded with citations**, and it
**declines rather than fabricates** when no source exists. All generative output passes **Azure
AI Content Safety**.

> 🇫🇷 **FR : Comment ça marche.** Les entretiens d'opérateurs, les **modes opératoires (SOP)**
> et journaux de poste atterrissent dans un lakehouse de savoir ; un **assistant d'IA
> générative** (Microsoft **Foundry** + **Foundry IQ** pour l'ancrage/RAG) répond aux questions
> des opérateurs en langage naturel — **sourcé avec citations**, et il **refuse plutôt que
> d'inventer** quand aucune source n'existe. Toute sortie générative passe **Azure AI Content
> Safety**.

**Model choice.** The project prefers **GPT-5-mini** class models over older ones for the
Foundry deployments.

> 🇫🇷 **FR : Choix de modèle.** Le projet privilégie les modèles de classe **GPT-5-mini** aux
> plus anciens pour les déploiements Foundry.

> **Vocabulary — GenAI / RAG / Grounding / SOP:** *GenAI* = generative AI (text-producing
> models). *RAG* = Retrieval-Augmented Generation — the model answers using retrieved documents.
> *Grounding* = anchoring answers to real sources. *SOP* = Standard Operating Procedure.
>
> 🇫🇷 **FR — GenAI / RAG / Ancrage / SOP :** *GenAI* = IA générative (modèles produisant du
> texte). *RAG* = génération augmentée par récupération — le modèle répond à partir de documents
> récupérés. *Ancrage (grounding)* = attacher les réponses à de vraies sources. *SOP* = mode
> opératoire normalisé.

---

## 6.5 The shared pattern (every pillar) / Le schéma commun (chaque pilier)

1. **Read Gold** features from the Lakehouse.
2. **Predict / optimize** (model or solver).
3. **Attach evidence + confidence + model version** (Principle VI).
4. **Emit `Proposed`/`Raised`** — a human Approves/Adjusts/Rejects (Principle I).
5. **Append an immutable `AuditRecord`** (Principle II).
6. **Preserve `origin` (synthetic vs real)** throughout (Principle IX).

> 🇫🇷 **FR :**
> 1. **Lire les variables Gold** depuis le Lakehouse.
> 2. **Prédire / optimiser** (modèle ou solveur).
> 3. **Joindre preuves + confiance + version de modèle** (Principe VI).
> 4. **Émettre `Proposed`/`Raised`** — un humain Approuve/Ajuste/Rejette (Principe I).
> 5. **Ajouter un `AuditRecord` immuable** (Principe II).
> 6. **Préserver `origin` (synthétique vs réel)** tout du long (Principe IX).

> **Vocabulary — Golden fixture:** a frozen reference output used in tests to guarantee the
> model keeps producing the expected result (regression guard). Each pillar has one in
> `libs/fixtures/`.
>
> 🇫🇷 **FR — Fixture « golden » :** une sortie de référence figée, utilisée dans les tests pour
> garantir que le modèle continue de produire le résultat attendu (garde-fou de régression).
> Chaque pilier en possède une dans `libs/fixtures/`.

**Next:** [07 — Governance, security & compliance »](07-governance-security.md)

> 🇫🇷 **FR : Suite :** [07 — Gouvernance, sécurité et conformité »](07-governance-security.md)
