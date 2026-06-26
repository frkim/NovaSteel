// Dedicated Container App for the steel-factory simulator.
metadata description = 'Deploys the NovaSteel steel-factory simulator Container App into the existing managed environment.'

@description('Azure region.')
param location string

@description('Resource tags.')
param tags object = {}

@description('Simulator Container App name.')
param appName string

@description('Existing Container Apps managed environment resource ID.')
param managedEnvironmentId string

@description('Azure Container Registry name used for simulator image pulls.')
param containerRegistryName string

@description('Key Vault name containing the optional IoT Hub simulator device connection-string secret.')
param keyVaultName string

@description('Container image for the simulator app.')
param containerImage string = '${containerRegistryName}.azurecr.io/steel-factory-simulator:latest'

@description('IoT Hub simulator device identity.')
param simulatorDeviceId string = 'sim-steel-factory-simulator'

@description('Key Vault secret name containing the IoT Hub device connection string.')
param iotHubConnectionStringSecretName string = 'iothub-simulator-device-connection-string'

var acrLoginServer = '${containerRegistryName}.azurecr.io'
var roles = {
  acrPull: '7f951dda-4ed3-4680-a7ca-43fe172d538d'
  keyVaultSecretsUser: '4633458b-17de-408a-b874-0445c86b69e6'
}

resource acr 'Microsoft.ContainerRegistry/registries@2025-11-01' existing = {
  name: containerRegistryName
}

resource keyVault 'Microsoft.KeyVault/vaults@2025-05-01' existing = {
  name: keyVaultName
}

resource app 'Microsoft.App/containerApps@2025-01-01' = {
  name: appName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: managedEnvironmentId
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 80
        transport: 'auto'
        allowInsecure: false
      }
      registries: [
        {
          server: acrLoginServer
          identity: 'system'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'steel-factory-simulator'
          image: containerImage
          env: [
            {
              name: 'ASPNETCORE_URLS'
              value: 'http://+:80'
            }
            {
              name: 'Simulator__Transport'
              value: 'InMemory'
            }
            {
              name: 'Simulator__IotHub__DeviceId'
              value: simulatorDeviceId
            }
            {
              name: 'Simulator__IotHub__KeyVaultUri'
              value: keyVault.properties.vaultUri
            }
            {
              name: 'Simulator__IotHub__ConnectionStringSecretName'
              value: iotHubConnectionStringSecretName
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 3
      }
    }
  }
}

resource acrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, app.name, roles.acrPull)
  scope: acr
  properties: {
    principalId: app.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.acrPull)
    principalType: 'ServicePrincipal'
  }
}

resource keyVaultSecretsUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, app.name, roles.keyVaultSecretsUser)
  scope: keyVault
  properties: {
    principalId: app.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.keyVaultSecretsUser)
    principalType: 'ServicePrincipal'
  }
}

output appName string = app.name
output appPrincipalId string = app.identity.principalId
output appFqdn string = app.properties.configuration.ingress.fqdn
