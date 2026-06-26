# NovaSteel "Project Ignition" — Azure Infrastructure (Bicep)

Infrastructure-as-Code for the **NovaSteel AI-powered steel production optimization
platform**. It provisions the Azure reference architecture described in
[`../docs/usecase/First_Proposal/02-solution-architecture.md`](../docs/usecase/First_Proposal/02-solution-architecture.md)
and [`02a-fabric-iot-architecture.md`](../docs/usecase/First_Proposal/02a-fabric-iot-architecture.md).

> **Demo configuration.** These templates use **public network access** for all
> services and do **not** deploy private endpoints, Private DNS, or a VNet — to keep
> the demo simple to stand up and reach. For production, re-introduce private
> networking (VNet + Private Endpoints + Private DNS) and set services to
> private/disabled public access.

## Region & data residency

Default region is **Sweden Central** (`swedencentral`) for EU data residency.
`westeurope` and `germanywestcentral` are also allowed. GPT-5 and
`text-embedding-3-large` are available in Sweden Central.

## What gets deployed

| Module | Azure service | Role in the platform |
| ------ | ------------- | -------------------- |
| `monitoring.bicep` | Log Analytics + Application Insights | Observability (Azure Monitor) |
| `identity.bicep` | User-assigned managed identity | Entra ID workload identity |
| `keyvault.bicep` | Key Vault (RBAC) | Secrets / keys |
| `storage.bicep` | Storage (ADLS Gen2) | Medallion data lake (bronze/silver/gold) |
| `container-registry.bicep` | Container Registry | Container images (apps & agents) |
| `iot-hub.bicep` | IoT Hub | Cloud-direct device telemetry ingestion (one-way OT→IT) |
| `event-hubs.bicep` | Event Hubs | Streaming telemetry → Fabric RTI |
| `fabric.bicep` | Microsoft Fabric capacity | OneLake, data engineering, **Data Science (ML)**, RTI, Power BI |
| `foundry.bicep` | Microsoft Foundry (AI Services) + **GPT-5** + embeddings | Knowledge-capture assistant + **Foundry IQ grounding/RAG** |
| `functions.bicep` | Azure Functions (Elastic Premium) | Energy-dispatch optimization agent |
| `container-apps.bicep` | Container Apps | Energy-dispatch microservice + steel factory simulator |
| `purview.bicep` | Microsoft Purview | Governance, lineage, EU AI Act traceability |
| `policy.bicep` | Azure Policy (allowed locations) | EU data-residency guardrail (Constitution III) |
| `app-state.bicep` | Azure SQL (serverless) | Immutable audit records + app/workflow state (opt-in) |
| `defender.bicep` | Microsoft Defender for Cloud | Subscription-wide posture & workload protection |
| `rbac.bicep` | Role assignments | Least-privilege data-plane access wiring |

### AI models

The Microsoft Foundry account deploys, by default:

- **`gpt-5`** (version `2025-08-07`, `GlobalStandard`) — knowledge assistant
  chat/reasoning.
- **`text-embedding-3-large`** — embeddings for vectorized RAG.

Override via the `modelDeployments` parameter of `modules/foundry.bicep`.
GPT-5 may be gated in some tenants/regions — request access in the Microsoft
Foundry portal if a deployment is blocked.

## Not provisioned by this IaC (deployed out-of-band)

Some listed services are not ARM/Bicep resources or are tenant/SaaS-level and are
onboarded separately:

- **Microsoft Entra ID** — tenant identity (represented here via managed
  identities and RBAC).
- **Power BI** — runs on the deployed **Microsoft Fabric** capacity.

## Prerequisites

- Azure CLI with the Bicep CLI (`az bicep upgrade`).
- Permission to create resource groups and assign roles (Owner or
  User Access Administrator + Contributor) on the target subscription.
- Resource providers registered (e.g. `Microsoft.Fabric`, `Microsoft.Purview`,
  `Microsoft.CognitiveServices`, `Microsoft.App`).

## Configure

Edit [`main.bicepparam`](main.bicepparam). At minimum set **`fabricAdminMembers`**
to a real Entra UPN or service principal object ID (required by Fabric capacity).

## Deploy

```bash
# Validate / preview (recommended)
az deployment sub what-if \
  --location swedencentral \
  --template-file main.bicep \
  --parameters main.bicepparam

# Deploy
az deployment sub create \
  --location swedencentral \
  --template-file main.bicep \
  --parameters main.bicepparam
```

The deployment is **subscription-scoped**: it creates the resource group
(`rg-novasteel-dev` by default), enables Defender for Cloud plans, then deploys
the platform resources into the resource group.

## Key parameters

| Parameter | Default | Notes |
| --------- | ------- | ----- |
| `location` | `swedencentral` | `swedencentral` \| `westeurope` \| `germanywestcentral` |
| `namePrefix` | `novasteel` | Resource name prefix |
| `environmentName` | `dev` | Suffix; part of resource names |
| `fabricSkuName` | `F8` | Fabric capacity F-SKU (F2..F128) |
| `fabricAdminMembers` | — | **Required**; Fabric capacity admins |
| `enableDefenderForCloud` | `true` | Defender for Cloud plans |
| `deployPurview` | `true` | Disable if Purview is unavailable in your tenant/region |
| `purviewLocation` | `''` | Optional Purview region override |
| `enforceEuResidencyPolicy` | `true` | Assign Azure Policy allowed-locations (EU residency, Constitution III) |
| `deployAppState` | `false` | Deploy the Azure SQL audit/app-state store; requires `sqlAadAdminObjectId` |
| `sqlAadAdminObjectId` | `''` | Entra admin object ID for the Azure SQL audit store |
| `sqlAadAdminLogin` | `''` | Entra admin display name for the Azure SQL audit store |

## Notes

- API versions target the latest GA (or required preview for AI Foundry projects /
  GPT-5). Run `az bicep upgrade` so the CLI has matching type definitions.
- All figures and SKUs are **reference/demo defaults** — right-size during a
  design workshop (see [`../docs/usecase/First_Proposal/05-cost-estimate.md`](../docs/usecase/First_Proposal/05-cost-estimate.md)).
