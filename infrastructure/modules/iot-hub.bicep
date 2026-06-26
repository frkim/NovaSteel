// Azure IoT Hub for plant device telemetry (cloud-direct ingestion).
metadata description = 'IoT Hub for cloud-direct, one-way (device->cloud) plant telemetry ingestion. No edge runtime; no cloud-to-device path (Constitution IV).'

@description('Azure region.')
param location string

@description('Resource tags.')
param tags object = {}

@description('IoT Hub name (globally unique).')
param name string

@description('IoT Hub SKU name.')
@allowed([
  'S1'
  'S2'
  'S3'
  'B1'
  'B2'
  'B3'
])
param skuName string = 'S1'

@description('Number of provisioned IoT Hub units.')
@minValue(1)
param skuCapacity int = 1

@description('Number of device-to-cloud partitions.')
@minValue(2)
@maxValue(32)
param partitionCount int = 4

resource iotHub 'Microsoft.Devices/IotHubs@2023-06-30' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: skuName
    capacity: skuCapacity
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    minTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
    eventHubEndpoints: {
      events: {
        retentionTimeInDays: 1
        partitionCount: partitionCount
      }
    }
    routing: {
      fallbackRoute: {
        name: '$fallback'
        source: 'DeviceMessages'
        condition: 'true'
        endpointNames: [
          'events'
        ]
        isEnabled: true
      }
    }
  }
}

output id string = iotHub.id
output name string = iotHub.name
output hostName string = iotHub.properties.hostName
