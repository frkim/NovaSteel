// Azure Policy: EU data-residency guardrail (subscription scope).
// Constitution III (v2.0.0 — EU-Default with Governed Exceptions): EU regions are the
// enforced DEFAULT for resource deployment. A non-EU region is permitted only as a
// documented, minimized, labelled, time-bounded LAST RESORT when a required service is
// unavailable in every EU region — implemented operationally as a per-case policy
// exemption / notScopes on these assignments (not by widening the default list).
metadata description = 'Assigns built-in Allowed Locations policies so EU regions are the default for all resources and resource groups; non-EU requires a documented last-resort exception (Constitution III v2.0.0).'

targetScope = 'subscription'

@description('Approved EU regions (the enforced default) for all resources and resource groups. Non-EU last-resort deviations are handled via documented per-resource exemptions, not by editing this list.')
param allowedLocations array = [
  'swedencentral'
  'westeurope'
  'germanywestcentral'
  'francecentral'
]

@description('Policy assignment enforcement mode. Use DoNotEnforce to audit-only before turning on enforcement.')
@allowed([
  'Default'
  'DoNotEnforce'
])
param enforcementMode string = 'Default'

// Built-in policy definition IDs
var allowedLocationsResourcesDef = tenantResourceId('Microsoft.Authorization/policyDefinitions', 'e56962a6-4747-49cd-b67b-bf8b01975c4c')
var allowedLocationsResourceGroupsDef = tenantResourceId('Microsoft.Authorization/policyDefinitions', 'e765b5de-1225-4ba3-bd56-1ac6695af988')

resource resourceLocations 'Microsoft.Authorization/policyAssignments@2024-04-01' = {
  name: 'novasteel-eu-locations'
  properties: {
    displayName: 'NovaSteel — allowed locations (EU residency)'
    description: 'EU regions are the enforced default for resource deployment (Constitution III v2.0.0). Non-EU is permitted only as a documented last-resort exemption when no EU region supports a required service.'
    policyDefinitionId: allowedLocationsResourcesDef
    enforcementMode: enforcementMode
    parameters: {
      listOfAllowedLocations: {
        value: allowedLocations
      }
    }
  }
}

resource resourceGroupLocations 'Microsoft.Authorization/policyAssignments@2024-04-01' = {
  name: 'novasteel-eu-rg-locations'
  properties: {
    displayName: 'NovaSteel — allowed locations for resource groups (EU residency)'
    description: 'EU regions are the enforced default for resource-group creation (Constitution III v2.0.0). Non-EU is permitted only as a documented last-resort exemption.'
    policyDefinitionId: allowedLocationsResourceGroupsDef
    enforcementMode: enforcementMode
    parameters: {
      listOfAllowedLocations: {
        value: allowedLocations
      }
    }
  }
}

output resourceLocationsAssignmentId string = resourceLocations.id
output resourceGroupLocationsAssignmentId string = resourceGroupLocations.id
