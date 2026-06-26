using System.Collections.Concurrent;
using Microsoft.Extensions.Options;
using NovaSteel.Contracts;
using SteelFactorySimulator.Options;

namespace SteelFactorySimulator.Simulation;

public sealed class SimulationController(
    SensorReadingEngine engine,
    ITelemetrySink sink,
    IOptions<SimulatorOptions> options,
    ScenarioState scenarioState,
    ILogger<SimulationController> logger)
{
    private readonly ConcurrentDictionary<string, TelemetryReading> _latest = new(StringComparer.OrdinalIgnoreCase);
    private readonly SemaphoreSlim _stepLock = new(1, 1);
    private readonly SimulatorOptions _options = options.Value;
    private int _stepIndex;
    private DateTimeOffset _currentTime = DateTimeOffset.UtcNow;
    private ActiveScenario? _scenario;

    public bool IsRunning { get; private set; }

    public void Start() => IsRunning = true;

    public void Stop() => IsRunning = false;

    public void StartDegradingFurnace(string assetId, int horizonDays)
    {
        var normalizedAssetId = assetId.Trim().ToUpperInvariant();
        _scenario = new ActiveScenario($"degrading-furnace-{normalizedAssetId}", "degrading-furnace", normalizedAssetId, _currentTime, horizonDays);
        scenarioState.Set(_scenario);
        logger.LogInformation("Started deterministic degrading-furnace scenario {ScenarioId}", _scenario.Id);
    }

    public void ClearScenario()
    {
        _scenario = null;
        scenarioState.Clear();
    }

    public async ValueTask StepAsync(CancellationToken cancellationToken = default)
    {
        if (!IsRunning)
        {
            return;
        }

        await _stepLock.WaitAsync(cancellationToken);
        try
        {
            var readings = engine.Generate(_currentTime, _stepIndex, _scenario);
            foreach (var reading in readings)
            {
                _latest[$"{reading.AssetId}:{reading.Metric}"] = reading;
                await sink.PublishAsync(reading, cancellationToken);
            }

            _stepIndex++;
            var speed = Math.Max(_options.Replay?.SpeedMultiplier ?? 1, 1);
            _currentTime = _currentTime.AddMinutes(Math.Max(_options.StepMinutes, 1) * speed);
        }
        finally
        {
            _stepLock.Release();
        }
    }

    public IReadOnlyCollection<TelemetryReading> GetSnapshot() => _latest.Values
        .OrderBy(reading => reading.Site)
        .ThenBy(reading => reading.AssetType)
        .ThenBy(reading => reading.AssetId)
        .ThenBy(reading => reading.Metric)
        .ToArray();

    public SimulationStatus GetStatus() => new(
        IsRunning,
        _stepIndex,
        _currentTime,
        _scenario?.Id,
        _scenario?.AssetId,
        _scenario?.HorizonDays,
        GetSnapshot().Count);
}

public sealed record SimulationStatus(
    bool IsRunning,
    int StepIndex,
    DateTimeOffset SimulationTime,
    string? ActiveScenario,
    string? ScenarioAssetId,
    int? ScenarioHorizonDays,
    int ReadingCount);
