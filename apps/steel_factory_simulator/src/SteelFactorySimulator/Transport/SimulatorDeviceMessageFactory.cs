using NovaSteel.Contracts;
using SteelFactorySimulator.Models;

namespace SteelFactorySimulator.Transport;

public static class SimulatorDeviceMessageFactory
{
    public const string SchemaVersion = "1.0";

    public static SimulatorDeviceMessage Create(
        string deviceId,
        IEnumerable<TelemetryReading> readings,
        string? injectedScenario = null,
        DateTimeOffset? enqueuedAt = null)
    {
        var batch = readings.ToArray();
        if (string.IsNullOrWhiteSpace(deviceId))
        {
            throw new ArgumentException("A device id is required.", nameof(deviceId));
        }

        if (batch.Length == 0)
        {
            throw new ArgumentException("At least one telemetry reading is required.", nameof(readings));
        }

        if (batch.Any(reading => reading.Origin != Origin.Synthetic || string.IsNullOrWhiteSpace(reading.SourceId)))
        {
            throw new InvalidOperationException("Simulator device messages may contain only synthetic readings with a sourceId.");
        }

        var timestamp = enqueuedAt ?? DateTimeOffset.UtcNow;
        var messageId = $"{deviceId}-{timestamp:yyyyMMddHHmmssfff}-{Guid.NewGuid():N}";
        return new SimulatorDeviceMessage(deviceId, messageId, timestamp, SchemaVersion, batch, injectedScenario);
    }
}
