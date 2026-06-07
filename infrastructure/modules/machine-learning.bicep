// Azure Machine Learning workspace for the RUL + energy models (training, MLOps, edge serving).
metadata description = 'Azure Machine Learning workspace (physics-informed RUL + energy models, MLOps registry) with a dedicated workspace storage account.'

@description('Azure region.')
param location string

@description('Resource tags.')
param tags object = {}

@description('Workspace name.')
param name string

@description('Friendly display name.')
param friendlyName string = 'NovaSteel Models'

@description('Dedicated workspace storage account name (3-24 lowercase alphanumeric).')
@maxLength(24)
param workspaceStorageName string

@description('Resource ID of the shared Key Vault.')
param keyVaultId string

@description('Resource ID of the Application Insights component.')
param applicationInsightsId string

@description('Resource ID of the shared Container Registry.')
param containerRegistryId string

resource workspaceStorage 'Microsoft.Storage/storageAccounts@2025-06-01' = {
  name: workspaceStorageName
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    publicNetworkAccess: 'Enabled'
  }
}

resource workspace 'Microsoft.MachineLearningServices/workspaces@2025-12-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: friendlyName
    storageAccount: workspaceStorage.id
    keyVault: keyVaultId
    applicationInsights: applicationInsightsId
    containerRegistry: containerRegistryId
    hbiWorkspace: false
    publicNetworkAccess: 'Enabled'
  }
}

output id string = workspace.id
output name string = workspace.name
output principalId string = workspace.identity.principalId
