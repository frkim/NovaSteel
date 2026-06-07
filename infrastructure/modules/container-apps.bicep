// Azure Container Apps environment + energy-dispatch microservice (alternative/long-running host).
metadata description = 'Container Apps managed environment and a sample energy-dispatch microservice.'

@description('Azure region.')
param location string

@description('Resource tags.')
param tags object = {}

@description('Managed environment name.')
param environmentName string

@description('Sample container app name.')
param appName string = 'energy-dispatch'

@description('Resource ID of the Log Analytics workspace for environment logs.')
param logAnalyticsWorkspaceId string

@description('Container image for the sample app.')
param containerImage string = 'mcr.microsoft.com/k8se/quickstart:latest'

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2025-07-01' existing = {
  name: last(split(logAnalyticsWorkspaceId, '/'))
}

resource environment 'Microsoft.App/managedEnvironments@2025-01-01' = {
  name: environmentName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
    zoneRedundant: false
  }
}

resource app 'Microsoft.App/containerApps@2025-01-01' = {
  name: appName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: environment.id
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 80
        transport: 'auto'
        allowInsecure: false
      }
    }
    template: {
      containers: [
        {
          name: appName
          image: containerImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 5
      }
    }
  }
}

output environmentId string = environment.id
output environmentName string = environment.name
output appName string = app.name
output appPrincipalId string = app.identity.principalId
output appFqdn string = app.properties.configuration.ingress.fqdn
