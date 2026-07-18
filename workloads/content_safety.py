"""Azure AI Content Safety integration (Constitution VI).

All generative output (P2/P3 explainers, P4 knowledge assistant) must pass Content Safety
before it is surfaced. Auth uses Entra managed identity (DefaultAzureCredential) — no API key.

The `ContentSafetyChecker` protocol is injectable so pillars are unit-tested deterministically
with `AllowAll` / `BlockAll`, and run live against the deployed AI Services Content Safety
endpoint via `AzureContentSafety`.

Env (defaults target the deployed account aif-novastee-dev-ox26fi):
  CONTENT_SAFETY_ENDPOINT   e.g. https://aif-novastee-dev-ox26fi.cognitiveservices.azure.com
  CONTENT_SAFETY_API_VERSION  default '2024-09-01'
  CONTENT_SAFETY_MAX_SEVERITY default '2'  (0=safe .. 6=high; block if any category exceeds)
"""

from __future__ import annotations

import os
from typing import Protocol, runtime_checkable

DEFAULT_API_VERSION = "2024-09-01"
DEFAULT_MAX_SEVERITY = 2


@runtime_checkable
class ContentSafetyChecker(Protocol):
    def is_safe(self, text: str) -> bool: ...


class AllowAll:
    """No-op checker (dev/tests). Explicit so 'unchecked' is never accidental."""

    def is_safe(self, text: str) -> bool:  # noqa: D401
        return True


class BlockAll:
    """Rejects everything — used to prove the safety gate blocks unsafe output in tests."""

    def is_safe(self, text: str) -> bool:
        return False


class AzureContentSafety:
    """Live Content Safety checker over the deployed AI Services account (Entra auth, no key)."""

    def __init__(self, endpoint: str | None = None, api_version: str | None = None,
                 max_severity: int | None = None) -> None:
        self.endpoint = (endpoint or os.getenv("CONTENT_SAFETY_ENDPOINT", "")).rstrip("/")
        self.api_version = api_version or os.getenv("CONTENT_SAFETY_API_VERSION", DEFAULT_API_VERSION)
        self.max_severity = (
            max_severity if max_severity is not None
            else int(os.getenv("CONTENT_SAFETY_MAX_SEVERITY", str(DEFAULT_MAX_SEVERITY)))
        )
        if not self.endpoint:
            raise ValueError("CONTENT_SAFETY_ENDPOINT is required for AzureContentSafety")
        from azure.identity import DefaultAzureCredential  # lazy import

        self._credential = DefaultAzureCredential()

    def _token(self) -> str:
        return self._credential.get_token("https://cognitiveservices.azure.com/.default").token

    def is_safe(self, text: str) -> bool:
        import requests  # lazy import

        url = f"{self.endpoint}/contentsafety/text:analyze?api-version={self.api_version}"
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {self._token()}", "Content-Type": "application/json"},
            json={"text": text},
            timeout=30,
        )
        resp.raise_for_status()
        analysis = resp.json().get("categoriesAnalysis", [])
        return all(item.get("severity", 0) <= self.max_severity for item in analysis)


def default_checker() -> ContentSafetyChecker:
    """AzureContentSafety when an endpoint is configured, else AllowAll (dev)."""
    if os.getenv("CONTENT_SAFETY_ENDPOINT"):
        return AzureContentSafety()
    return AllowAll()
