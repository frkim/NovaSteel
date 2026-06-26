using System.Threading.Channels;

namespace NovaSteel.Contracts;

/// <summary>Publishes telemetry to a transport (IoT Hub / Event Hubs in prod, in-memory in tests).</summary>
public interface ITelemetrySink
{
    ValueTask PublishAsync(TelemetryReading reading, CancellationToken ct = default);
}

/// <summary>Consumes a stream of telemetry from a transport.</summary>
public interface ITelemetrySource
{
    IAsyncEnumerable<TelemetryReading> ReadAllAsync(CancellationToken ct = default);
}

/// <summary>In-memory transport used for local development and tests.</summary>
public sealed class InMemoryTelemetryChannel : ITelemetrySink, ITelemetrySource
{
    private readonly Channel<TelemetryReading> _channel = Channel.CreateUnbounded<TelemetryReading>();

    public ValueTask PublishAsync(TelemetryReading reading, CancellationToken ct = default)
        => _channel.Writer.WriteAsync(reading, ct);

    public void Complete() => _channel.Writer.Complete();

    public IAsyncEnumerable<TelemetryReading> ReadAllAsync(CancellationToken ct = default)
        => _channel.Reader.ReadAllAsync(ct);
}
