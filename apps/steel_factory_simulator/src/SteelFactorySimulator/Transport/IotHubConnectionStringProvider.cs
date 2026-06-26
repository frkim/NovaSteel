using Azure.Identity;
using Azure.Security.KeyVault.Secrets;
using Microsoft.Extensions.Options;
using SteelFactorySimulator.Options;

namespace SteelFactorySimulator.Transport;

public sealed class IotHubConnectionStringProvider(IOptions<IotHubOptions> options)
{
    private readonly IotHubOptions _options = options.Value;

    public async ValueTask<string> GetConnectionStringAsync(CancellationToken cancellationToken)
    {
        if (!string.IsNullOrWhiteSpace(_options.ConnectionString))
        {
            return _options.ConnectionString;
        }

        if (!string.IsNullOrWhiteSpace(_options.KeyVaultUri) && !string.IsNullOrWhiteSpace(_options.ConnectionStringSecretName))
        {
            var client = new SecretClient(new Uri(_options.KeyVaultUri), new DefaultAzureCredential());
            var secret = await client.GetSecretAsync(_options.ConnectionStringSecretName, cancellationToken: cancellationToken);
            return secret.Value.Value;
        }

        throw new InvalidOperationException(
            "IoT Hub transport is enabled, but no connection string or Key Vault secret was configured. " +
            "Set Simulator:IotHub:ConnectionString for local testing or Simulator:IotHub:KeyVaultUri and " +
            "Simulator:IotHub:ConnectionStringSecretName for managed identity secret retrieval.");
    }
}
