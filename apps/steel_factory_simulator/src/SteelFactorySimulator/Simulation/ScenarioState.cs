namespace SteelFactorySimulator.Simulation;

public sealed class ScenarioState
{
    public string? ActiveScenarioId { get; private set; }

    public void Set(ActiveScenario scenario) => ActiveScenarioId = scenario.Id;

    public void Clear() => ActiveScenarioId = null;
}
