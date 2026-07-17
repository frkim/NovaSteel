using './main.bicep'

// EU data residency: swedencentral (primary), westeurope or germanywestcentral.
param location = 'swedencentral'
param namePrefix = 'novasteel'
param environmentName = 'dev'

// Microsoft Defender for Cloud plans across the subscription.
// Already applied (CloudPosture/Storage/KeyVaults/Containers/AppServices/Arm/VirtualMachines = Standard);
// disabled here to avoid transient "another update in progress" conflicts on re-apply (plans are retained).
param enableDefenderForCloud = false

// Microsoft Fabric capacity. Right-size in a design workshop (F2..F128).
param fabricSkuName = 'F8'

// REQUIRED: Fabric capacity admins — Entra UPN(s) or service principal object ID(s).
// Using a dedicated service-principal object ID: Fabric capacity admin validation
// rejects guest (#EXT#) user UPNs/object IDs, so an SP is used as the capacity admin.
param fabricAdminMembers = [
  'dd0e874e-c9d8-494f-b7ac-3a182952e628'
]

// Microsoft Purview (set to false if Purview is unavailable in your region/tenant).
// Disabled: this subscription's SecurityControl tag policy blocks Purview's managed
// side-resources (error 21010). Re-enable with a policy exemption for the Purview managed RG.
param deployPurview = false

// Simulator Container App already deployed & healthy; skip re-provisioning to avoid ACA update lag.
// Set true (with a real image via CI) for a fresh environment.
param deploySimulator = false

// Azure SQL audit/app-state store (research.md R7). Opt-in: set deployAppState = true
// and provide the Entra admin object ID (Entra-only auth; no SQL logins).
param deployAppState = false
// param sqlAadAdminObjectId = '00000000-0000-0000-0000-000000000000'
// param sqlAadAdminLogin = 'novasteel-sql-admins'
// param sqlAadAdminPrincipalType = 'Group'

param tags = {
  costCenter: 'manufacturing-it'
  owner: 'platform-team'
}
