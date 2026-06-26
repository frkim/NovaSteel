namespace SteelFactorySimulator.Simulation;

public sealed record ActiveScenario(string Id, string Kind, string AssetId, DateTimeOffset StartedAt, int HorizonDays)
{
    public double ProgressAt(DateTimeOffset timestamp)
    {
        if (HorizonDays <= 0)
        {
            return 1;
        }

        var progress = (timestamp - StartedAt).TotalDays / HorizonDays;
        return Math.Clamp(progress, 0, 1);
    }
}

public sealed record DegradingFurnaceRequest(string? AssetId, int HorizonDays = 30);
