namespace NovaSteel.Contracts;

/// <summary>Day-ahead energy market signal that drives the energy-dispatch agent.</summary>
public readonly record struct MarketSignal(
    Site Market,
    DateTimeOffset Timestamp,
    double SpotPriceEurMwh,
    double GridCarbonGramsPerKwh);
