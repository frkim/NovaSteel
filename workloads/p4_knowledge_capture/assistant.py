"""GenAI operator knowledge assistant (P4) — grounded, cited, decline-on-no-source.

Pipeline: retrieve procedures -> ground gpt-5 -> enforce citations & Content Safety ->
return a Knowledge `Recommendation` for HUMAN REVIEW (never auto-authoritative).

Constitution gates enforced here:
- VI: answers are grounded with citations; the model MUST decline (not fabricate) when
  no source supports the question (FR-014, SC-008).
- I:  the returned Recommendation is `Proposed` and requires human review before it
  becomes part of the authoritative library — the assistant never self-approves.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field

from novasteel_core.models import (
    Citation,
    Recommendation,
    RecommendationPillar,
    RecommendationStatus,
)

from .foundry_client import ChatClient
from .knowledge_library import KnowledgeItem
from .retrieval import retrieve

INSUFFICIENT = "INSUFFICIENT_CONTEXT"

SYSTEM_PROMPT = (
    "You are the NovaSteel operator knowledge assistant. Answer the question ONLY using the "
    "numbered SOURCES provided. Cite every claim inline using the source tags like [S1], [S2]. "
    f"If the SOURCES do not contain the answer, reply with exactly this token and nothing else: {INSUFFICIENT}. "
    "Never invent procedures, numbers, or safety guidance. Be concise and operational."
)

_CITE = re.compile(r"\[S(\d+)\]")


@dataclass
class AssistantAnswer:
    """Result of an assistant query."""

    question: str
    declined: bool
    text: str | None = None
    recommendation: Recommendation | None = None
    used_sources: list[str] = field(default_factory=list)  # cited source_ids


class KnowledgeAssistant:
    def __init__(self, chat: ChatClient, library: list[KnowledgeItem],
                 site: str = "LU", top_k: int = 3, min_score: float = 0.2,
                 embed_client=None, content_safety=None) -> None:
        self._chat = chat
        self._library = library
        self._site = site
        self._top_k = top_k
        self._min_score = min_score
        self._embed = embed_client
        from workloads.content_safety import AllowAll
        self._safety = content_safety or AllowAll()

    def ask(self, question: str) -> AssistantAnswer:
        hits = retrieve(question, self._library, self._top_k, self._min_score, self._embed)
        if not hits:
            # No grounding -> decline, do not call the model to fabricate (FR-014).
            return AssistantAnswer(question=question, declined=True,
                                   text="No supporting procedure found; declining to answer.")

        items = [it for it, _ in hits]
        sources_block = "\n".join(
            f"[S{i+1}] ({it.source_id}) {it.title}: {it.text}" for i, it in enumerate(items)
        )
        user = f"QUESTION:\n{question}\n\nSOURCES:\n{sources_block}"
        answer = self._chat.complete(SYSTEM_PROMPT, user).strip()

        if INSUFFICIENT in answer:
            return AssistantAnswer(question=question, declined=True,
                                   text="Model reported insufficient grounded context; declined.")

        cited_idx = {int(n) for n in _CITE.findall(answer)}
        cited_items = [items[i - 1] for i in sorted(cited_idx) if 1 <= i <= len(items)]
        if not cited_items:
            # An answer with no citations is treated as ungrounded and rejected (SC-008).
            return AssistantAnswer(question=question, declined=True,
                                   text="Answer lacked citations; rejected as ungrounded.")

        citations = [Citation(source_id=it.source_id, title=it.title) for it in cited_items]
        content_safe = self._safety.is_safe(answer)
        if not content_safe:
            # Unsafe generation is never published, even if grounded (Constitution VI).
            return AssistantAnswer(question=question, declined=True,
                                   text="Answer failed Content Safety; withheld.",
                                   used_sources=[it.source_id for it in cited_items])
        rec = Recommendation(
            recommendation_id=str(uuid.uuid4()),
            pillar=RecommendationPillar.Knowledge,
            site=self._site,
            summary=answer,
            rationale="Grounded answer over cited operator procedures; awaiting human review.",
            citations=citations,
            content_safety_passed=content_safe,
            status=RecommendationStatus.Proposed,  # human-in-the-loop gate (Constitution I)
        )
        return AssistantAnswer(question=question, declined=False, text=answer,
                               recommendation=rec,
                               used_sources=[it.source_id for it in cited_items])
