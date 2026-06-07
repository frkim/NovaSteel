// Platform user-assigned managed identity (Entra ID workload identity).
metadata description = 'User-assigned managed identity used by platform workloads for least-privilege access (Entra ID).'

@description('Azure region.')
param location string

@description('Resource tags.')
param tags object = {}

@description('Managed identity name.')
param name string

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: name
  location: location
  tags: tags
}

output id string = identity.id
output name string = identity.name
output principalId string = identity.properties.principalId
output clientId string = identity.properties.clientId
