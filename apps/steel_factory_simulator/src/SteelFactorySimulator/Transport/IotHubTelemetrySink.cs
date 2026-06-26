using System.Text;
using System.Text.Json;
using Microsoft.Azure.Devices.Client;
using Microsoft.Extensions.Options;
using NovaSteel.Contracts;
using SteelFactorySimulator.Models;
using SteelFactorySimulator.Options;
using SteelFactorySimulator.Simulation;

namespace SteelFactorySimulator.Transport;

public sealed class IotHubTelemetrySink : ITelemetrySink, IAsyncDisposable
{
    private readonly IotHubOptions _options;
    private readonly IotHubConnectionStringProvider _connectionStrings;
    private readonly ScenarioState _scenarioState;
    private readonly ILogger<IotHubTelemetrySink> _logger;
    private readonly List<TelemetryReading> _buffer = [];
    private readonly SemaphoreSlim _lock = new(1, 1);
    private DeviceClient? _client;

    public IotHubTelemetrySink(IOptions<IotHubOptions> options, ScenarioState scenarioState, ILogger<IotHubTelemetrySink> logger)
    {
        _options = options.Value;
        _connectionStrings = new IotHubConnectionStringProvider(options);
        _scenarioState = scenarioState;
        _logger = logger;
    }

    public async ValueTask PublishAsync(TelemetryReading reading, CancellationToken ct = default)
    {
        if (reading.Origin != Origin.Synthetic || string.IsNullOrWhiteSpace(reading.SourceId))
        {
            throw new InvalidOperationException("The simulator IoT Hub sink refuses non-synthetic telemetry or missing sourceId values.");
        }

        await _lock.WaitAsync(ct);
        try
        {
            _buffer.Add(reading);
            if (_buffer.Count >= Math.Max(_options.BatchSize, 1))
            {
                await FlushLockedAsync(ct);
            }
        }
        finally
        {
            _lock.Release();
        }
    }

    public async ValueTask FlushAsync(CancellationToken ct = default)
    {
        await _lock.WaitAsync(ct);
        try
        {
            await FlushLockedAsync(ct);
        }
        finally
        {
            _lock.Release();
        }
    }

    public async ValueTask DisposeAsync()
    {
        if (_client is not null)
        {
            await _client.CloseAsync();
            _client.Dispose();
        }

        _lock.Dispose();
    }

    internal static Message CreateIotHubMessage(SimulatorDeviceMessage deviceMessage)
    {
        var json = JsonSerializer.Serialize(deviceMessage, NovaSteelJson.Options);
        var message = new Message(Encoding.UTF8.GetBytes(json))
        {
            MessageId = deviceMessage.MessageId,
            ContentType = "application/json",
            ContentEncoding = "utf-8"
        };
        message.Properties["schemaVersion"] = deviceMessage.SchemaVersion;
        if (!string.IsNullOrWhiteSpace(deviceMessage.InjectedScenario))
        {
            message.Properties["injectedScenario"] = deviceMessage.InjectedScenario;
        }

        return message;
    }

    private async Task FlushLockedAsync(CancellationToken ct)
    {
        if (_buffer.Count == 0)
        {
            return;
        }

        var payload = SimulatorDeviceMessageFactory.Create(_options.DeviceId, _buffer, _scenarioState.ActiveScenarioId);
        using var message = CreateIotHubMessage(payload);
        var client = await GetClientAsync(ct);
        await client.SendEventAsync(message, ct);
        _logger.LogInformation("Published {Count} synthetic simulator readings to IoT Hub as {MessageId}", _buffer.Count, payload.MessageId);
        _buffer.Clear();
    }

    private async Task<DeviceClient> GetClientAsync(CancellationToken ct)
    {
        if (_client is not null)
        {
            return _client;
        }

        var connectionString = await _connectionStrings.GetConnectionStringAsync(ct);
        _client = DeviceClient.CreateFromConnectionString(connectionString, TransportType.Mqtt);
        await _client.OpenAsync(ct);
        return _client;
    }
}
