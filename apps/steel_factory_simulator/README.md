# Steel Factory Simulator

Device-side simulator for NovaSteel synthetic OT telemetry. It emits blast-furnace,
rolling-mill, and utility readings using `libs\NovaSteel.Contracts` and always sets
`origin = Synthetic` plus a `sourceId`.

## Run locally

```powershell
dotnet run --project apps\steel_factory_simulator\src\SteelFactorySimulator\SteelFactorySimulator.csproj -- --transport inmemory
```

Open `http://localhost:5080` for global start/stop, live sensor overview, and incident
injection.

## IoT Hub sink (opt-in)

Default transport is in-memory. Enable device-to-cloud publishing only with:

```powershell
$env:Simulator__Transport="IoTHub"
$env:Simulator__IotHub__DeviceId="sim-LU-BF1"
$env:Simulator__IotHub__KeyVaultUri="https://<vault>.vault.azure.net/"
$env:Simulator__IotHub__ConnectionStringSecretName="iothub-simulator-device-connection-string"
dotnet run --project apps\steel_factory_simulator\src\SteelFactorySimulator\SteelFactorySimulator.csproj
```

For local development you may set `Simulator__IotHub__ConnectionString`; do not commit
secrets. The production path uses managed identity to read the Key Vault secret. No
cloud-to-device, direct-method, or reverse control path is implemented.

## P1 degrading-furnace replay

```powershell
dotnet run --project apps\steel_factory_simulator\src\SteelFactorySimulator\SteelFactorySimulator.csproj -- --replay degrading-furnace-LU-BF1 --speed 100x --transport inmemory
```

The deterministic scenario ramps `ThermocoupleTemp`, `HeatFlux`, `Vibration`, and
`PowerDrawKw` over a 30-day horizon so a ≥21-day degradation signal is detectable. Use
the UI to trigger the same scenario for any furnace asset.

## Validate

```powershell
dotnet build apps\steel_factory_simulator\src\SteelFactorySimulator\SteelFactorySimulator.csproj
dotnet test apps\steel_factory_simulator\tests\SteelFactorySimulator.Tests\SteelFactorySimulator.Tests.csproj
```
