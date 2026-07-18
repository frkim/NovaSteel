"""Deploy the NovaSteel Direct Lake semantic model to Fabric via REST (Constitution VI/VII).

Creates/updates a semantic-model item in the Fabric workspace from a local definition directory
(TMDL/BIM + `.platform`), so the reporting model — including per-site RLS roles — is deployed as
code rather than hand-built in the portal. Report *visuals* remain design work.

Auth: Fabric REST with a workspace-admin identity (managed identity / az login). No keys.

Env:
  FABRIC_TOKEN   token for https://api.fabric.microsoft.com
  WORKSPACE_ID   Fabric workspace id (default: NovaSteel dev)

Usage:  python deploy_powerbi_model.py <definition_dir> [--apply]
  (definition_dir defaults to platform/bi/semantic_model)
"""

from __future__ import annotations

import base64
import json
import os
import pathlib
import sys
import time

import requests

WORKSPACE_ID = os.getenv("WORKSPACE_ID", "9a005c2a-169c-4cd7-af65-7f097bd0c5b8")
BASE = "https://api.fabric.microsoft.com/v1"
DEFAULT_DIR = pathlib.Path(__file__).resolve().parents[1] / "bi" / "semantic_model"


def _headers() -> dict:
    return {"Authorization": f"Bearer {os.environ['FABRIC_TOKEN']}", "Content-Type": "application/json"}


def _parts(defn_dir: pathlib.Path) -> list[dict]:
    parts = []
    for f in sorted(defn_dir.rglob("*")):
        if f.is_file():
            payload = base64.b64encode(f.read_bytes()).decode("ascii")
            parts.append({"path": f.relative_to(defn_dir).as_posix(), "payload": payload,
                          "payloadType": "InlineBase64"})
    return parts


def _poll(url: str) -> str:
    while True:
        time.sleep(4)
        o = requests.get(url, headers=_headers()).json()
        if o.get("status") not in ("Running", "NotStarted"):
            return o.get("status", "Failed")


def deploy(defn_dir: pathlib.Path, apply: bool) -> int:
    parts = _parts(defn_dir)
    print(f"Semantic model definition parts: {[p['path'] for p in parts]}")
    if not apply:
        print("[dry-run] pass --apply to create the semantic model in Fabric.")
        return 0
    body = {"displayName": "NovaSteel", "definition": {"parts": parts}}
    resp = requests.post(f"{BASE}/workspaces/{WORKSPACE_ID}/semanticModels",
                         headers=_headers(), data=json.dumps(body))
    if resp.status_code == 202:
        status = _poll(resp.headers["Location"])
        print(f"create semantic model: {status}")
        return 0 if status == "Succeeded" else 1
    print(f"create semantic model: {resp.status_code} {resp.text[:300]}")
    return 0 if resp.status_code in (200, 201) else 1


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--apply"]
    defn_dir = pathlib.Path(args[0]) if args else DEFAULT_DIR
    return deploy(defn_dir, "--apply" in sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
