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

@description('Enforce EU data-residency via Azure Policy (allowed locations). Constitution III.')
param enforceEuResidencyPolicy bool = true

@description('Microsoft Fabric capacity SKU (F-SKU).')
param fabricSkuName string = 'F8'

@description('Fabric capacity administrators (Entra UPNs or service principal object IDs). Required.')
param fabricAdminMembers array

@description('Optional region override for Microsoft Purview (defaults to location). Some tenants restrict Purview regions.')
param purviewLocation string = ''

@description('Region for Azure IoT Hub (not available in swedencentral). Kept within the EU allowed set for data residency.')
@allowed([
  'westeurope'
  'germanywestcentral'
  'northeurope'
])
param iotHubLocation string = 'westeurope'

@description('Deploy Microsoft Purview (governance/lineage). Disable where tenant/region constraints apply.')
param deployPurview bool = true

@description('Deploy the steel-factory simulator Container App. Disable to skip re-provisioning an already-deployed simulator.')
param deploySimulator bool = true

@description('Deploy the Logic App that pauses the Fabric capacity nightly at 02:00 (cost control).')
param deployFabricPauseSchedule bool = true

@description('Hour (0-23, W. Europe time) at which the Fabric capacity is paused.')
@minValue(0)
@maxValue(23)
param fabricPauseHour int = 2

@description('Deploy the Azure SQL audit/app-state store (research.md R7). Requires sqlAadAdminObjectId when true.')
param deployAppState bool = false

@description('Entra admin display name for the Azure SQL audit store (user UPN, group, or SP name).')
param sqlAadAdminLogin string = ''

@description('Entra admin object ID for the Azure SQL audit store.')
param sqlAadAdminObjectId string = ''

@description('Entra admin principal type for the Azure SQL audit store.')
@allowed([
  'User'
  'Group'
  'Application'
])
param sqlAadAdminPrincipalType string = 'Group'

@description('Additional resource tags.')
param tags object = {}

var defaultTags = {
  workload: 'project-ignition'
  application: 'novasteel-optimization-platform'
  environment: environmentName
  dataResidency: 'eu'
  managedBy: 'bicep'
  SecurityControl: 'Ignore'
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

module euResidencyPolicy 'modules/policy.bicep' = if (enforceEuResidencyPolicy) {
  name: 'eu-residency-policy'
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
    iotHubLocation: iotHubLocation
    deployPurview: deployPurview
    deploySimulator: deploySimulator
    deployFabricPauseSchedule: deployFabricPauseSchedule
    fabricPauseHour: fabricPauseHour
    deployAppState: deployAppState
    sqlAadAdminLogin: sqlAadAdminLogin
    sqlAadAdminObjectId: sqlAadAdminObjectId
    sqlAadAdminPrincipalType: sqlAadAdminPrincipalType
  }
}

output resourceGroupName string = resourceGroup.name
output location string = location
output foundryEndpoint string = platform.outputs.foundryEndpoint
output keyVaultName string = platform.outputs.keyVaultName
output dataLakeName string = platform.outputs.dataLakeName
output fabricCapacityName string = platform.outputs.fabricCapacityName
output fabricPauseWorkflowName string = platform.outputs.fabricPauseWorkflowName
