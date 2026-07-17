// Resource-group orchestrator: deploys the full NovaSteel platform into one resource group.
metadata description = 'Deploys the NovaSteel "Project Ignition" Azure platform (data, AI/ML, ingestion, apps, governance, security) into a resource group. Demo configuration: public network access, no private endpoints.'

@description('Azure region for all resources (EU residency).')
param location string

@description('Short name prefix for the workload.')
param namePrefix string = 'novasteel'

@description('Environment short name (e.g. dev, test, pilot, prod).')
param environmentName string = 'dev'

@description('Resource tags applied to every resource.')
param tags object = {}

@description('Microsoft Fabric capacity SKU (F-SKU).')
param fabricSkuName string = 'F8'

@description('Fabric capacity administrators (Entra UPNs or service principal object IDs). Required.')
param fabricAdminMembers array

@description('Optional region override for Microsoft Purview (defaults to location). Some tenants restrict Purview regions.')
param purviewLocation string = ''

@description('Region for Azure IoT Hub. IoT Hub is not available in every EU region (e.g. not swedencentral), so it is placed in an EU region that supports it while keeping data EU-resident.')
@allowed([
  'westeurope'
  'germanywestcentral'
  'northeurope'
])
param iotHubLocation string = 'westeurope'

@description('Deploy Microsoft Purview (governance/lineage). Disable where tenant/region constraints apply.')
param deployPurview bool = true

@description('Deploy the Azure SQL audit/app-state store. Requires sqlAadAdminObjectId when true.')
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

// ---------- Naming ----------
var token = toLower(take(uniqueString(resourceGroup().id, environmentName), 6))
var short = toLower(take(replace(namePrefix, '-', ''), 8))
var env = toLower(environmentName)

var names = {
  logAnalytics: 'log-${namePrefix}-${env}'
  appInsights: 'appi-${namePrefix}-${env}'
  identity: 'id-${namePrefix}-${env}'
  keyVault: take('kv${short}${env}${token}', 24)
  dataLake: take('dl${short}${env}${token}', 24)
  funcStorage: take('fns${short}${token}', 24)
  acr: take('acr${short}${env}${token}', 50)
  iotHub: 'iot-${short}-${env}-${token}'
  eventHubs: 'evhns-${short}-${env}-${token}'
  fabric: take('fab${short}${env}${token}', 63)
  foundry: 'aif-${short}-${env}-${token}'
  purview: 'pview-${short}-${env}-${token}'
  functionApp: 'func-${short}-${env}-${token}'
  functionPlan: 'plan-${short}-${env}-${token}'
  containerEnv: 'cae-${short}-${env}-${token}'
  simulatorApp: 'sim-${short}-${env}-${token}'
  sqlServer: 'sql-${short}-${env}-${token}'
  fabricPause: 'logic-${short}-fabricpause-${env}'
}

// ---------- Observability ----------
module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring'
  params: {
    location: location
    tags: tags
    logAnalyticsName: names.logAnalytics
    applicationInsightsName: names.appInsights
  }
}

// ---------- Identity ----------
module identity 'modules/identity.bicep' = {
  name: 'identity'
  params: {
    location: location
    tags: tags
    name: names.identity
  }
}

// ---------- Key Vault ----------
module keyVault 'modules/keyvault.bicep' = {
  name: 'keyvault'
  params: {
    location: location
    tags: tags
    name: names.keyVault
  }
}

// ---------- Data lake (ADLS Gen2) ----------
module dataLake 'modules/storage.bicep' = {
  name: 'datalake'
  params: {
    location: location
    tags: tags
    name: names.dataLake
  }
}

// ---------- Container Registry ----------
module acr 'modules/container-registry.bicep' = {
  name: 'acr'
  params: {
    location: location
    tags: tags
    name: names.acr
  }
}

// ---------- IoT Hub ----------
module iotHub 'modules/iot-hub.bicep' = {
  name: 'iothub'
  params: {
    location: iotHubLocation
    tags: tags
    name: names.iotHub
  }
}

// ---------- Event Hubs ----------
module eventHubs 'modules/event-hubs.bicep' = {
  name: 'eventhubs'
  params: {
    location: location
    tags: tags
    namespaceName: names.eventHubs
  }
}

// ---------- Microsoft Fabric ----------
module fabric 'modules/fabric.bicep' = {
  name: 'fabric'
  params: {
    location: location
    tags: tags
    name: names.fabric
    skuName: fabricSkuName
    adminMembers: fabricAdminMembers
  }
}

// ---------- Fabric nightly pause schedule ----------
@description('Deploy the Logic App that pauses the Fabric capacity nightly at 02:00 (cost control).')
param deployFabricPauseSchedule bool = true

@description('Hour (0-23, W. Europe time) at which the Fabric capacity is paused.')
param fabricPauseHour int = 2

module fabricPause 'modules/fabric-pause-schedule.bicep' = if (deployFabricPauseSchedule) {
  name: 'fabric-pause-schedule'
  params: {
    location: location
    tags: tags
    name: names.fabricPause
    fabricCapacityName: fabric.outputs.name
    scheduleHour: fabricPauseHour
  }
}

// ---------- Microsoft Foundry (AI Services + GPT-5) ----------
module foundry 'modules/foundry.bicep' = {
  name: 'foundry'
  params: {
    location: location
    tags: tags
    name: names.foundry
  }
}

// ---------- Energy-dispatch Function App ----------
module functions 'modules/functions.bicep' = {
  name: 'functions'
  params: {
    location: location
    tags: tags
    name: names.functionApp
    planName: names.functionPlan
    storageAccountName: names.funcStorage
    applicationInsightsConnectionString: monitoring.outputs.applicationInsightsConnectionString
  }
}

// ---------- Container Apps ----------
module containerApps 'modules/container-apps.bicep' = {
  name: 'containerapps'
  params: {
    location: location
    tags: tags
    environmentName: names.containerEnv
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsId
  }
}

@description('Deploy the steel-factory simulator Container App. Disable to skip re-provisioning an already-deployed simulator (avoids ACA update lag).')
param deploySimulator bool = true

module simulatorApp 'modules/container-app-simulator.bicep' = if (deploySimulator) {
  name: 'simulator-containerapp'
  params: {
    location: location
    tags: tags
    appName: names.simulatorApp
    managedEnvironmentId: containerApps.outputs.environmentId
    containerRegistryName: names.acr
    keyVaultName: names.keyVault
    fabricCapacityName: names.fabric
  }
  dependsOn: [
    acr
    keyVault
  ]
}

// ---------- Purview ----------
module purview 'modules/purview.bicep' = if (deployPurview) {
  name: 'purview'
  params: {
    location: empty(purviewLocation) ? location : purviewLocation
    tags: tags
    name: names.purview
  }
}

// ---------- App-state / audit store (Azure SQL) ----------
module appState 'modules/app-state.bicep' = if (deployAppState && !empty(sqlAadAdminObjectId)) {
  name: 'appstate'
  params: {
    location: location
    tags: tags
    serverName: names.sqlServer
    aadAdminLogin: sqlAadAdminLogin
    aadAdminObjectId: sqlAadAdminObjectId
    aadAdminPrincipalType: sqlAadAdminPrincipalType
  }
}

// ---------- RBAC wiring ----------
module rbac 'modules/rbac.bicep' = {
  name: 'rbac'
  params: {
    dataLakeStorageName: names.dataLake
    keyVaultName: names.keyVault
    aiServicesName: names.foundry
    containerRegistryName: names.acr
    functionPrincipalId: functions.outputs.principalId
    containerAppPrincipalId: containerApps.outputs.appPrincipalId
  }
  dependsOn: [
    dataLake
  ]
}

// ---------- Outputs ----------
output logAnalyticsName string = monitoring.outputs.logAnalyticsName
output applicationInsightsName string = monitoring.outputs.applicationInsightsName
output managedIdentityName string = identity.outputs.name
output keyVaultName string = keyVault.outputs.name
output dataLakeName string = dataLake.outputs.name
output containerRegistryName string = acr.outputs.name
output iotHubName string = iotHub.outputs.name
output eventHubsNamespace string = eventHubs.outputs.namespaceName
output fabricCapacityName string = fabric.outputs.name
output fabricPauseWorkflowName string = deployFabricPauseSchedule ? fabricPause!.outputs.name : ''
output foundryName string = foundry.outputs.name
output foundryEndpoint string = foundry.outputs.endpoint
output functionAppName string = functions.outputs.name
output containerAppsEnvironmentName string = containerApps.outputs.environmentName
output simulatorAppName string = deploySimulator ? simulatorApp!.outputs.appName : ''
output simulatorAppFqdn string = deploySimulator ? simulatorApp!.outputs.appFqdn : ''
output purviewName string = deployPurview ? purview!.outputs.name : ''
output appStateServerName string = (deployAppState && !empty(sqlAadAdminObjectId)) ? appState!.outputs.serverName : ''
output appStateDatabaseName string = (deployAppState && !empty(sqlAadAdminObjectId)) ? appState!.outputs.databaseName : ''
