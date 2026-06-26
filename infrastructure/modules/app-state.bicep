// Azure SQL: audit + application/workflow-state store (research.md R7).
// Holds the immutable, append-only AuditRecord stream (Constitution II; 10y/5y retention per NFR-008)
// and application/workflow state. Entra-only authentication (no SQL logins).
metadata description = 'Azure SQL logical server + serverless database for audit records and application/workflow state. Entra-only auth.'

@description('Azure region (EU residency).')
param location string

@description('Resource tags.')
param tags object = {}

@description('SQL logical server name (lowercase, globally unique).')
param serverName string

@description('Database name.')
param databaseName string = 'novasteel-appstate'

@description('Entra (Azure AD) administrator display name (user UPN, group, or service principal name).')
param aadAdminLogin string

@description('Entra (Azure AD) administrator object ID (user/group/service principal).')
param aadAdminObjectId string

@description('Entra administrator principal type.')
@allowed([
  'User'
  'Group'
  'Application'
])
param aadAdminPrincipalType string = 'Group'

@description('Database SKU (default: General Purpose serverless, Gen5, 2 vCores).')
param skuName string = 'GP_S_Gen5_2'

resource sqlServer 'Microsoft.Sql/servers@2024-05-01-preview' = {
  name: serverName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    minimalTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
    administrators: {
      administratorType: 'ActiveDirectory'
      login: aadAdminLogin
      sid: aadAdminObjectId
      tenantId: subscription().tenantId
      principalType: aadAdminPrincipalType
      azureADOnlyAuthentication: true
    }
  }
}

resource database 'Microsoft.Sql/servers/databases@2024-05-01-preview' = {
  parent: sqlServer
  name: databaseName
  location: location
  tags: tags
  sku: {
    name: skuName
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    zoneRedundant: false
    autoPauseDelay: 60
    minCapacity: json('0.5')
  }
}

// Demo config (consistent with other modules): allow Azure services to reach the server.
// For production, replace with VNet rules / Private Link and disable public network access.
resource allowAzureServices 'Microsoft.Sql/servers/firewallRules@2024-05-01-preview' = {
  parent: sqlServer
  name: 'AllowAllAzureIps'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

output serverName string = sqlServer.name
output serverFqdn string = sqlServer.properties.fullyQualifiedDomainName
output databaseName string = database.name
