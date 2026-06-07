// Microsoft Foundry (Cognitive Services AIServices account) + project + GPT-5 model deployments.
// Microsoft Foundry was formerly branded "Azure AI Foundry"; the underlying resource
// type (Microsoft.CognitiveServices/accounts, kind=AIServices) is unchanged.
metadata description = 'Microsoft Foundry account (kind=AIServices) with a Foundry project and Azure OpenAI GPT-5 model deployments for the knowledge-capture assistant.'

@description('Azure region.')
param location string

@description('Resource tags.')
param tags object = {}

@description('Microsoft Foundry / AI Services account name (globally unique, used as custom subdomain).')
param name string

@description('Foundry project name.')
param projectName string = 'novasteel-knowledge'

@description('Friendly display name for the project.')
param projectDisplayName string = 'NovaSteel Knowledge Capture'

@description('Model deployments to create (GPT-5 chat/reasoning + embeddings).')
param modelDeployments array = [
  {
    name: 'gpt-5'
    model: 'gpt-5'
    version: '2025-08-07'
    skuName: 'GlobalStandard'
    capacity: 20
  }
  {
    name: 'text-embedding-3-large'
    model: 'text-embedding-3-large'
    version: '1'
    skuName: 'Standard'
    capacity: 50
  }
]

resource account 'Microsoft.CognitiveServices/accounts@2025-10-01-preview' = {
  name: name
  location: location
  tags: tags
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: name
    allowProjectManagement: true
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
    disableLocalAuth: false
  }
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2025-10-01-preview' = {
  parent: account
  name: projectName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    displayName: projectDisplayName
    description: 'Grounded knowledge-capture assistant (RAG over operator procedures).'
  }
}

@batchSize(1)
resource deployments 'Microsoft.CognitiveServices/accounts/deployments@2025-10-01-preview' = [
  for deployment in modelDeployments: {
    parent: account
    name: deployment.name
    sku: {
      name: deployment.skuName
      capacity: deployment.capacity
    }
    properties: {
      model: {
        format: 'OpenAI'
        name: deployment.model
        version: deployment.version
      }
    }
  }
]

output id string = account.id
output name string = account.name
output endpoint string = account.properties.endpoint
output principalId string = account.identity.principalId
output projectName string = project.name
