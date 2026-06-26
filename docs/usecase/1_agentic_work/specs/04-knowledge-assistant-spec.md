# Spec 04 — GenAI Knowledge-Capture Assistant

> **Sub-project 4** · KPI: preserve retiring-operator expertise · Stack: Python (`services/knowledge_assistant`)
> Source: [3_c4model.md](../../0_preliminary%20analysis/3_c4model.md) §3b, [usecase.md](../../usecase.md)

## Purpose

Turn operator interviews into a structured, searchable procedure library and
answer operator questions with **cited** retrieval-grounded responses, behind a
pluggable model interface (so it runs offline with fixtures, and on Foundry in prod).

## Requirements

| ID | Requirement | Acceptance |
| --- | --- | --- |
| K-1 | Accept an interview transcript (text; speech-to-text is upstream) and extract structured **procedure steps** (title, steps[], hazards[], equipment[]) | Extractor returns the schema; unit-tested on a fixture transcript |
| K-2 | Persist procedures to a local document store (JSON/Delta under `.data/`) | Round-trip read/write tested |
| K-3 | Build a retrieval index over procedures (embeddings or keyword fallback) | Query returns relevant procedure(s) |
| K-4 | Answer a question with a grounded response that **cites** the source procedure id(s) | Answer includes ≥1 citation; ungrounded → "I don't know" |
| K-5 | Abstract the LLM behind an `IChatModel` interface with a recorded-fixture implementation | Tests run with no network/API key |
| K-6 | Apply a safety filter that blocks unsafe/ungrounded output | Unsafe prompt is refused in test |
| K-7 | Expose `POST /ingest` (transcript → procedures) and `POST /ask` (question → cited answer) | FastAPI endpoint tests green |

## Out of scope

- No live audio capture / Azure Speech here — transcript is the input boundary.
- No production Foundry IQ wiring — the retrieval seam is local; Foundry is the adapter.

## Success criteria

- `pytest` covers extraction schema, store round-trip, retrieval relevance,
  citation enforcement, the "I don't know" path, and safety refusal — all with the
  fixture `IChatModel` (deterministic, offline).
