// Azure AI Search for RAG over the operator procedure library.
metadata description = 'Azure AI Search service providing vector + semantic retrieval (RAG) for the GenAI knowledge assistant.'

@description('Azure region.')
param location string

@description('Resource tags.')
param tags object = {}

@description('Search service name (2-60 lowercase, globally unique).')
@maxLength(60)
param name string

@description('Search SKU.')
@allowed([
  'basic'
  'standard'
  'standard2'
  'standard3'
])
param skuName string = 'standard'

@description('Number of replicas.')
@minValue(1)
param replicaCount int = 1

@description('Number of partitions.')
@minValue(1)
param partitionCount int = 1

resource search 'Microsoft.Search/searchServices@2025-05-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: skuName
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    replicaCount: replicaCount
    partitionCount: partitionCount
    hostingMode: 'Default'
    semanticSearch: 'standard'
    publicNetworkAccess: 'enabled'
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
    disableLocalAuth: false
  }
}

output id string = search.id
output name string = search.name
output principalId string = search.identity.principalId
