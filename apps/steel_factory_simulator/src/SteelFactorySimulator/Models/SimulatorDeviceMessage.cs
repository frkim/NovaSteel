using NovaSteel.Contracts;

namespace SteelFactorySimulator.Models;

public sealed record SimulatorDeviceMessage(
    string DeviceId,
    string MessageId,
    DateTimeOffset EnqueuedAt,
    string SchemaVersion,
    IReadOnlyList<TelemetryReading> Readings,
    string? InjectedScenario = null);
