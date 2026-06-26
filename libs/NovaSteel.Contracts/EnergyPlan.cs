namespace NovaSteel.Contracts;

/// <summary>Planning horizon for an energy-dispatch proposal.</summary>
public readonly record struct PlanningHorizon
{
    public DateTimeOffset From { get; init; }

    public DateTimeOffset To { get; init; }
}

/// <summary>Scheduled energy-intensive production job.</summary>
public readonly record struct ScheduledJob
{
    private readonly string? _jobId;

    public string JobId
    {
        get => _jobId ?? "";
        init => _jobId = value;
    }

    public DateTimeOffset SlotStart { get; init; }

    public DateTimeOffset SlotEnd { get; init; }

    public DateTimeOffset? Deadline { get; init; }

    public double EnergyMwh { get; init; }
}

/// <summary>Frozen per-site baseline used to compare an energy-dispatch plan.</summary>
public readonly record struct BaselineComparison
{
    public double BaselineEnergyPerTon { get; init; }

    public double BaselineCo2PerTon { get; init; }

    public double BaselineCostEur { get; init; }
}

/// <summary>Energy-dispatch output with expected energy, CO2, cost, baseline, and review status.</summary>
public readonly record struct EnergyPlan
{
    private readonly string? _energyPlanId;
    private readonly ScheduledJob[]? _scheduledJobs;
    private readonly string[]? _deadlineBreaches;

    public EnergyPlan()
    {
    }

    public string EnergyPlanId
    {
        get => _energyPlanId ?? "";
        init => _energyPlanId = value;
    }

    public Site Site { get; init; }

    public PlanningHorizon PlanningHorizon { get; init; }

    public ScheduledJob[] ScheduledJobs
    {
        get => _scheduledJobs ?? Array.Empty<ScheduledJob>();
        init => _scheduledJobs = value;
    }

    public double ExpectedEnergyPerTon { get; init; }

    public double ExpectedCo2PerTon { get; init; }

    public double ExpectedCostEur { get; init; }

    public BaselineComparison BaselineComparison { get; init; }

    public string[] DeadlineBreaches
    {
        get => _deadlineBreaches ?? Array.Empty<string>();
        init => _deadlineBreaches = value;
    }

    public Solver Solver { get; init; }

    public Origin Origin { get; init; } = Origin.Real;

    public EnergyPlanStatus Status { get; init; }
}
