// Azure Key Vault (RBAC) with public network access (demo configuration).
metadata description = 'Key Vault for platform secrets/keys, RBAC-authorized.'

@description('Azure region.')
param location string

@description('Resource tags.')
param tags object = {}

@description('Key Vault name (3-24 chars, globally unique).')
@maxLength(24)
param name string

@description('Tenant ID for the vault.')
param tenantId string = subscription().tenantId

resource keyVault 'Microsoft.KeyVault/vaults@2025-05-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    tenantId: tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
  }
}

output id string = keyVault.id
output name string = keyVault.name
output uri string = keyVault.properties.vaultUri
