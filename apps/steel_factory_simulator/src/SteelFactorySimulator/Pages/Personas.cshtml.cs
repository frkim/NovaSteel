using Microsoft.AspNetCore.Mvc.RazorPages;

namespace SteelFactorySimulator.Pages;

/// <summary>
/// Persona-driven POC walkthrough. Personas are grounded in the NovaSteel reviewer roles
/// (NovaSteel.Contracts ReviewerRole), the four pillars (P1–P4) and the constitution.
/// </summary>
public sealed class PersonasModel : PageModel
{
    public IReadOnlyList<Persona> Personas { get; } = BuildPersonas();

    public void OnGet()
    {
    }

    private static IReadOnlyList<Persona> BuildPersonas() =>
    [
        new Persona(
            Key: "operator",
            Name: "Furnace Operator",
            Role: "Operator",
            Icon: "🏭",
            Objective: "Run the furnaces safely and stably; act only on approved recommendations and never run to failure.",
            Pillar: "Live telemetry + P4 knowledge assistant",
            InThePoc:
            [
                "Watches the live device→cloud sensor table (Home) with quality + freshness flags.",
                "Asks the grounded knowledge assistant (P4) and gets cited, decline-on-no-source answers.",
                "Receives Proposed recommendations to execute only after a reviewer approves them."
            ],
            Guarantees:
            [
                "Human-in-the-loop: the platform never actuates plant equipment (Principle I).",
                "One-way OT→IT: telemetry flows out only; no control path back (Principle IV)."
            ],
            SuccessCriteria: "Stale/missing telemetry is flagged, never shown as current (Principle VI)."),

        new Persona(
            Key: "maintenance",
            Name: "Maintenance Engineer",
            Role: "Maintenance",
            Icon: "🛠️",
            Objective: "Prevent unplanned furnace-lining breaches (~€8M each) by relining during planned downtime.",
            Pillar: "P1 — Predictive maintenance (RUL)",
            InThePoc:
            [
                "Reviews P1 LiningFailureRisk predictions with per-metric evidence, confidence and lead time.",
                "Confirms a prediction → a proposed work order is raised (never auto-dispatched to EAM).",
                "Escalated (<21-day) cases are flagged High priority for expedited review."
            ],
            Guarantees:
            [
                "Every prediction is auditable (inputs, model version, reviewer, rationale) — Principle II.",
                "Confirm/Reject decisions are recorded in an immutable, append-only audit log."
            ],
            SuccessCriteria: "SC-003 — ≥ 21-day advance warning before predicted lining failure."),

        new Persona(
            Key: "energy",
            Name: "Energy Manager",
            Role: "Energy",
            Icon: "⚡",
            Objective: "Cut energy cost and CO₂ by shifting flexible heats to cheap, low-carbon windows — without missing deadlines.",
            Pillar: "P2 — Energy-dispatch optimization",
            InThePoc:
            [
                "Reviews a Proposed EnergyPlan with baseline comparison and a grounded GenAI explanation.",
                "Sees energy/CO₂/cost per ton vs the uncoordinated baseline, plus any deadline breaches.",
                "Approves or Adjusts the plan; nothing touches the grid or furnaces automatically."
            ],
            Guarantees:
            [
                "Explanations carry evidence + uncertainty and pass Content Safety (Principle VI).",
                "Infeasible batches are flagged, never silently forced; plan stays Proposed (Principle I)."
            ],
            SuccessCriteria: "SC-001 −14% energy & SC-002 −22% CO₂ (POC achieves ~17% / ~52%)."),

        new Persona(
            Key: "quality",
            Name: "Quality Metallurgist",
            Role: "Quality",
            Icon: "🔬",
            Objective: "Lift high-grade automotive yield and make sure no out-of-spec coil is shipped.",
            Pillar: "P3 — Quality prediction & SPC",
            InThePoc:
            [
                "Reviews per-heat QualityOutcome predictions with sulphur/inclusion/tapping-temp evidence.",
                "Gets SPC drift alerts (3-sigma / Western Electric) before the grade band is breached.",
                "Approves a reviewable trim action for recoverable heats; predicted-vs-actual is linked."
            ],
            Guarantees:
            [
                "Root-cause narratives are grounded in the heat's evidence and cited (Principle VI).",
                "Recommendations are Proposed for review; non-recoverable heats get no auto-fix."
            ],
            SuccessCriteria: "SC-004 — +8% high-grade yield (POC lifts 0.65 → 0.95)."),

        new Persona(
            Key: "executive",
            Name: "Executive / ESG Lead",
            Role: "ExecutiveEsg",
            Icon: "📊",
            Objective: "Track cost, energy and ESG performance against a stable baseline and meet regulatory reporting.",
            Pillar: "Power BI Direct Lake + KPI baseline + EU-ETS",
            InThePoc:
            [
                "Views energy/ton, CO₂/ton, cost/ton and high-grade yield vs the frozen 12-month baseline.",
                "Sees the verified EU-ETS annual emissions roll-up (synthetic data excluded).",
                "Monitors SC target gauges across the four pillars per site."
            ],
            Guarantees:
            [
                "Real vs synthetic data is strictly separated; synthetic never counts in a real KPI (Principle IX).",
                "Per-site row-level security — no cross-site data bleed (Principle VII)."
            ],
            SuccessCriteria: "Frozen, normalized KPI baseline; verified EU-ETS tCO₂ report."),

        new Persona(
            Key: "compliance",
            Name: "Compliance / Data Protection Officer",
            Role: "ComplianceDpo",
            Icon: "🛡️",
            Objective: "Guarantee end-to-end traceability, GDPR compliance and EU data residency.",
            Pillar: "Governance — Purview / audit / GDPR / policy",
            InThePoc:
            [
                "Traces any output back through model version, inputs, reviewer and rationale (Purview lineage).",
                "Runs the GDPR erasure flow: raw personal content erased, audit trail retained.",
                "Verifies EU-region residency is enforced as policy-as-code with zero egress."
            ],
            Guarantees:
            [
                "Audit records are immutable and exempt from erasure; history is append-only (Principle II).",
                "All data stored/processed in EU regions; access is least-privilege by persona (Principles III/VII)."
            ],
            SuccessCriteria: "Immutable audit trail; GDPR-erasable raw content; EU residency enforced.")
    ];
}

public sealed record Persona(
    string Key,
    string Name,
    string Role,
    string Icon,
    string Objective,
    string Pillar,
    string[] InThePoc,
    string[] Guarantees,
    string SuccessCriteria);
