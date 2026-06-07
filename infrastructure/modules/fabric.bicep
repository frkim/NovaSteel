// Microsoft Fabric capacity (OneLake, data engineering, RTI, warehouse, Power BI).
metadata description = 'Microsoft Fabric capacity backing the OneLake data platform, Real-Time Intelligence and Power BI (pinned to an EU region).'

@description('Azure region for the Fabric capacity (EU residency).')
param location string

@description('Resource tags.')
param tags object = {}

@description('Fabric capacity name (lowercase, 3-63 chars, globally unique).')
param name string

@description('Fabric capacity SKU (F-SKU). Sizing is a workshop decision.')
@allowed([
  'F2'
  'F4'
  'F8'
  'F16'
  'F32'
  'F64'
  'F128'
])
param skuName string = 'F8'

@description('Capacity administrators: Entra UPNs or service principal object IDs.')
param adminMembers array

resource capacity 'Microsoft.Fabric/capacities@2023-11-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: skuName
    tier: 'Fabric'
  }
  properties: {
    administration: {
      members: adminMembers
    }
  }
}

output id string = capacity.id
output name string = capacity.name
