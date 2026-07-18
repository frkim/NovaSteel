"""P4 interview-capture pipeline (FR-012, Constitution II).

Turns a raw operator-interview transcript into a de-identified, source-cited ``KnowledgeItem``
for the library, while preserving the raw personal content separately so it stays erasable under
GDPR (see platform/governance/gdpr.py). PII (names, emails, phone numbers) is redacted from the
knowledge text; the raw transcript is retained only in the erasable capture, linked to the
operator's subject id.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from workloads.p4_knowledge_capture.knowledge_library import KnowledgeItem

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"\+?\d[\d\s().-]{6,}\d")


@dataclass(frozen=True)
class RawCapture:
    """Erasable raw personal content from an interview (GDPR right-to-erasure applies)."""

    item_id: str        # matches the KnowledgeItem.source_id it was derived into
    subject_id: str     # the operator (data subject)
    site: str
    raw_transcript: str


@dataclass(frozen=True)
class CapturedKnowledge:
    item: KnowledgeItem        # de-identified, added to the library
    raw: RawCapture            # raw personal content, kept erasable


def redact_pii(text: str, *, names: tuple[str, ...] = ()) -> str:
    """Redact emails, phone numbers and provided operator names from free text."""
    redacted = _EMAIL.sub("[EMAIL]", text)
    redacted = _PHONE.sub("[PHONE]", redacted)
    for name in names:
        if name.strip():
            redacted = re.sub(re.escape(name), "[OPERATOR]", redacted, flags=re.IGNORECASE)
    return redacted


def capture_interview(
    transcript: str,
    *,
    operator_id: str,
    operator_name: str,
    site: str,
    source_id: str,
    title: str,
    tags: tuple[str, ...] = (),
) -> CapturedKnowledge:
    """De-identify a transcript into a KnowledgeItem + retain the erasable raw capture."""
    if not transcript.strip():
        raise ValueError("transcript is empty")
    deidentified = redact_pii(transcript, names=(operator_name,))
    item = KnowledgeItem(source_id=source_id, title=title, text=deidentified, site=site, tags=tags)
    raw = RawCapture(item_id=source_id, subject_id=operator_id, site=site, raw_transcript=transcript)
    return CapturedKnowledge(item=item, raw=raw)
