using './main.bicep'

// EU data residency: swedencentral (primary), westeurope or germanywestcentral.
param location = 'swedencentral'
param namePrefix = 'novasteel'
param environmentName = 'dev'

// Microsoft Defender for Cloud plans across the subscription.
param enableDefenderForCloud = true

// Microsoft Fabric capacity. Right-size in a design workshop (F2..F128).
param fabricSkuName = 'F8'

// REQUIRED: Fabric capacity admins — replace with real Entra UPN(s) or
// service principal object ID(s) before deploying.
param fabricAdminMembers = [
  'admin@novasteel.example'
]

// Microsoft Purview (set to false if Purview is unavailable in your region/tenant).
param deployPurview = true

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
