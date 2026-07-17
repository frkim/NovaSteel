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
    private readonly ConcurrentDictionary<string, SensorSeries> _history = new(StringComparer.OrdinalIgnoreCase);
    private const int MaxHistoryPointsPerSensor = 1000;
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
                var key = $"{reading.AssetId}:{reading.Metric}";
                _latest[key] = reading;
                _history.GetOrAdd(key, _ => new SensorSeries(MaxHistoryPointsPerSensor)).Add(reading);
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

    /// <summary>Time-ordered history for a single sensor (asset + metric), for charting.</summary>
    public IReadOnlyList<SensorHistoryPoint> GetHistory(string assetId, string metric)
    {
        var key = $"{assetId}:{metric}";
        return _history.TryGetValue(key, out var series)
            ? series.Snapshot()
            : Array.Empty<SensorHistoryPoint>();
    }

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

/// <summary>A single point in a sensor's charted time series.</summary>
public sealed record SensorHistoryPoint(
    DateTimeOffset Timestamp,
    double Value,
    string Unit,
    Quality Quality,
    Origin Origin);

/// <summary>Thread-safe bounded ring buffer of readings for one sensor.</summary>
internal sealed class SensorSeries(int capacity)
{
    private readonly object _gate = new();
    private readonly Queue<TelemetryReading> _points = new();

    public void Add(TelemetryReading reading)
    {
        lock (_gate)
        {
            _points.Enqueue(reading);
            while (_points.Count > capacity)
            {
                _points.Dequeue();
            }
        }
    }

    public IReadOnlyList<SensorHistoryPoint> Snapshot()
    {
        lock (_gate)
        {
            return _points
                .OrderBy(reading => reading.Timestamp)
                .Select(reading => new SensorHistoryPoint(
                    reading.Timestamp,
                    reading.Value,
                    reading.Unit,
                    reading.Quality,
                    reading.Origin))
                .ToArray();
        }
    }
}
