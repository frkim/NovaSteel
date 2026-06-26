using System.IO;
using System.Text.Json;
using System.Text.Json.Nodes;
using FluentAssertions;
using NovaSteel.Contracts;
using Xunit;

namespace NovaSteel.Contracts.Tests;

public class EntityContractTests
{
    private static string FixturePath(string name)
    {
        var dir = AppContext.BaseDirectory;
        while (dir is not null && !Directory.Exists(Path.Combine(dir, "libs", "fixtures")))
            dir = Directory.GetParent(dir)?.FullName;

        if (dir is null)
            throw new DirectoryNotFoundException("Could not locate libs/fixtures from test output.");

        return Path.Combine(dir, "libs", "fixtures", name);
    }

    private static List<T> ReadJsonLines<T>(string name)
    {
        return File.ReadLines(FixturePath(name))
            .Where(line => !string.IsNullOrWhiteSpace(line))
            .Select(line => JsonSerializer.Deserialize<T>(line, NovaSteelJson.Options)
                ?? throw new InvalidDataException($"Could not deserialize fixture line in {name}."))
            .ToList();
    }

    private static void AssertJsonRoundTrip<T>(T value)
    {
        var json = JsonSerializer.Serialize(value, NovaSteelJson.Options);
        var back = JsonSerializer.Deserialize<T>(json, NovaSteelJson.Options);
        JsonSerializer.Serialize(back, NovaSteelJson.Options).Should().Be(json);
    }

    [Fact]
    public void Prediction_round_trips_and_uses_string_enums()
    {
        var prediction = new Prediction
        {
            PredictionId = "11111111-1111-4111-8111-111111111111",
            Pillar = Pillar.Maintenance,
            Site = Site.LU,
            AssetId = "LU-BF1",
            HeatId = null,
            Kind = PredictionKind.LiningFailureRisk,
            TimeToFailureDays = 28,
            PredictedAt = DateTimeOffset.Parse("2026-06-21T10:05:00Z"),
            Confidence = 0.91,
            Evidence =
            [
                new EvidenceItem { Metric = "ThermocoupleTemp", Value = 1487.2, Weight = 0.58, Note = "Thermal rise" }
            ],
            ModelVersion = "fabric-mlflow:rul-lining:7",
            InputWindowRef = "onelake://silver/features/lining/LU-BF1/2026-06-21T10:00:00Z",
            Origin = Origin.Synthetic,
            Status = PredictionStatus.Raised
        };

        var json = JsonSerializer.Serialize(prediction, NovaSteelJson.Options);
        json.Should().Contain("\"kind\":\"LiningFailureRisk\"").And.Contain("\"status\":\"Raised\"");
        json.Should().NotContain("\"kind\":0");
        AssertJsonRoundTrip(prediction);
    }

    [Fact]
    public void Recommendation_round_trips_and_uses_string_enums()
    {
        var recommendation = new Recommendation
        {
            RecommendationId = "22222222-2222-4222-8222-222222222222",
            Pillar = RecommendationPillar.Knowledge,
            Site = Site.LU,
            Summary = "Use documented inspection procedure.",
            Rationale = "Grounded in approved source.",
            ExpectedImpact = JsonNode.Parse("""{"operatorTimeSavedMinutes":18.0}""")!.AsObject(),
            Citations =
            [
                new Citation { SourceId = "knowledge:operator-interview:LU-2026-06", Title = "Interview", Locator = "00:14:32" }
            ],
            Confidence = 0.82,
            ContentSafetyPassed = true,
            ConflictsWith = null,
            Status = RecommendationStatus.Approved
        };

        var json = JsonSerializer.Serialize(recommendation, NovaSteelJson.Options);
        json.Should().Contain("\"pillar\":\"Knowledge\"").And.Contain("\"status\":\"Approved\"");
        json.Should().NotContain("\"status\":0");
        AssertJsonRoundTrip(recommendation);
    }

    [Fact]
    public void EnergyPlan_round_trips_and_uses_string_enums()
    {
        var plan = new EnergyPlan
        {
            EnergyPlanId = "33333333-3333-4333-8333-333333333333",
            Site = Site.DE,
            PlanningHorizon = new PlanningHorizon
            {
                From = DateTimeOffset.Parse("2026-06-22T00:00:00Z"),
                To = DateTimeOffset.Parse("2026-06-23T00:00:00Z")
            },
            ScheduledJobs =
            [
                new ScheduledJob
                {
                    JobId = "DE-ROLL-20260622-01",
                    SlotStart = DateTimeOffset.Parse("2026-06-22T02:00:00Z"),
                    SlotEnd = DateTimeOffset.Parse("2026-06-22T04:00:00Z"),
                    Deadline = DateTimeOffset.Parse("2026-06-22T08:00:00Z"),
                    EnergyMwh = 42.5
                }
            ],
            ExpectedEnergyPerTon = 4.3,
            ExpectedCo2PerTon = 0.71,
            ExpectedCostEur = 18500,
            BaselineComparison = new BaselineComparison
            {
                BaselineEnergyPerTon = 5.0,
                BaselineCo2PerTon = 0.91,
                BaselineCostEur = 22000
            },
            DeadlineBreaches = [],
            Solver = Solver.Milp,
            Origin = Origin.Real,
            Status = EnergyPlanStatus.Proposed
        };

        var json = JsonSerializer.Serialize(plan, NovaSteelJson.Options);
        json.Should().Contain("\"solver\":\"Milp\"").And.Contain("\"status\":\"Proposed\"");
        json.Should().NotContain("\"solver\":0");
        AssertJsonRoundTrip(plan);
    }

    [Fact]
    public void HumanDecision_round_trips_and_uses_string_enums()
    {
        var decision = new HumanDecision
        {
            DecisionId = "44444444-4444-4444-8444-444444444444",
            SubjectType = DecisionSubjectType.Prediction,
            SubjectId = "11111111-1111-4111-8111-111111111111",
            Site = Site.LU,
            Decision = DecisionType.Confirm,
            ReviewerId = "entra:maintenance-engineer-lu-01",
            ReviewerRole = ReviewerRole.Maintenance,
            Rationale = "Actionable lead time.",
            DecidedAt = DateTimeOffset.Parse("2026-06-21T10:20:00Z"),
            ResultingWorkOrderId = null
        };

        var json = JsonSerializer.Serialize(decision, NovaSteelJson.Options);
        json.Should().Contain("\"subjectType\":\"Prediction\"").And.Contain("\"decision\":\"Confirm\"");
        json.Should().NotContain("\"decision\":0");
        AssertJsonRoundTrip(decision);
    }

    [Fact]
    public void AuditRecord_round_trips_and_uses_string_enums()
    {
        var audit = new AuditRecord
        {
            AuditId = "55555555-5555-4555-8555-555555555555",
            SubjectType = AuditSubjectType.Prediction,
            SubjectId = "11111111-1111-4111-8111-111111111111",
            Site = Site.LU,
            Action = "PredictionRaised",
            InputsRef = ["fixture://telemetry_reading.json#2"],
            ModelOrLogicVersion = "fabric-mlflow:rul-lining:7",
            Output = JsonNode.Parse("""{"predictionId":"11111111-1111-4111-8111-111111111111","status":"Raised"}""")!.AsObject(),
            ReviewerId = null,
            Rationale = null,
            Timestamp = DateTimeOffset.Parse("2026-06-21T10:05:01Z"),
            Origin = Origin.Synthetic,
            RetentionClass = RetentionClass.PredictionDecisionAudit
        };

        var json = JsonSerializer.Serialize(audit, NovaSteelJson.Options);
        json.Should().Contain("\"subjectType\":\"Prediction\"").And.Contain("\"retentionClass\":\"PredictionDecisionAudit\"");
        json.Should().NotContain("\"retentionClass\":0");
        AssertJsonRoundTrip(audit);
    }

    [Fact]
    public void New_entity_fixtures_deserialise_and_preserve_contract_values()
    {
        var prediction = ReadJsonLines<Prediction>("prediction.json").Single();
        prediction.Pillar.Should().Be(Pillar.Maintenance);
        prediction.Kind.Should().Be(PredictionKind.LiningFailureRisk);
        prediction.TimeToFailureDays.Should().BeGreaterThanOrEqualTo(21);
        prediction.Status.Should().Be(PredictionStatus.Raised);
        prediction.Origin.Should().Be(Origin.Synthetic);

        ReadJsonLines<Recommendation>("recommendation.json").Single().Status.Should().Be(RecommendationStatus.Approved);
        ReadJsonLines<EnergyPlan>("energy_plan.json").Single().Solver.Should().Be(Solver.Milp);
        ReadJsonLines<HumanDecision>("human_decision.json").Single().ReviewerRole.Should().Be(ReviewerRole.Maintenance);

        var audit = ReadJsonLines<AuditRecord>("audit_record.json").Single();
        audit.Origin.Should().Be(Origin.Synthetic);
        audit.InputsRef.Should().Contain("fixture://telemetry_reading.json#2");
    }

    [Fact]
    public void Required_string_and_array_fields_never_deserialise_to_null()
    {
        JsonSerializer.Deserialize<Prediction>("{}", NovaSteelJson.Options).PredictionId.Should().Be("");
        JsonSerializer.Deserialize<Prediction>("{}", NovaSteelJson.Options).ModelVersion.Should().Be("");
        JsonSerializer.Deserialize<Prediction>("{}", NovaSteelJson.Options).Evidence.Should().NotBeNull();
        JsonSerializer.Deserialize<EvidenceItem>("{}", NovaSteelJson.Options).Metric.Should().Be("");

        JsonSerializer.Deserialize<Recommendation>("{}", NovaSteelJson.Options).RecommendationId.Should().Be("");
        JsonSerializer.Deserialize<Recommendation>("{}", NovaSteelJson.Options).Summary.Should().Be("");
        JsonSerializer.Deserialize<Recommendation>("{}", NovaSteelJson.Options).Rationale.Should().Be("");
        JsonSerializer.Deserialize<Citation>("{}", NovaSteelJson.Options).SourceId.Should().Be("");
        JsonSerializer.Deserialize<Citation>("{}", NovaSteelJson.Options).Title.Should().Be("");

        JsonSerializer.Deserialize<EnergyPlan>("{}", NovaSteelJson.Options).EnergyPlanId.Should().Be("");
        JsonSerializer.Deserialize<EnergyPlan>("{}", NovaSteelJson.Options).ScheduledJobs.Should().NotBeNull();
        JsonSerializer.Deserialize<EnergyPlan>("{}", NovaSteelJson.Options).DeadlineBreaches.Should().NotBeNull();
        JsonSerializer.Deserialize<ScheduledJob>("{}", NovaSteelJson.Options).JobId.Should().Be("");

        JsonSerializer.Deserialize<HumanDecision>("{}", NovaSteelJson.Options).DecisionId.Should().Be("");
        JsonSerializer.Deserialize<HumanDecision>("{}", NovaSteelJson.Options).SubjectId.Should().Be("");
        JsonSerializer.Deserialize<HumanDecision>("{}", NovaSteelJson.Options).ReviewerId.Should().Be("");

        var audit = JsonSerializer.Deserialize<AuditRecord>("{}", NovaSteelJson.Options);
        audit.AuditId.Should().Be("");
        audit.SubjectId.Should().Be("");
        audit.Action.Should().Be("");
        audit.InputsRef.Should().NotBeNull();
        audit.ModelOrLogicVersion.Should().Be("");
        audit.Output.Should().NotBeNull();
    }
}
