<#
.SYNOPSIS
  Provision the NovaSteel Fabric workspace + lakehouse on the live F8 capacity.

.DESCRIPTION
  Creates a Fabric workspace, assigns it to the deployed capacity
  (fabnovasteedevox26fi), and creates the medallion lakehouse + RTI Eventhouse.
  Run AS AN IDENTITY THAT IS A FABRIC CAPACITY ADMIN and permitted to call the
  Fabric APIs. In this environment two constraints apply (see platform/README.md):
    * the F8 capacity admin is a service principal (guest users are rejected by Fabric);
    * calling the Fabric APIs as a service principal requires the tenant setting
      "Service principals can use Fabric APIs" to be enabled (else HTTP 401).
  It also RESUMES the capacity first (it is paused by default to avoid F8 billing).

.EXAMPLE
  ./create_fabric_workspace.ps1 -WorkspaceName novasteel-dev
#>
[CmdletBinding()]
param(
  [string]$WorkspaceName = 'novasteel-dev',
  [string]$LakehouseName = 'onelake_novasteel',
  [string]$EventhouseName = 'novasteel-rti',
  [string]$SubscriptionId = '3377065c-bf76-4767-a982-32bce4ffb592',
  [string]$ResourceGroup = 'rg-novasteel-dev',
  [string]$CapacityName = 'fabnovasteedevox26fi',
  [switch]$PauseAfter
)

$ErrorActionPreference = 'Stop'
$capResId = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroup/providers/Microsoft.Fabric/capacities/$CapacityName"

Write-Host "Resuming Fabric capacity $CapacityName ..."
az rest --method post --url "https://management.azure.com$capResId/resume?api-version=2023-11-01" | Out-Null
Start-Sleep 30

$tok = az account get-access-token --resource 'https://api.fabric.microsoft.com' --query accessToken -o tsv
$headers = @{ Authorization = "Bearer $tok"; 'Content-Type' = 'application/json' }
$fabric = 'https://api.fabric.microsoft.com/v1'

$capId = (Invoke-RestMethod -Uri "$fabric/capacities" -Headers $headers -Method GET).value |
  Where-Object { $_.displayName -eq $CapacityName } | Select-Object -ExpandProperty id
if (-not $capId) { throw "Capacity $CapacityName not visible to caller (not a capacity admin?)." }

Write-Host "Creating workspace $WorkspaceName ..."
$ws = Invoke-RestMethod -Method POST -Uri "$fabric/workspaces" -Headers $headers `
  -Body (@{ displayName = $WorkspaceName; description = 'NovaSteel Project Ignition data-and-AI workspace' } | ConvertTo-Json)

Write-Host "Assigning capacity ..."
Invoke-RestMethod -Method POST -Uri "$fabric/workspaces/$($ws.id)/assignToCapacity" -Headers $headers `
  -Body (@{ capacityId = $capId } | ConvertTo-Json) | Out-Null

Write-Host "Creating lakehouse $LakehouseName ..."
Invoke-RestMethod -Method POST -Uri "$fabric/workspaces/$($ws.id)/lakehouses" -Headers $headers `
  -Body (@{ displayName = $LakehouseName } | ConvertTo-Json) | Out-Null

Write-Host "Creating eventhouse $EventhouseName (then run platform/rti/eventhouse.kql) ..."
Invoke-RestMethod -Method POST -Uri "$fabric/workspaces/$($ws.id)/eventhouses" -Headers $headers `
  -Body (@{ displayName = $EventhouseName } | ConvertTo-Json) | Out-Null

Write-Host "Workspace $($ws.id) ready. Import the medallion notebooks, eventstream, and Data Factory pipeline next."

if ($PauseAfter) {
  az rest --method post --url "https://management.azure.com$capResId/suspend?api-version=2023-11-01" | Out-Null
  Write-Host "Capacity paused."
}
