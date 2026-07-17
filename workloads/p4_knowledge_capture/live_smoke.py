"""Live smoke test of the knowledge assistant against the DEPLOYED gpt-5.

Requires: `az login` (Cognitive Services OpenAI User on aif-novastee-dev-ox26fi) and
`pip install azure-identity requests`. Proves the end-to-end grounded/cited/decline
behaviour on real gpt-5 — not part of the deterministic unit suite.

Run:  python workloads/p4_knowledge_capture/live_smoke.py
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from workloads.p4_knowledge_capture.assistant import KnowledgeAssistant
from workloads.p4_knowledge_capture.foundry_client import FoundryClient
from workloads.p4_knowledge_capture.knowledge_library import load_library


def main() -> int:
    client = FoundryClient()
    assistant = KnowledgeAssistant(client, load_library())

    grounded_q = "When should we schedule a blast furnace lining relining?"
    ungrounded_q = "What is the boiling point of helium on Jupiter?"

    print("== Grounded question ==")
    a1 = assistant.ask(grounded_q)
    print("declined:", a1.declined)
    print("answer:", a1.text)
    print("citations:", a1.used_sources)
    assert not a1.declined, "expected a grounded, cited answer"
    assert a1.recommendation and a1.recommendation.citations, "expected citations (SC-008)"

    print("\n== Ungrounded question (must decline, not fabricate) ==")
    a2 = assistant.ask(ungrounded_q)
    print("declined:", a2.declined)
    print("answer:", a2.text)
    assert a2.declined, "expected a decline for an ungrounded question (FR-014)"

    print("\nLIVE SMOKE OK: grounded+cited answer and correct decline against gpt-5.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
