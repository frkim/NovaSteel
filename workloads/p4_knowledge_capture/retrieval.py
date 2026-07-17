"""Lightweight retrieval over the procedure library (grounding for the assistant).

Default is a dependency-free lexical scorer (token overlap) so unit tests are fast and
deterministic. When a live `EmbeddingClient` is supplied, cosine similarity over
text-embedding-3-large is used instead (production RAG via Foundry IQ / embeddings).
"""

from __future__ import annotations

import math
import re
from typing import Sequence

from .knowledge_library import KnowledgeItem

_WORD = re.compile(r"[a-z0-9]+")
_STOPWORDS = frozenset(
    "a an the is are was were be to of for and or in on at by with from as it this that "
    "what when how do does can should would i we you they my our your".split()
)


def _tokens(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOPWORDS and len(w) > 1}


def _lexical_score(query: str, item: KnowledgeItem) -> float:
    q = _tokens(query)
    if not q:
        return 0.0
    doc = _tokens(f"{item.title} {item.text} {' '.join(item.tags)}")
    overlap = q & doc
    return len(overlap) / len(q)


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def retrieve(query: str,
             library: list[KnowledgeItem],
             top_k: int = 3,
             min_score: float = 0.2,
             embed_client=None) -> list[tuple[KnowledgeItem, float]]:
    """Return up to top_k (item, score) above min_score, best first.

    If nothing scores above `min_score`, returns [] — the assistant MUST then decline
    rather than fabricate (FR-014, SC-008).
    """
    if embed_client is not None:
        docs = [f"{it.title}. {it.text}" for it in library]
        vectors = embed_client.embed([query, *docs])
        qv, dvs = vectors[0], vectors[1:]
        scored = [(it, _cosine(qv, dv)) for it, dv in zip(library, dvs)]
    else:
        scored = [(it, _lexical_score(query, it)) for it in library]

    scored.sort(key=lambda t: t[1], reverse=True)
    return [(it, s) for it, s in scored[:top_k] if s >= min_score]
