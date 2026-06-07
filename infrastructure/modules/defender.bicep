// Microsoft Defender for Cloud plans (subscription scope).
metadata description = 'Enables Microsoft Defender for Cloud plans across the subscription (posture + workload protection).'

targetScope = 'subscription'

@description('Defender plans to enable with their tiers.')
param plans array = [
  { name: 'CloudPosture', tier: 'Standard' }
  { name: 'StorageAccounts', tier: 'Standard' }
  { name: 'KeyVaults', tier: 'Standard' }
  { name: 'Containers', tier: 'Standard' }
  { name: 'AppServices', tier: 'Standard' }
  { name: 'Arm', tier: 'Standard' }
  { name: 'Api', tier: 'Standard' }
  { name: 'VirtualMachines', tier: 'Standard' }
]

resource pricings 'Microsoft.Security/pricings@2024-01-01' = [
  for plan in plans: {
    name: plan.name
    properties: {
      pricingTier: plan.tier
    }
  }
]
