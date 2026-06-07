// Centralized least-privilege RBAC role assignments across platform resources.
metadata description = 'Grants platform workload identities least-privilege data-plane access to storage, Key Vault, AI Services, AI Search and ACR.'

@description('Data lake storage account name.')
param dataLakeStorageName string

@description('Key Vault name.')
param keyVaultName string

@description('AI Services (AI Foundry) account name.')
param aiServicesName string

@description('AI Search service name.')
param searchName string

@description('Container Registry name.')
param containerRegistryName string

@description('Azure ML workspace managed identity principal ID.')
param mlPrincipalId string = ''

@description('Function App managed identity principal ID.')
param functionPrincipalId string = ''

@description('Container App managed identity principal ID.')
param containerAppPrincipalId string = ''

@description('AI Search managed identity principal ID.')
param searchPrincipalId string = ''

@description('Microsoft Foundry (AI Services) managed identity principal ID.')
param foundryPrincipalId string = ''

// Built-in role definition IDs
var roles = {
  storageBlobDataContributor: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
  storageBlobDataReader: '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'
  keyVaultSecretsUser: '4633458b-17de-408a-b874-0445c86b69e6'
  cognitiveServicesOpenAIUser: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
  searchIndexDataReader: '1407120a-92aa-4202-b7e9-c0e197c71c8f'
  searchServiceContributor: '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
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

resource search 'Microsoft.Search/searchServices@2025-05-01' existing = {
  name: searchName
}

resource acr 'Microsoft.ContainerRegistry/registries@2025-11-01' existing = {
  name: containerRegistryName
}

// ---- Storage (data lake) ----
resource mlStorage 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(mlPrincipalId)) {
  name: guid(dataLake.id, mlPrincipalId, roles.storageBlobDataContributor)
  scope: dataLake
  properties: {
    principalId: mlPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.storageBlobDataContributor)
    principalType: 'ServicePrincipal'
  }
}

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

resource searchStorageReader 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(searchPrincipalId)) {
  name: guid(dataLake.id, searchPrincipalId, roles.storageBlobDataReader)
  scope: dataLake
  properties: {
    principalId: searchPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.storageBlobDataReader)
    principalType: 'ServicePrincipal'
  }
}

// ---- Key Vault ----
resource mlKv 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(mlPrincipalId)) {
  name: guid(keyVault.id, mlPrincipalId, roles.keyVaultSecretsUser)
  scope: keyVault
  properties: {
    principalId: mlPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.keyVaultSecretsUser)
    principalType: 'ServicePrincipal'
  }
}

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

resource searchOpenAi 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(searchPrincipalId)) {
  name: guid(aiServices.id, searchPrincipalId, roles.cognitiveServicesOpenAIUser)
  scope: aiServices
  properties: {
    principalId: searchPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.cognitiveServicesOpenAIUser)
    principalType: 'ServicePrincipal'
  }
}

// ---- AI Search (RAG "on your data") ----
resource foundrySearchReader 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(foundryPrincipalId)) {
  name: guid(search.id, foundryPrincipalId, roles.searchIndexDataReader)
  scope: search
  properties: {
    principalId: foundryPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.searchIndexDataReader)
    principalType: 'ServicePrincipal'
  }
}

resource foundrySearchContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(foundryPrincipalId)) {
  name: guid(search.id, foundryPrincipalId, roles.searchServiceContributor)
  scope: search
  properties: {
    principalId: foundryPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.searchServiceContributor)
    principalType: 'ServicePrincipal'
  }
}

// ---- Container Registry (AcrPull) ----
resource mlAcr 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(mlPrincipalId)) {
  name: guid(acr.id, mlPrincipalId, roles.acrPull)
  scope: acr
  properties: {
    principalId: mlPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.acrPull)
    principalType: 'ServicePrincipal'
  }
}

resource containerAppAcr 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(containerAppPrincipalId)) {
  name: guid(acr.id, containerAppPrincipalId, roles.acrPull)
  scope: acr
  properties: {
    principalId: containerAppPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.acrPull)
    principalType: 'ServicePrincipal'
  }
}
