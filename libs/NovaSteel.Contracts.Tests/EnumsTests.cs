using FluentAssertions;
using NovaSteel.Contracts;
using Xunit;

namespace NovaSteel.Contracts.Tests;

public class EnumsTests
{
    [Fact]
    public void Unknown_metric_falls_back_to_Unknown()
    {
        EnumParse.OrFallback("NotARealMetric", Metric.Unknown).Should().Be(Metric.Unknown);
    }

    [Fact]
    public void Known_site_parses_case_insensitively()
    {
        EnumParse.OrFallback("de", Site.LU).Should().Be(Site.DE);
    }

    [Fact]
    public void Null_value_falls_back()
    {
        EnumParse.OrFallback(null, AssetType.Unknown).Should().Be(AssetType.Unknown);
    }

    [Fact]
    public void Origin_parses_expected_schema_casing()
    {
        EnumParse.OrFallback("Synthetic", Origin.Real).Should().Be(Origin.Synthetic);
    }
}
