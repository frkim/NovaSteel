using Microsoft.Extensions.Options;
using NovaSteel.Contracts;
using SteelFactorySimulator.Options;
using SteelFactorySimulator.Services;
using SteelFactorySimulator.Simulation;
using SteelFactorySimulator.Transport;

var cliConfiguration = SimulatorCliConfiguration.Parse(args);
var builder = WebApplication.CreateBuilder(args);
builder.Configuration.AddInMemoryCollection(cliConfiguration);

builder.Services.AddRazorPages();
builder.Services.Configure<SimulatorOptions>(builder.Configuration.GetSection("Simulator"));
builder.Services.Configure<IotHubOptions>(builder.Configuration.GetSection("Simulator:IotHub"));
builder.Services.Configure<FabricOptions>(builder.Configuration.GetSection("Fabric"));
builder.Services.AddHttpClient<FabricCapacityService>();
builder.Services.AddSingleton<InMemoryTelemetryChannel>();
builder.Services.AddSingleton<ScenarioState>();
builder.Services.AddSingleton<SensorReadingEngine>();
builder.Services.AddSingleton<SimulationController>();
builder.Services.AddHostedService<SimulationHostedService>();
builder.Services.AddSingleton<ITelemetrySink>(sp =>
{
    var options = sp.GetRequiredService<IOptions<SimulatorOptions>>().Value;
    return options.Transport.Equals("iothub", StringComparison.OrdinalIgnoreCase)
        ? ActivatorUtilities.CreateInstance<IotHubTelemetrySink>(sp)
        : sp.GetRequiredService<InMemoryTelemetryChannel>();
});

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
}

app.UseStaticFiles();
app.UseRouting();

app.MapRazorPages();
app.MapGet("/api/status", (SimulationController controller) => Results.Json(controller.GetStatus(), NovaSteelJson.Options));
app.MapGet("/api/readings", (SimulationController controller) => Results.Json(controller.GetSnapshot(), NovaSteelJson.Options));
app.MapGet("/api/history", (string assetId, string metric, SimulationController controller) =>
    Results.Json(controller.GetHistory(assetId ?? string.Empty, metric ?? string.Empty), NovaSteelJson.Options));
app.MapPost("/api/simulation/start", (SimulationController controller) =>
{
    controller.Start();
    return Results.Json(controller.GetStatus(), NovaSteelJson.Options);
});
app.MapPost("/api/simulation/stop", (SimulationController controller) =>
{
    controller.Stop();
    return Results.Json(controller.GetStatus(), NovaSteelJson.Options);
});
app.MapPost("/api/scenarios/degrading-furnace", (DegradingFurnaceRequest request, SimulationController controller) =>
{
    controller.StartDegradingFurnace(
        string.IsNullOrWhiteSpace(request.AssetId) ? "LU-BF1" : request.AssetId,
        request.HorizonDays <= 0 ? 30 : request.HorizonDays);
    controller.Start();
    return Results.Json(controller.GetStatus(), NovaSteelJson.Options);
});
app.MapPost("/api/scenarios/clear", (SimulationController controller) =>
{
    controller.ClearScenario();
    return Results.Json(controller.GetStatus(), NovaSteelJson.Options);
});

app.MapGet("/api/fabric/status", async (FabricCapacityService fabric, CancellationToken ct) =>
    Results.Json(await fabric.GetStatusAsync(ct), NovaSteelJson.Options));
app.MapPost("/api/fabric/resume", async (FabricCapacityService fabric, CancellationToken ct) =>
{
    try
    {
        await fabric.ResumeAsync(ct);
        return Results.Json(await fabric.GetStatusAsync(ct), NovaSteelJson.Options);
    }
    catch (Exception ex)
    {
        return Results.Problem(ex.Message, statusCode: 502, title: "Fabric resume failed");
    }
});
app.MapPost("/api/fabric/pause", async (FabricCapacityService fabric, CancellationToken ct) =>
{
    try
    {
        await fabric.SuspendAsync(ct);
        return Results.Json(await fabric.GetStatusAsync(ct), NovaSteelJson.Options);
    }
    catch (Exception ex)
    {
        return Results.Problem(ex.Message, statusCode: 502, title: "Fabric pause failed");
    }
});

var controller = app.Services.GetRequiredService<SimulationController>();
var options = app.Services.GetRequiredService<IOptions<SimulatorOptions>>().Value;
if (options.Replay is { Scenario.Length: > 0 } replay)
{
    if (replay.Scenario.StartsWith("degrading-furnace-", StringComparison.OrdinalIgnoreCase))
    {
        controller.StartDegradingFurnace(replay.Scenario["degrading-furnace-".Length..], replay.HorizonDays);
    }

    controller.Start();
}
else if (options.AutoStart)
{
    controller.Start();
}

app.Run();

public static partial class Program;
