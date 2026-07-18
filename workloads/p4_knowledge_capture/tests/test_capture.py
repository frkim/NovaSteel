from __future__ import annotations

from workloads.p4_knowledge_capture.assistant import KnowledgeAssistant
from workloads.p4_knowledge_capture.capture import capture_interview, redact_pii
from workloads.p4_knowledge_capture.knowledge_library import KnowledgeItem, load_library

TRANSCRIPT = (
    "Interview with Jane Doe (jane.doe@novasteel.eu, +32 470 12 34 56): "
    "Reline the furnace lining when the RUL model forecasts failure within 21 days. "
    "Never run to failure."
)


class FakeChat:
    def __init__(self, response: str) -> None:
        self.response = response

    def complete(self, system: str, user: str) -> str:
        return self.response


def test_redact_pii_removes_email_phone_and_name() -> None:
    out = redact_pii(TRANSCRIPT, names=("Jane Doe",))
    assert "jane.doe@novasteel.eu" not in out
    assert "470 12 34 56" not in out
    assert "Jane Doe" not in out
    assert "[EMAIL]" in out and "[PHONE]" in out and "[OPERATOR]" in out
    # Operational knowledge is preserved.
    assert "21 days" in out


def test_capture_produces_deidentified_item_and_erasable_raw() -> None:
    cap = capture_interview(
        TRANSCRIPT, operator_id="operator-jane", operator_name="Jane Doe", site="DE",
        source_id="SOP-FURNACE-RELINE-099", title="Furnace reline trigger (captured)",
        tags=("furnace", "rul"),
    )
    assert isinstance(cap.item, KnowledgeItem)
    # De-identified item carries no PII.
    assert "jane.doe@novasteel.eu" not in cap.item.text and "Jane Doe" not in cap.item.text
    assert cap.item.source_id == "SOP-FURNACE-RELINE-099" and cap.item.site == "DE"
    # Raw personal content retained separately, linked to the subject + item.
    assert cap.raw.subject_id == "operator-jane"
    assert cap.raw.item_id == cap.item.source_id
    assert "Jane Doe" in cap.raw.raw_transcript  # raw kept for GDPR-erasable store


def test_captured_item_is_usable_by_the_assistant() -> None:
    cap = capture_interview(
        TRANSCRIPT, operator_id="operator-jane", operator_name="Jane Doe", site="DE",
        source_id="SOP-FURNACE-RELINE-099", title="Furnace reline trigger", tags=("furnace",),
    )
    library = load_library() + [cap.item]
    assistant = KnowledgeAssistant(FakeChat("Reline within 21 days [S1]."), library, site="DE")
    ans = assistant.ask("When do we reline the furnace lining?")
    assert not ans.declined
    assert ans.recommendation is not None
