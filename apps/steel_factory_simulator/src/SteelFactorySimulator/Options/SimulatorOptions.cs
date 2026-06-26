namespace SteelFactorySimulator.Options;

public sealed class SimulatorOptions
{
    public string Transport { get; set; } = "InMemory";
    public int Seed { get; set; } = 20260623;
    public bool AutoStart { get; set; }
    public int IntervalMilliseconds { get; set; } = 1000;
    public int StepMinutes { get; set; } = 5;
    public string SourceId { get; set; } = "sim:steel_factory_simulator@v1";
    public ReplayOptions? Replay { get; set; }
}

public sealed class ReplayOptions
{
    public string Scenario { get; set; } = "";
    public double SpeedMultiplier { get; set; } = 1;
    public int HorizonDays { get; set; } = 30;
}
