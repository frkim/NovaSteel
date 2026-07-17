// Azure Policy: EU data-residency guardrail (subscription scope).
// Constitution III — residency MUST be enforced by Azure Policy, not convention.
metadata description = 'Assigns built-in Allowed Locations policies to restrict all resources and resource groups to approved EU regions.'

targetScope = 'subscription'

@description('Approved EU regions for all resources and resource groups (data residency).')
param allowedLocations array = [
  'swedencentral'
  'westeurope'
  'germanywestcentral'
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
    description: 'Restricts resource deployment to approved EU regions (Constitution III — EU data residency).'
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
    description: 'Restricts resource-group creation to approved EU regions (Constitution III — EU data residency).'
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
