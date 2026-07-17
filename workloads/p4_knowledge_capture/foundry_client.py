"""Live-callable client for the deployed Microsoft Foundry models (gpt-5 + embeddings).

Uses Entra auth (DefaultAzureCredential / az login) against the deployed AI Services
account. Kept behind the `ChatClient` protocol so the assistant can be unit-tested
with a deterministic fake and separately smoke-tested against live gpt-5.

Env (defaults target the deployed account aif-novastee-dev-ox26fi):
  FOUNDRY_ENDPOINT   e.g. https://aif-novastee-dev-ox26fi.cognitiveservices.azure.com
  FOUNDRY_CHAT_DEPLOYMENT     default 'gpt-5'
  FOUNDRY_EMBED_DEPLOYMENT    default 'text-embedding-3-large'
  FOUNDRY_API_VERSION         default '2025-01-01-preview'
"""

from __future__ import annotations

import os
from typing import Protocol, Sequence

DEFAULT_ENDPOINT = "https://aif-novastee-dev-ox26fi.cognitiveservices.azure.com"
DEFAULT_API_VERSION = "2025-01-01-preview"


class ChatClient(Protocol):
    """Minimal chat surface the assistant depends on (injectable for tests)."""

    def complete(self, system: str, user: str) -> str: ...


class EmbeddingClient(Protocol):
    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class FoundryClient:
    """Live client for the deployed Foundry gpt-5 chat + embeddings (Entra auth)."""

    def __init__(self,
                 endpoint: str | None = None,
                 chat_deployment: str | None = None,
                 embed_deployment: str | None = None,
                 api_version: str | None = None) -> None:
        self.endpoint = (endpoint or os.getenv("FOUNDRY_ENDPOINT", DEFAULT_ENDPOINT)).rstrip("/")
        self.chat_deployment = chat_deployment or os.getenv("FOUNDRY_CHAT_DEPLOYMENT", "gpt-5")
        self.embed_deployment = embed_deployment or os.getenv("FOUNDRY_EMBED_DEPLOYMENT", "text-embedding-3-large")
        self.api_version = api_version or os.getenv("FOUNDRY_API_VERSION", DEFAULT_API_VERSION)
        # Lazy imports so unit tests that use a fake client need no azure SDK.
        from azure.identity import DefaultAzureCredential  # type: ignore
        self._credential = DefaultAzureCredential()

    def _token(self) -> str:
        return self._credential.get_token("https://cognitiveservices.azure.com/.default").token

    def complete(self, system: str, user: str, max_completion_tokens: int = 3000) -> str:
        import requests  # lazy
        url = f"{self.endpoint}/openai/deployments/{self.chat_deployment}/chat/completions?api-version={self.api_version}"
        body = {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_completion_tokens": max_completion_tokens,
        }
        resp = requests.post(url, headers={"Authorization": f"Bearer {self._token()}"}, json=body, timeout=120)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        import requests  # lazy
        url = f"{self.endpoint}/openai/deployments/{self.embed_deployment}/embeddings?api-version={self.api_version}"
        resp = requests.post(url, headers={"Authorization": f"Bearer {self._token()}"},
                             json={"input": list(texts)}, timeout=120)
        resp.raise_for_status()
        return [d["embedding"] for d in resp.json()["data"]]
