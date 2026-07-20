# EU Data Residency — Documented Exceptions Register

Constitution **Principle III v2.0.0** ("EU-Default with Governed Exceptions") makes EU regions
the enforced default and permits a non-EU region **only as a documented, minimized, labelled,
time-bounded last resort** when a required service is unavailable in every EU region. Every
such deviation is recorded here.

> Enforcement: the `novasteel-eu-locations` and `novasteel-eu-rg-locations` Azure Policy
> assignments keep EU the default. An exception is implemented as a **minimal `notScopes`
> entry** (or policy exemption) covering only the exception's resource group(s), plus a
> `dataResidency` tag on the affected resources.

---

## EX-001 — Microsoft Purview (data governance / catalog)

| Field | Value |
| --- | --- |
| **Status** | Active |
| **Date** | 2026-07-20 |
| **Service** | Microsoft Purview account (`Microsoft.Purview/accounts`), tenant-level "new" Purview |
| **Resource** | `pview-novastee-dev-ox26fi` in RG `rg-novasteel-governance`; managed RG `managed-rg-pview-novastee-dev-ox26fi` |
| **Region used** | `eastus` (non-EU) |
| **EU regions checked** | swedencentral, westeurope, germanywestcentral, francecentral, northeurope — **all rejected** |
| **Why no EU region** | Purview's **tenant service locations are US-only** for tenant `9d94eb6e-d45e-4f05-bc1b-d0bbd2421561` (`eastus, eastus2, southcentralus, westcentralus, westus, westus2, westus3`). Verified live: EU-region deployment fails preflight with *"service location could not be found in the list of service locations for the tenant."* |
| **Exception mechanism** | `notScopes` on `novasteel-eu-locations` and `novasteel-eu-rg-locations` limited to the two RG paths above (nothing else on the subscription is exempt). |
| **Residency label** | Resources tagged `dataResidency=us-exception`. |
| **Minimization** | Only the Purview account + its RP-managed RG are non-EU. Purview holds **catalog metadata / lineage / classifications**; scan **sample ingestion** should be kept off / minimized so no personal or sensitive plant data egresses. The governed **data itself** (OneLake / Fabric / telemetry / audit) remains **EU-resident**. |
| **Managed-resource protection** | The Purview managed RG carries a **system deny-assignment** that blocks all principals (including internal tag-based automation) from modifying its resources, so they are protected independent of the `SecurityControl` tag. |
| **Revisit trigger** | Replace with an EU-homed Purview as soon as Microsoft enables an **EU Purview service location** for the tenant (raise a tenant/Microsoft request). Re-check quarterly. |

### Deployment note (how it was created)
Because the internal `Add SecurityControl=Ignore` **Modify** tag policy (assignment
`5f73e260853e4a11a4acaecd`) is evaluated at subscription scope for Purview's not-yet-existent
managed RG, and Purview's RP preflight rejects any Modify policy on its managed resources,
`exemption` / `DoNotEnforce` / `notScopes` cannot clear it. Deployment therefore required
**temporarily setting that tag policy definition's effect to `disabled`** during creation, then
**restoring it to `modify`** immediately afterward (verified restored). Existing resources kept
their tags throughout; only Purview was created in the window, and its managed resources are
covered by the managed-RG deny-assignment.
