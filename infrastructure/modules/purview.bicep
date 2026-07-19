// Microsoft Purview account for data governance, lineage and classification.
metadata description = 'Microsoft Purview account for lineage/classification. NOTE: classic Purview is region-restricted per tenant and may not have an EU service location — deploy ONLY where an EU region is supported, else Principle III (EU residency) is violated. Where Purview is US-only, use Fabric OneLake catalog lineage + the immutable audit trail instead (see platform/governance/README.md §1).'

@description('Azure region.')
param location string

@description('Resource tags.')
param tags object = {}

@description('Purview account name (3-63 chars, globally unique).')
param name string

@description('Public network access setting.')
@allowed([
  'Enabled'
  'Disabled'
])
param publicNetworkAccess string = 'Enabled'

resource purview 'Microsoft.Purview/accounts@2021-12-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    publicNetworkAccess: publicNetworkAccess
    managedResourceGroupName: 'managed-rg-${name}'
  }
}

output id string = purview.id
output name string = purview.name
output principalId string = purview.identity.principalId
