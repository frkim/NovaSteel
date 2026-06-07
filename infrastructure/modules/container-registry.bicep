// Azure Container Registry for ML images and Container Apps.
metadata description = 'Container Registry for model/container images.'

@description('Azure region.')
param location string

@description('Resource tags.')
param tags object = {}

@description('Registry name (5-50 alphanumeric, globally unique).')
@maxLength(50)
param name string

@description('Registry SKU.')
@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param skuName string = 'Standard'

resource registry 'Microsoft.ContainerRegistry/registries@2025-11-01' = {
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
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'
  }
}

output id string = registry.id
output name string = registry.name
output loginServer string = registry.properties.loginServer
