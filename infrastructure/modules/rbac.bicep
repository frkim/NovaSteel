// Centralized least-privilege RBAC role assignments across platform resources.
metadata description = 'Grants platform workload identities least-privilege data-plane access to storage, Key Vault, AI Services and ACR.'

@description('Data lake storage account name.')
param dataLakeStorageName string

@description('Key Vault name.')
param keyVaultName string

@description('AI Services (AI Foundry) account name.')
param aiServicesName string

@description('Container Registry name.')
param containerRegistryName string

@description('Function App managed identity principal ID.')
param functionPrincipalId string = ''

@description('Container App managed identity principal ID.')
param containerAppPrincipalId string = ''

// Built-in role definition IDs
var roles = {
  storageBlobDataContributor: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
  keyVaultSecretsUser: '4633458b-17de-408a-b874-0445c86b69e6'
  cognitiveServicesOpenAIUser: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
  acrPull: '7f951dda-4ed3-4680-a7ca-43fe172d538d'
}

resource dataLake 'Microsoft.Storage/storageAccounts@2025-06-01' existing = {
  name: dataLakeStorageName
}

resource keyVault 'Microsoft.KeyVault/vaults@2025-05-01' existing = {
  name: keyVaultName
}

resource aiServices 'Microsoft.CognitiveServices/accounts@2025-10-01-preview' existing = {
  name: aiServicesName
}

resource acr 'Microsoft.ContainerRegistry/registries@2025-11-01' existing = {
  name: containerRegistryName
}

// ---- Storage (data lake) ----
resource functionStorage 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(functionPrincipalId)) {
  name: guid(dataLake.id, functionPrincipalId, roles.storageBlobDataContributor)
  scope: dataLake
  properties: {
    principalId: functionPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.storageBlobDataContributor)
    principalType: 'ServicePrincipal'
  }
}

resource containerAppStorage 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(containerAppPrincipalId)) {
  name: guid(dataLake.id, containerAppPrincipalId, roles.storageBlobDataContributor)
  scope: dataLake
  properties: {
    principalId: containerAppPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.storageBlobDataContributor)
    principalType: 'ServicePrincipal'
  }
}

// ---- Key Vault ----
resource functionKv 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(functionPrincipalId)) {
  name: guid(keyVault.id, functionPrincipalId, roles.keyVaultSecretsUser)
  scope: keyVault
  properties: {
    principalId: functionPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.keyVaultSecretsUser)
    principalType: 'ServicePrincipal'
  }
}

resource containerAppKv 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(containerAppPrincipalId)) {
  name: guid(keyVault.id, containerAppPrincipalId, roles.keyVaultSecretsUser)
  scope: keyVault
  properties: {
    principalId: containerAppPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.keyVaultSecretsUser)
    principalType: 'ServicePrincipal'
  }
}

// ---- AI Services (OpenAI) ----
resource functionOpenAi 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(functionPrincipalId)) {
  name: guid(aiServices.id, functionPrincipalId, roles.cognitiveServicesOpenAIUser)
  scope: aiServices
  properties: {
    principalId: functionPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.cognitiveServicesOpenAIUser)
    principalType: 'ServicePrincipal'
  }
}

resource containerAppOpenAi 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(containerAppPrincipalId)) {
  name: guid(aiServices.id, containerAppPrincipalId, roles.cognitiveServicesOpenAIUser)
  scope: aiServices
  properties: {
    principalId: containerAppPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.cognitiveServicesOpenAIUser)
    principalType: 'ServicePrincipal'
  }
}

// ---- Container Registry (AcrPull) ----
resource containerAppAcr 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(containerAppPrincipalId)) {
  name: guid(acr.id, containerAppPrincipalId, roles.acrPull)
  scope: acr
  properties: {
    principalId: containerAppPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.acrPull)
    principalType: 'ServicePrincipal'
  }
}
