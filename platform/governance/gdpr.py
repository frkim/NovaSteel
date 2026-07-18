"""GDPR erasure runbook — erase raw personal content, preserve the audit trail (Constitution II).

Right-to-erasure implementation: raw personal content (e.g., named operator interview transcripts
in the P4 knowledge library) is redacted/removed, while the immutable audit record is retained
(audit records are exempt from erasure). The erasure itself is recorded as a new append-only audit
entry — audit history is never deleted, only appended.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid5

from novasteel_core.audit import AuditLog
from novasteel_core.models import AuditRecord, AuditSubjectType, Origin, RetentionClass

LOGIC_VERSION = "gdpr-erasure-v1"


@dataclass
class PersonalContentItem:
    """A stored item that may carry personal data (subject_id) alongside derived content."""

    item_id: str
    subject_id: str            # data subject (person) this raw content belongs to
    site: str
    raw_personal_content: str  # erasable
    derived_content: str       # de-identified knowledge kept for operations
    erased: bool = False


@dataclass
class KnowledgeStore:
    items: list[PersonalContentItem] = field(default_factory=list)

    def for_subject(self, subject_id: str) -> list[PersonalContentItem]:
        return [i for i in self.items if i.subject_id == subject_id and not i.erased]


def erase_subject(
    subject_id: str,
    store: KnowledgeStore,
    audit_log: AuditLog,
    *,
    site: str = "",
    erased_at: datetime | None = None,
) -> int:
    """Erase raw personal content for ``subject_id``; retain derived content + audit trail.

    Returns the number of items redacted. Appends one audit record per erased item; never
    mutates or deletes existing audit history (Constitution II).
    """
    erased_at = erased_at or datetime.now(timezone.utc)
    count = 0
    for item in store.items:
        if item.subject_id != subject_id or item.erased:
            continue
        item.raw_personal_content = ""  # raw personal content erased
        item.erased = True
        count += 1
        audit_log.append(AuditRecord(
            audit_id=str(uuid5(NAMESPACE_URL, f"erasure:{item.item_id}:{subject_id}")),
            subject_type=AuditSubjectType.KnowledgeItem,
            subject_id=item.item_id,
            site=site or item.site,
            action="PersonalContentErased",
            inputs_ref=[subject_id],
            model_or_logic_version=LOGIC_VERSION,
            output={"itemId": item.item_id, "rawContentErased": True, "derivedContentRetained": True},
            reviewer_id=None,
            rationale="GDPR right-to-erasure: raw personal content removed; audit trail retained.",
            timestamp=erased_at,
            origin=Origin.Real,
            retention_class=RetentionClass.PredictionDecisionAudit,
        ))
    return count
