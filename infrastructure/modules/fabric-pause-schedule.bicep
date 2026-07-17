// Consumption Logic App that pauses the Microsoft Fabric capacity every day at 02:00
// (if it is currently running), to keep demo billing down. Constitution: cost control.
metadata description = 'Scheduled Logic App (Consumption) that suspends the Microsoft Fabric capacity nightly at 02:00 when it is Active.'

@description('Azure region for the Logic App.')
param location string

@description('Resource tags.')
param tags object = {}

@description('Logic App (workflow) name.')
param name string

@description('Name of the Microsoft Fabric capacity to pause.')
param fabricCapacityName string

@description('Hour of day (0-23, local to timeZone) at which the pause runs.')
@minValue(0)
@maxValue(23)
param scheduleHour int = 2

@description('Windows time zone id used to evaluate the schedule.')
param timeZone string = 'W. Europe Standard Time'

// Contributor is required to read capacity state and invoke the suspend action
// (Microsoft.Fabric/capacities/suspend/action). Scoped to the capacity only.
// NOTE: Contributor's role-definition GUID in this environment is 20f7382dd24c
// (matches container-app-simulator.bicep); the public-cloud GUID differs.
var contributorRoleId = 'b24988ac-6180-42a0-ab88-20f7382dd24c'

// Azure Resource Manager endpoint for the current cloud. resourceManager ends with '/',
// while resource ids start with '/', so trim the trailing slash to avoid '//'.
var armAudience = environment().resourceManager
#disable-next-line BCP329
var armBase = substring(armAudience, 0, length(armAudience) - 1)

resource capacity 'Microsoft.Fabric/capacities@2023-11-01' existing = {
  name: fabricCapacityName
}

resource workflow 'Microsoft.Logic/workflows@2019-05-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    state: 'Enabled'
    definition: {
      '$schema': 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#'
      contentVersion: '1.0.0.0'
      parameters: {
        capacityResourceId: {
          type: 'String'
          defaultValue: capacity.id
        }
      }
      triggers: {
        Daily_at_scheduled_hour: {
          type: 'Recurrence'
          recurrence: {
            frequency: 'Day'
            interval: 1
            timeZone: timeZone
            schedule: {
              hours: [
                string(scheduleHour)
              ]
              minutes: [
                0
              ]
            }
          }
        }
      }
      actions: {
        Get_capacity_state: {
          type: 'Http'
          runAfter: {}
          inputs: {
            method: 'GET'
            uri: '${armBase}@{parameters(\'capacityResourceId\')}?api-version=2023-11-01'
            authentication: {
              type: 'ManagedServiceIdentity'
              audience: armAudience
            }
          }
        }
        If_capacity_is_running: {
          type: 'If'
          runAfter: {
            Get_capacity_state: [
              'Succeeded'
            ]
          }
          expression: {
            equals: [
              '@toLower(coalesce(body(\'Get_capacity_state\')?[\'properties\']?[\'state\'], \'\'))'
              'active'
            ]
          }
          actions: {
            Suspend_capacity: {
              type: 'Http'
              runAfter: {}
              inputs: {
                method: 'POST'
                uri: '${armBase}@{parameters(\'capacityResourceId\')}/suspend?api-version=2023-11-01'
                authentication: {
                  type: 'ManagedServiceIdentity'
                  audience: armAudience
                }
              }
            }
          }
        }
      }
    }
  }
}

// Grant the Logic App's managed identity permission to read and suspend the capacity.
resource pauseRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(capacity.id, workflow.id, contributorRoleId)
  scope: capacity
  properties: {
    principalId: workflow.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', contributorRoleId)
    principalType: 'ServicePrincipal'
  }
}

output id string = workflow.id
output name string = workflow.name
output principalId string = workflow.identity.principalId
