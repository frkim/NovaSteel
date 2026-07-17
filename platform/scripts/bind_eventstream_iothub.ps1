<#
.SYNOPSIS
  Bind the Fabric Eventstream `es_telemetry` to Azure IoT Hub and land telemetry in the
  Eventhouse — entirely via the Fabric REST API (no portal step required).

.DESCRIPTION
  Contrary to earlier belief, the Fabric connections API DOES support IoT Hub — the
  connection type is `IoTHub` (exact casing; `IotHub` / `AzureEventHubs` are rejected).
  Steps:
    1. Create an `IoTHub` connection (IoTHub.Contents + Basic credentials = SAS policy/key).
    2. Set the eventstream topology (AzureIoTHub source -> DefaultStream -> Eventhouse
       destination) via updateDefinition. NOTE: the Eventhouse destination `itemId` must be
       the *KQLDatabase* item id, and its `inputNodes` must reference the stream (not the source).
  Because IoT Hub device messages are BATCHES (SimulatorDeviceMessage.readings[]), the
  destination lands the raw message into a staging table `TelemetryIngest`; a KQL update
  policy (`ExpandTelemetry`, see eventhouse-staging.kql) fans the array into flat `TelemetryRaw`.

  Run as an identity that is a Fabric workspace admin (or the capacity-admin SP with
  ServicePrincipalAccessGlobalAPIs enabled). Requires the F8 capacity to be resumed.

.EXAMPLE
  ./bind_eventstream_iothub.ps1 -IotHubName iot-novastee-dev-ox26fi -ResourceGroup rg-novasteel-dev
#>
[CmdletBinding()]
param(
  [string]$WorkspaceName = 'novasteel-dev',
  [string]$EventstreamName = 'es_telemetry',
  [string]$IotHubName = 'iot-novastee-dev-ox26fi',
  [string]$ResourceGroup = 'rg-novasteel-dev',
  [string]$SasPolicy = 'service',
  [string]$DatabaseName = 'novasteel_rti',
  [string]$StagingTable = 'TelemetryIngest',
  [string]$ConsumerGroup = '$Default'
)

$ErrorActionPreference = 'Stop'
$fabric = 'https://api.fabric.microsoft.com/v1'
function FabricHeaders {
  @{ Authorization = "Bearer $(az account get-access-token --resource 'https://api.fabric.microsoft.com' --query accessToken -o tsv)"; 'Content-Type' = 'application/json' }
}

$h = FabricHeaders
$ws = (Invoke-RestMethod -Uri "$fabric/workspaces" -Headers $h).value | Where-Object displayName -eq $WorkspaceName
if (-not $ws) { throw "Workspace '$WorkspaceName' not found (not admin, or SP API access disabled?)." }
$es = (Invoke-RestMethod -Uri "$fabric/workspaces/$($ws.id)/eventstreams" -Headers $h).value | Where-Object displayName -eq $EventstreamName
$kdb = (Invoke-RestMethod -Uri "$fabric/workspaces/$($ws.id)/kqlDatabases" -Headers $h).value | Select-Object -First 1

Write-Host "Creating IoTHub connection ..."
$key = az iot hub policy show --hub-name $IotHubName --name $SasPolicy --query primaryKey -o tsv
$connBody = @{
  connectivityType = 'ShareableCloud'; displayName = "novasteel-iothub"
  connectionDetails = @{ type = 'IoTHub'; creationMethod = 'IoTHub.Contents'
    parameters = @(@{ dataType = 'Text'; name = 'entityPath'; value = "$IotHubName.azure-devices.net" }) }
  privacyLevel = 'Organizational'
  credentialDetails = @{ singleSignOnType = 'None'; connectionEncryption = 'NotEncrypted'; skipTestConnection = $false
    credentials = @{ credentialType = 'Basic'; username = $SasPolicy; password = $key } }
} | ConvertTo-Json -Depth 8
$conn = Invoke-RestMethod -Method POST -Uri "$fabric/connections" -Headers $h -Body $connBody
Write-Host "  connectionId = $($conn.id)"

Write-Host "Setting eventstream topology (IoT Hub -> stream -> Eventhouse[$StagingTable]) ..."
$topology = [ordered]@{
  sources = @([ordered]@{ name = 'IoTHubInput'; type = 'AzureIoTHub'; properties = [ordered]@{ dataConnectionId = $conn.id; consumerGroupName = $ConsumerGroup; inputSerialization = [ordered]@{ type = 'Json'; properties = [ordered]@{ encoding = 'UTF8' } } } })
  destinations = @([ordered]@{ name = 'EventhouseOutput'; type = 'Eventhouse'; properties = [ordered]@{ dataIngestionMode = 'ProcessedIngestion'; workspaceId = $ws.id; itemId = $kdb.id; databaseName = $DatabaseName; tableName = $StagingTable; inputSerialization = [ordered]@{ type = 'Json'; properties = [ordered]@{ encoding = 'UTF8' } } }; inputNodes = @(@{ name = 'TelemetryStream' }) })
  streams = @([ordered]@{ name = 'TelemetryStream'; type = 'DefaultStream'; properties = @{}; inputNodes = @(@{ name = 'IoTHubInput' }) })
  operators = @(); compatibilityLevel = '1.1'
}
$b64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes(($topology | ConvertTo-Json -Depth 12)))
$defBody = @{ definition = @{ parts = @(@{ path = 'eventstream.json'; payload = $b64; payloadType = 'InlineBase64' }) } } | ConvertTo-Json -Depth 8
Invoke-WebRequest -Method POST -Uri "$fabric/workspaces/$($ws.id)/eventstreams/$($es.id)/updateDefinition" -Headers $h -Body $defBody -UseBasicParsing | Out-Null
Write-Host "Eventstream bound. Ensure eventhouse-staging.kql has been applied so readings[] fan into TelemetryRaw."
