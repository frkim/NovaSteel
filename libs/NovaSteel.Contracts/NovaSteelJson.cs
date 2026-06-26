using System.Text.Json;
using System.Text.Json.Serialization;

namespace NovaSteel.Contracts;

/// <summary>Shared JSON options: camelCase, string enums, ISO-8601 UTC timestamps.</summary>
public static class NovaSteelJson
{
    public static readonly JsonSerializerOptions Options = new(JsonSerializerDefaults.Web)
    {
        Converters = { new JsonStringEnumConverter() },
        WriteIndented = false
    };
}
