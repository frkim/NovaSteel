"""Register the NovaSteel data sources in Microsoft Purview and trigger a scan (Constitution II).

Automates registering OneLake + the Eventhouse (KQL DB) as Purview sources and kicking off a
scan so sensor -> Bronze -> Silver -> Gold -> prediction lineage is captured in the data map.
Fabric emits lineage to Purview automatically once the tenant integration is enabled (a one-time
admin setting that is NOT automatable here).

Auth: Purview REST with an identity holding the Purview Data Source Administrator + Data Curator
roles (managed identity / az login). No keys.

Env:
  PURVIEW_ACCOUNT   Purview account name (e.g. pview-...)
  PURVIEW_TOKEN     token for https://purview.azure.net  (az account get-access-token --resource https://purview.azure.net)

Usage:  python register_purview_sources.py [--apply]
"""

from __future__ import annotations

import os
import sys

import requests

ACCOUNT = os.getenv("PURVIEW_ACCOUNT", "pview-novastee-dev-ox26fi")
WORKSPACE_ID = os.getenv("WORKSPACE_ID", "9a005c2a-169c-4cd7-af65-7f097bd0c5b8")


def _base() -> str:
    return f"https://{ACCOUNT}.purview.azure.com/scan"


def _headers() -> dict:
    return {"Authorization": f"Bearer {os.environ['PURVIEW_TOKEN']}", "Content-Type": "application/json"}


SOURCES = {
    "novasteel-onelake": {
        "kind": "Fabric",
        "properties": {"tenant": os.getenv("AZURE_TENANT_ID", ""), "workspaceId": WORKSPACE_ID},
    },
}


def register_source(name: str, body: dict, apply: bool) -> None:
    if not apply:
        print(f"  [dry-run] would register source {name} ({body['kind']})")
        return
    resp = requests.put(f"{_base()}/datasources/{name}?api-version=2022-07-01-preview",
                        headers=_headers(), json=body)
    print(f"  register {name}: {resp.status_code}")


def trigger_scan(source: str, scan: str, apply: bool) -> None:
    if not apply:
        print(f"  [dry-run] would create + run scan {scan} on {source}")
        return
    requests.put(f"{_base()}/datasources/{source}/scans/{scan}?api-version=2022-07-01-preview",
                 headers=_headers(), json={"kind": "FabricMsi", "properties": {}})
    run = requests.post(f"{_base()}/datasources/{source}/scans/{scan}/runs?api-version=2022-07-01-preview",
                        headers=_headers())
    print(f"  scan {scan} run: {run.status_code}")


def main() -> int:
    apply = "--apply" in sys.argv
    print(f"Registering Purview sources ({'APPLY' if apply else 'dry-run'}) ...")
    print("Prerequisite (one-time, admin): enable Fabric->Purview lineage tenant setting.")
    for name, body in SOURCES.items():
        register_source(name, body, apply)
        trigger_scan(name, f"{name}-scan", apply)
    print("Done. Tag gold_kpi_synthetic with the Synthetic classification (Constitution IX).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
