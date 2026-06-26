# 1 · Agentic Work — Superpowers SDD Cycle

This folder applies the [obra/superpowers](https://github.com/obra/superpowers)
methodology to the **NovaSteel AI-Powered Steel Production Optimisation Platform**.
It turns the preliminary analysis into an executable, test-driven build.

> **Inputs (immutable source of truth):**
> [usecase.md](../usecase.md) +
> [0_preliminary analysis](../0_preliminary%20analysis/) —
> [0_architecture.md](../0_preliminary%20analysis/0_architecture.md),
> [1_azure_services.md](../0_preliminary%20analysis/1_azure_services.md),
> [2_mckensey_analysis.md](../0_preliminary%20analysis/2_mckensey_analysis.md),
> [3_c4model.md](../0_preliminary%20analysis/3_c4model.md).

## The Superpowers Workflow

| Phase | Skill | Output | Location |
| --- | --- | --- | --- |
| 1. Brainstorm | `brainstorming` | Decomposition + design, validated in sections | [00-decomposition.md](00-decomposition.md), [01-master-design.md](01-master-design.md) |
| 2. Spec | `brainstorming` (spec) | One spec per sub-project | [specs/](specs/) |
| 3. Plan | `writing-plans` | Bite-sized TDD task lists | [plans/](plans/) |
| 4. Implement | `subagent-driven-development` + `test-driven-development` | Working code (RED-GREEN-REFACTOR) | `apps/`, `services/`, `infrastructure/` |
| 5. Review | `requesting-code-review` | Severity-rated review per component | [reviews/](reviews/) |

## Core Principles (from Superpowers)

- **Test-Driven Development** — write the failing test first, always.
- **Systematic over ad-hoc** — process over guessing.
- **YAGNI / DRY** — build only what the KPIs require; no Azure-catalog tourism.
- **Evidence over claims** — verify before declaring success.
- **Scope guardrail** — only the **Fabric + Foundry** scoped service set from
  [1_azure_services.md](../0_preliminary%20analysis/1_azure_services.md) is in play.

## Decomposition — Five Sub-Projects

The platform is **not** a single spec. Per the brainstorming skill, it is
decomposed into independent sub-projects, each with its own spec → plan →
implementation → review cycle. Build order:

| # | Sub-project | KPI served | Stack |
| --- | --- | --- | --- |
| 0 | **Platform foundation** (contracts, telemetry schema, shared libs) | enabler | C#/.NET + Python |
| 1 | **Steel factory simulator** | feeds all workloads | C#/.NET |
| 2 | **Energy-dispatch optimisation agent** | −14% energy, −22% CO₂ | Python (solver) + C# API |
| 3 | **Furnace-lining RUL predictor** | 21-day warning | Python (physics-informed ML) |
| 4 | **GenAI knowledge-capture assistant** | preserve expertise | Python (AI) + Next.js UI |
| — | **Operations console** (Next.js) | cross-cutting surface | Next.js + C# BFF |

See [00-decomposition.md](00-decomposition.md) for the full rationale and
dependency graph.

## Status

| Sub-project | Spec | Plan | Implementation | Review |
| --- | :---: | :---: | :---: | :---: |
| 0 · Foundation | ✅ | ✅ | ✅ 8 C# + 2 Py tests | ✅ |
| 1 · Simulator | ✅ | ⏳ | ⏳ | ⏳ |
| 2 · Energy-dispatch agent | ✅ | ⏳ | ⏳ | ⏳ |
| 3 · RUL predictor | ✅ | ⏳ | ⏳ | ⏳ |
| 4 · Knowledge assistant | ✅ | ⏳ | ⏳ | ⏳ |
| 5 · Operations console | ✅ | ⏳ | ⏳ | ⏳ |

Legend: ⏳ pending · 🚧 in progress · ✅ done

