// Microsoft Purview account for data governance, lineage and classification.
metadata description = 'Microsoft Purview account providing end-to-end lineage, classification and EU AI Act traceability.'

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
