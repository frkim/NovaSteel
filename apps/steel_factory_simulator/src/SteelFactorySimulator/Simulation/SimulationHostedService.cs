using Microsoft.Extensions.Options;
using SteelFactorySimulator.Options;

namespace SteelFactorySimulator.Simulation;

public sealed class SimulationHostedService(
    SimulationController controller,
    IOptions<SimulatorOptions> options,
    ILogger<SimulationHostedService> logger) : BackgroundService
{
    private readonly SimulatorOptions _options = options.Value;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var interval = TimeSpan.FromMilliseconds(Math.Max(_options.IntervalMilliseconds, 100));
        logger.LogInformation("Steel factory simulator loop initialized with {IntervalMs} ms interval", interval.TotalMilliseconds);

        while (!stoppingToken.IsCancellationRequested)
        {
            await controller.StepAsync(stoppingToken);
            await Task.Delay(interval, stoppingToken);
        }
    }
}
