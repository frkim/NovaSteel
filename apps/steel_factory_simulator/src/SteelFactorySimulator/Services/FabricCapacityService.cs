using System.Net.Http.Headers;
using System.Text.Json;
using Azure.Core;
using Azure.Identity;
using Microsoft.Extensions.Options;
using SteelFactorySimulator.Options;

namespace SteelFactorySimulator.Services;

/// <summary>Current state of the Fabric capacity. `State` is the raw ARM value
/// (Active / Paused / Pausing / Resuming / Unknown / NotConfigured).</summary>
public sealed record FabricStatus(string State, bool Configured);

/// <summary>Reads and controls (pause/resume) the Microsoft Fabric capacity via ARM,
/// authenticating with the app's managed identity (DefaultAzureCredential).</summary>
public sealed class FabricCapacityService
{
    private const string Arm = "https://management.azure.com";
    private static readonly string[] Scope = ["https://management.azure.com/.default"];

    private readonly HttpClient _http;
    private readonly FabricOptions _options;
    private readonly TokenCredential _credential;
    private readonly ILogger<FabricCapacityService> _logger;

    public FabricCapacityService(HttpClient http, IOptions<FabricOptions> options, ILogger<FabricCapacityService> logger)
    {
        _http = http;
        _options = options.Value;
        _logger = logger;
        _credential = new DefaultAzureCredential();
    }

    public bool Configured => _options.IsConfigured;

    public async Task<FabricStatus> GetStatusAsync(CancellationToken ct = default)
    {
        if (!_options.IsConfigured)
        {
            return new FabricStatus("NotConfigured", false);
        }

        try
        {
            using var req = new HttpRequestMessage(
                HttpMethod.Get, $"{Arm}{_options.ResourceId}?api-version={_options.ApiVersion}");
            await AuthorizeAsync(req, ct);
            using var resp = await _http.SendAsync(req, ct);
            if (!resp.IsSuccessStatusCode)
            {
                _logger.LogWarning("Fabric status query returned {Status}", resp.StatusCode);
                return new FabricStatus("Unknown", true);
            }

            await using var stream = await resp.Content.ReadAsStreamAsync(ct);
            using var doc = await JsonDocument.ParseAsync(stream, cancellationToken: ct);
            var state = doc.RootElement.GetProperty("properties").GetProperty("state").GetString() ?? "Unknown";
            return new FabricStatus(state, true);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Fabric status query failed");
            return new FabricStatus("Unknown", true);
        }
    }

    public Task ResumeAsync(CancellationToken ct = default) => ActionAsync("resume", ct);

    public Task SuspendAsync(CancellationToken ct = default) => ActionAsync("suspend", ct);

    private async Task ActionAsync(string action, CancellationToken ct)
    {
        if (!_options.IsConfigured)
        {
            throw new InvalidOperationException("Fabric capacity is not configured.");
        }

        using var req = new HttpRequestMessage(
            HttpMethod.Post, $"{Arm}{_options.ResourceId}/{action}?api-version={_options.ApiVersion}");
        await AuthorizeAsync(req, ct);
        using var resp = await _http.SendAsync(req, ct);
        resp.EnsureSuccessStatusCode();
        _logger.LogInformation("Fabric capacity {Action} requested", action);
    }

    private async Task AuthorizeAsync(HttpRequestMessage req, CancellationToken ct)
    {
        var token = await _credential.GetTokenAsync(new TokenRequestContext(Scope), ct);
        req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token.Token);
    }
}
