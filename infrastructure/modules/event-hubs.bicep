// Event Hubs namespace for high-throughput telemetry streaming (Fabric Real-Time Intelligence source).
metadata description = 'Event Hubs namespace + hub + consumer group for streaming telemetry into Fabric RTI.'

@description('Azure region.')
param location string

@description('Resource tags.')
param tags object = {}

@description('Event Hubs namespace name (globally unique).')
param namespaceName string

@description('Event hub name.')
param eventHubName string = 'telemetry'

@description('Namespace SKU.')
@allowed([
  'Standard'
  'Premium'
])
param skuName string = 'Standard'

@description('Throughput units (Standard).')
@minValue(1)
param capacity int = 1

@description('Partition count for the event hub.')
@minValue(1)
@maxValue(32)
param partitionCount int = 4

@description('Message retention in days.')
@minValue(1)
@maxValue(7)
param messageRetentionInDays int = 3

@description('Consumer group for Fabric Real-Time Intelligence.')
param consumerGroupName string = 'fabric-rti'

resource namespace 'Microsoft.EventHub/namespaces@2024-01-01' = {
  name: namespaceName
  location: location
  tags: tags
  sku: {
    name: skuName
    tier: skuName
    capacity: capacity
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    minimumTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
    zoneRedundant: true
  }
}

resource eventHub 'Microsoft.EventHub/namespaces/eventhubs@2024-01-01' = {
  parent: namespace
  name: eventHubName
  properties: {
    partitionCount: partitionCount
    messageRetentionInDays: messageRetentionInDays
  }
}

resource consumerGroup 'Microsoft.EventHub/namespaces/eventhubs/consumergroups@2024-01-01' = {
  parent: eventHub
  name: consumerGroupName
}

output namespaceId string = namespace.id
output namespaceName string = namespace.name
output eventHubName string = eventHub.name
