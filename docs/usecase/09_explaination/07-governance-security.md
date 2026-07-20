# 07 — Governance, Security & Compliance

NovaSteel operates in a **regulated, safety-critical** context (GDPR, the EU AI Act, EU
emissions rules). Governance is not an afterthought — it is encoded as **ten principles** (a
"constitution") that every change must respect.

> 🇫🇷 **FR :** NovaSteel évolue dans un contexte **réglementé et critique pour la sécurité**
> (RGPD, AI Act européen, règles européennes sur les émissions). La gouvernance n'est pas
> secondaire — elle est codifiée en **dix principes** (une « constitution ») que chaque
> évolution doit respecter.

> **Vocabulary — Constitution (here):** a project governance document. Principles I–IX are
> **NON-NEGOTIABLE** — breaking one **blocks the merge** of code. Principle X is advisory.
>
> 🇫🇷 **FR — Constitution (ici) :** un document de gouvernance projet. Les principes I–IX sont
> **NON NÉGOCIABLES** — en enfreindre un **bloque la fusion** du code. Le principe X est
> indicatif.

The full explanatory version is in
[`../../technical/architecture-principles.md`](../../technical/architecture-principles.md); the
normative source is the
[Constitution](../0_specs/NovaSteel/.specify/memory/constitution.md).

> 🇫🇷 **FR :** La version explicative complète est dans
> [`../../technical/architecture-principles.md`](../../technical/architecture-principles.md) ;
> la source normative est la
> [Constitution](../0_specs/NovaSteel/.specify/memory/constitution.md).

---

## 7.1 The ten principles, in one line each / Les dix principes, en une ligne

| # | Principle | In one line | 🇫🇷 En une ligne |
|---|-----------|-------------|------------------|
| I | Human-in-the-Loop | AI advises; a human approves; never actuate the plant | L'IA conseille ; un humain approuve ; ne jamais actionner l'usine |
| II | End-to-End Traceability | Immutable audit record + Purview lineage for every decision | Audit immuable + traçabilité Purview pour chaque décision |
| III | EU Data Residency (EU-default, governed exceptions) | EU regions are the enforced default; non-EU only as a documented last resort | Régions UE par défaut (imposées) ; non-UE seulement en dernier recours documenté |
| IV | One-Way OT→IT Boundary | Telemetry flows out only; no command path back to OT | La télémétrie sort seulement ; aucun retour de commande vers l'OT |
| V | Scoped, Unified Stack | Only the approved Fabric+Foundry+PaaS services | Uniquement les services approuvés Fabric+Foundry+PaaS |
| VI | Explainability & Responsible AI | Evidence, confidence, grounded GenAI, Content Safety | Preuves, confiance, GenAI sourcée, Content Safety |
| VII | Role-Based Access & Per-Site Isolation | Least-privilege by persona; no cross-site data bleed | Moindre privilège par persona ; pas de fuite inter-sites |
| VIII | Contract-First, Test-First | Shared contracts + golden fixtures; tests before ship | Contrats partagés + fixtures ; tests avant livraison |
| IX | Synthetic-Data Integrity | Synthetic data marked end-to-end; never shown as real | Données synthétiques marquées ; jamais présentées comme réelles |
| X | Phased Delivery *(advisory)* | Prove value at one site first; keep it simple (YAGNI) | Prouver la valeur sur un site d'abord ; rester simple (YAGNI) |

---

## 7.2 How the principles show up in the build / Comment les principes se traduisent

- **I (Human-in-the-Loop):** every pillar emits `Proposed`/`Raised`; nothing auto-actuates.
- **II (Traceability):** an `AuditLog` appends immutable `AuditRecord`s; lineage in Purview.
- **III (EU residency):** an Azure Policy pins EU regions as the default; IoT Hub moved to West
  Europe (not available in Sweden Central) to stay EU-resident. A non-EU region is allowed only
  as a documented, minimized last resort when no EU region supports a required service.
- **IV (One-way OT→IT):** ingestion is device→cloud only; the Data Pipeline only reads/proposes.
- **V (Scoped stack):** ML lives in Fabric Data Science, RAG in Foundry IQ; Azure ML / AI
  Search are excluded.
- **VI (Explainability):** predictions carry evidence + confidence; GenAI cites or declines,
  and passes Content Safety; stale telemetry is flagged.
- **VII (RBAC / isolation):** access by persona via Entra ID; data scoped per site.
- **VIII (Test-first):** the medallion has a passing `pytest` provenance/data-quality gate.
- **IX (Synthetic integrity):** every reading carries `origin=Synthetic`; the simulator's data
  is never counted in a real KPI.

> 🇫🇷 **FR :**
> - **I (humain dans la boucle) :** chaque pilier émet `Proposed`/`Raised` ; rien ne s'actionne
>   automatiquement.
> - **II (traçabilité) :** un `AuditLog` ajoute des `AuditRecord` immuables ; traçabilité dans
>   Purview.
> - **III (résidence UE) :** une Azure Policy impose les régions UE par défaut ; IoT Hub déplacé en
>   Europe de l'Ouest (indisponible en Suède Centre) pour rester dans l'UE. Une région hors UE
>   n'est autorisée qu'en dernier recours documenté et minimisé, si aucune région UE ne prend en
>   charge un service requis.
> - **IV (unidirectionnel OT→IT) :** ingestion appareil→cloud seulement ; le pipeline lit/propose.
> - **V (pile maîtrisée) :** le ML vit dans Fabric Data Science, le RAG dans Foundry IQ ; Azure
>   ML / AI Search sont exclus.
> - **VI (explicabilité) :** les prédictions portent preuves + confiance ; la GenAI cite ou
>   refuse, et passe Content Safety ; la télémétrie périmée est signalée.
> - **VII (RBAC / isolation) :** accès par persona via Entra ID ; données cloisonnées par site.
> - **VIII (test d'abord) :** le médaillon a un test `pytest` de provenance/qualité qui passe.
> - **IX (intégrité synthétique) :** chaque relevé porte `origin=Synthetic` ; les données du
>   simulateur ne sont jamais comptées dans un KPI réel.

---

## 7.3 Regulations in play / Réglementations concernées

- **GDPR** (General Data Protection Regulation): protects personal data. Audit records are
  **exempt from erasure** (legal-obligation exception) while **raw personal content** (e.g.
  interview recordings) **stays erasable**.
- **EU AI Act:** classifies AI systems by risk. Human oversight (Principle I) + traceability
  (Principle II) + explainability (Principle VI) address **high-risk** obligations.
- **EU-ETS:** the carbon market; energy plans produce an **EU-ETS audit trail** for emissions
  accounting.

> 🇫🇷 **FR :**
> - **RGPD** (Règlement général sur la protection des données) : protège les données
>   personnelles. Les enregistrements d'audit sont **exemptés d'effacement** (obligation légale)
>   tandis que le **contenu personnel brut** (ex. enregistrements d'entretiens) **reste
>   effaçable**.
> - **AI Act européen :** classe les systèmes d'IA par risque. La supervision humaine (Principe
>   I) + la traçabilité (Principe II) + l'explicabilité (Principe VI) répondent aux obligations
>   **haut risque**.
> - **EU-ETS :** le marché carbone ; les plans énergétiques produisent une **piste d'audit
>   EU-ETS** pour la comptabilité des émissions.

---

## 7.4 Security building blocks / Briques de sécurité

- **Entra ID** — identity, single sign-on, conditional access, least-privilege roles.
- **Managed Identities** — services authenticate **without stored passwords** (preferred over
  keys/connection strings throughout).
- **Key Vault** — central, audited store for any secret/key.
- **Purview + OneLake Catalog** — lineage, classification, sensitivity labels, endorsement.
- **Azure Policy** — enforces EU regions as the **default** via **policy-as-code** (fails
  deployment for non-EU unless a documented last-resort exception applies).
- **Monitoring** — Log Analytics + Application Insights + alert rules (model drift, telemetry
  freshness).

> 🇫🇷 **FR :**
> - **Entra ID** — identité, authentification unique, accès conditionnel, rôles au moindre
>   privilège.
> - **Identités managées** — les services s'authentifient **sans mot de passe stocké** (préféré
>   aux clés/chaînes de connexion partout).
> - **Key Vault** — magasin central et audité pour tout secret/clé.
> - **Purview + Catalogue OneLake** — traçabilité, classification, étiquettes de
>   confidentialité, certification.
> - **Azure Policy** — impose les régions UE **par défaut** en **politique-en-tant-que-code**
>   (échec du déploiement hors UE sauf exception documentée de dernier recours).
> - **Supervision** — Log Analytics + Application Insights + règles d'alerte (dérive de modèle,
>   fraîcheur de télémétrie).

---

## 7.5 Access layers you must not confuse / Couches d'accès à ne pas confondre

A recurring gotcha (and a likely defense question): **three separate permission systems**.

> 🇫🇷 **FR :** Un piège récurrent (et une question probable en soutenance) : **trois systèmes
> de permissions distincts**.

| Layer | Controls | Example role |
|-------|----------|--------------|
| **Entra directory role** | The tenant/identity (users, admins) | Global Administrator |
| **Azure RBAC** | Azure resources (subscription, resource group) | Owner, Contributor |
| **Fabric workspace role** | Fabric items in a workspace | Admin, Member, Viewer |

Being an Azure Owner or Global Admin does **not** grant Fabric workspace access — you must be
added to the **workspace** explicitly.

> 🇫🇷 **FR :** Être Propriétaire Azure ou Administrateur global ne donne **pas** accès à
> l'espace de travail Fabric — il faut être ajouté explicitement au **workspace**.
> | Couche | Contrôle | Exemple de rôle |
> |--------|----------|-----------------|
> | **Rôle d'annuaire Entra** | Le tenant/l'identité (utilisateurs, admins) | Administrateur global |
> | **Azure RBAC** | Les ressources Azure (abonnement, groupe) | Propriétaire, Contributeur |
> | **Rôle d'espace de travail Fabric** | Les éléments Fabric d'un workspace | Admin, Membre, Lecteur |

**Next:** [08 — Glossary (EN→FR) »](08-glossary.md)

> 🇫🇷 **FR : Suite :** [08 — Glossaire (EN→FR) »](08-glossary.md)
