// ADLS Gen2 data lake storage account (OneLake/Fabric shortcut target, medallion landing).
metadata description = 'Hierarchical-namespace storage account (ADLS Gen2) for the data lake.'

@description('Azure region.')
param location string

@description('Resource tags.')
param tags object = {}

@description('Storage account name (3-24 lowercase alphanumeric, globally unique).')
@maxLength(24)
param name string

@description('Storage SKU.')
@allowed([
  'Standard_LRS'
  'Standard_ZRS'
  'Standard_GRS'
])
param sku string = 'Standard_ZRS'

@description('Enable ADLS Gen2 hierarchical namespace.')
param enableHierarchicalNamespace bool = true

@description('Medallion containers to create.')
param containerNames array = [
  'bronze'
  'silver'
  'gold'
]

resource storage 'Microsoft.Storage/storageAccounts@2025-06-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: sku
  }
  kind: 'StorageV2'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    isHnsEnabled: enableHierarchicalNamespace
    accessTier: 'Hot'
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2025-06-01' = {
  parent: storage
  name: 'default'
  properties: {
    deleteRetentionPolicy: {
      enabled: true
      days: 7
    }
  }
}

resource containers 'Microsoft.Storage/storageAccounts/blobServices/containers@2025-06-01' = [
  for containerName in containerNames: {
    parent: blobService
    name: containerName
    properties: {
      publicAccess: 'None'
    }
  }
]

output id string = storage.id
output name string = storage.name
output primaryDfsEndpoint string = storage.properties.primaryEndpoints.dfs
output primaryBlobEndpoint string = storage.properties.primaryEndpoints.blob
