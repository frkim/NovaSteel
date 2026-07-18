// Azure Monitor alerting: action group + drift and SLO scheduled-query alert rules.
metadata description = 'Observability hardening — model-drift and freshness/SLO alerts on the NovaSteel Log Analytics workspace (Constitution VI/observability). Alerts are advisory; they never actuate plant equipment.'

@description('Azure region.')
param location string

@description('Resource tags.')
param tags object = {}

@description('Name prefix, e.g. novasteel.')
param namePrefix string

@description('Environment short name, e.g. dev.')
param env string

@description('Resource id of the Log Analytics workspace the alerts query.')
param logAnalyticsId string

@description('Email address that receives alert notifications.')
param alertEmail string = ''

@description('Freshness SLO: alert if no simulator telemetry logs arrive within this many minutes.')
@allowed([
  5
  10
  15
  30
  45
  60
])
param freshnessSloMinutes int = 15

@description('Enable the scheduled-query alert rules.')
param enableAlerts bool = true

var actionGroupName = 'ag-${namePrefix}-${env}'
var hasEmail = !empty(alertEmail)

resource actionGroup 'Microsoft.Insights/actionGroups@2023-01-01' = {
  name: actionGroupName
  location: 'global'
  tags: tags
  properties: {
    groupShortName: take('${namePrefix}${env}', 12)
    enabled: true
    emailReceivers: hasEmail ? [
      {
        name: 'ops-email'
        emailAddress: alertEmail
        useCommonAlertSchema: true
      }
    ] : []
  }
}

// SLO / freshness: the simulator (OT->IT one-way ingestion) must keep emitting. If no console
// logs land within the SLO window, the pipeline may be stalled (Constitution IV/VI).
resource freshnessAlert 'Microsoft.Insights/scheduledQueryRules@2023-12-01' = if (enableAlerts) {
  name: 'alert-${namePrefix}-${env}-telemetry-freshness'
  location: location
  tags: tags
  properties: {
    displayName: 'NovaSteel telemetry freshness SLO breach'
    description: 'No simulator telemetry logs observed within the freshness SLO window; ingestion may be stalled.'
    severity: 2
    enabled: true
    scopes: [logAnalyticsId]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT${freshnessSloMinutes}M'
    criteria: {
      allOf: [
        {
          query: 'union isfuzzy=true ContainerAppConsoleLogs_CL\n| where Log_s has "telemetry" or Log_s has "readings"\n| summarize Count = count()'
          timeAggregation: 'Total'
          metricMeasureColumn: 'Count'
          operator: 'LessThanOrEqual'
          threshold: 0
          failingPeriods: {
            numberOfEvaluationPeriods: 1
            minFailingPeriodsToAlert: 1
          }
        }
      ]
    }
    autoMitigate: true
    actions: {
      actionGroups: [actionGroup.id]
    }
  }
}

// Model drift: watch P1 furnace-RUL prediction confidence. A sustained drop in mean confidence
// signals feature/model drift and warrants human review of the model (Constitution VI).
resource driftAlert 'Microsoft.Insights/scheduledQueryRules@2023-12-01' = if (enableAlerts) {
  name: 'alert-${namePrefix}-${env}-model-drift'
  location: location
  tags: tags
  properties: {
    displayName: 'NovaSteel P1 model drift (low mean confidence)'
    description: 'Mean P1 prediction confidence has dropped below the drift threshold over the window; review model/features.'
    severity: 3
    enabled: true
    scopes: [logAnalyticsId]
    evaluationFrequency: 'PT30M'
    windowSize: 'PT6H'
    criteria: {
      allOf: [
        {
          query: 'union isfuzzy=true (datatable(confidence_d:real)[]), P1Predictions_CL\n| summarize AvgConfidence = avg(todouble(confidence_d))'
          timeAggregation: 'Average'
          metricMeasureColumn: 'AvgConfidence'
          operator: 'LessThan'
          threshold: json('0.5')
          failingPeriods: {
            numberOfEvaluationPeriods: 1
            minFailingPeriodsToAlert: 1
          }
        }
      ]
    }
    autoMitigate: false
    actions: {
      actionGroups: [actionGroup.id]
    }
  }
}

output actionGroupId string = actionGroup.id
output actionGroupName string = actionGroup.name
