# Spec 05 — Operations Console

> **Sub-project 5** · cross-cutting human surface · Stack: Next.js + C# BFF (`apps/operations_console`)
> Source: [01-master-design.md](../01-master-design.md) §B, [3_c4model.md](../../0_preliminary%20analysis/3_c4model.md) §1

## Purpose

A single operator/engineer/exec surface: live KPI dashboard, furnace alert feed,
energy-dispatch plan review + approval, and the knowledge assistant chat.

## Requirements

| ID | Requirement | Acceptance |
| --- | --- | --- |
| U-1 | C# BFF aggregates outputs from sub-projects 2·3·4 behind one API | BFF contract tests green |
| U-2 | KPI dashboard page shows energy €, tCO₂, RUL/alerts, yield (from workload outputs) | Component renders with mocked data |
| U-3 | Alert feed lists furnace "fail ≤21d" alerts with confidence and drivers | Renders RUL output |
| U-4 | Dispatch review page shows the plan + savings and an Approve action (human-in-loop) | Approve calls BFF → energy agent |
| U-5 | Assistant chat page sends questions to the knowledge service and renders cited answers | Citations shown |
| U-6 | The UI never actuates equipment — all actions are recommendations/approvals | No control endpoints exist |

## Out of scope

- No production Entra ID auth wiring in the first cut (local dev auth stub; Entra is the prod adapter).
- No mobile/responsive polish beyond a usable desktop layout.

## Success criteria

- `npm test` (component tests) green for the four pages with mocked BFF data.
- `dotnet test` green for the BFF aggregation + approval forwarding.
