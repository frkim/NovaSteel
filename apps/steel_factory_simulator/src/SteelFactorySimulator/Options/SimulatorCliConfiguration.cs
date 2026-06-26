namespace SteelFactorySimulator.Options;

public static class SimulatorCliConfiguration
{
    public static Dictionary<string, string?> Parse(string[] args)
    {
        var values = new Dictionary<string, string?>(StringComparer.OrdinalIgnoreCase);
        for (var i = 0; i < args.Length; i++)
        {
            var arg = args[i];
            if (!arg.StartsWith("--", StringComparison.Ordinal))
            {
                continue;
            }

            var key = arg[2..];
            var value = i + 1 < args.Length && !args[i + 1].StartsWith("--", StringComparison.Ordinal)
                ? args[++i]
                : "true";

            switch (key.ToLowerInvariant())
            {
                case "transport":
                    values["Simulator:Transport"] = value;
                    break;
                case "replay":
                    values["Simulator:Replay:Scenario"] = value;
                    break;
                case "speed":
                    values["Simulator:Replay:SpeedMultiplier"] = value.TrimEnd('x', 'X');
                    break;
                case "seed":
                    values["Simulator:Seed"] = value;
                    break;
                case "autostart":
                    values["Simulator:AutoStart"] = value;
                    break;
            }
        }

        return values;
    }
}
