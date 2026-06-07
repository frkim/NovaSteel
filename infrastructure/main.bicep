// NovaSteel "Project Ignition" — subscription-scope entry point.
// Creates the resource group, enables Microsoft Defender for Cloud, and deploys the platform.
// Demo configuration: public network access, no private endpoints.
metadata description = 'Top-level deployment for the NovaSteel AI-powered steel production optimization platform.'

targetScope = 'subscription'

@description('Azure region for the resource group and all resources (EU residency).')
@allowed([
  'swedencentral'
  'westeurope'
  'germanywestcentral'
])
param location string = 'swedencentral'

@description('Short name prefix for the workload.')
param namePrefix string = 'novasteel'

@description('Environment short name (e.g. dev, test, pilot, prod).')
param environmentName string = 'dev'

@description('Name of the resource group to create/use.')
param resourceGroupName string = 'rg-${namePrefix}-${environmentName}'

@description('Enable Microsoft Defender for Cloud plans on the subscription.')
param enableDefenderForCloud bool = true

@description('Microsoft Fabric capacity SKU (F-SKU).')
param fabricSkuName string = 'F8'

@description('Fabric capacity administrators (Entra UPNs or service principal object IDs). Required.')
param fabricAdminMembers array

@description('Optional region override for Microsoft Purview (defaults to location). Some tenants restrict Purview regions.')
param purviewLocation string = ''

@description('Deploy Microsoft Purview (governance/lineage). Disable where tenant/region constraints apply.')
param deployPurview bool = true

@description('Additional resource tags.')
param tags object = {}

var defaultTags = {
  workload: 'project-ignition'
  application: 'novasteel-optimization-platform'
  environment: environmentName
  dataResidency: 'eu'
  managedBy: 'bicep'
}

var allTags = union(defaultTags, tags)

resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: allTags
}

module defender 'modules/defender.bicep' = if (enableDefenderForCloud) {
  name: 'defender-for-cloud'
  scope: subscription()
}

module platform 'resources.bicep' = {
  name: 'novasteel-platform'
  scope: resourceGroup
  params: {
    location: location
    namePrefix: namePrefix
    environmentName: environmentName
    tags: allTags
    fabricSkuName: fabricSkuName
    fabricAdminMembers: fabricAdminMembers
    purviewLocation: purviewLocation
    deployPurview: deployPurview
  }
}

output resourceGroupName string = resourceGroup.name
output location string = location
output foundryEndpoint string = platform.outputs.foundryEndpoint
output keyVaultName string = platform.outputs.keyVaultName
output dataLakeName string = platform.outputs.dataLakeName
output fabricCapacityName string = platform.outputs.fabricCapacityName
