"""Provision per-persona / per-site Entra groups + Fabric workspace roles (Constitution VII).

Automates the RBAC scaffolding: one Entra security group per (persona, site) and a Fabric
workspace role assignment for each, so access is least-privilege and data is per-site isolated.
Group *membership* (which humans belong where) is a business decision and is NOT automated.

Auth: Entra via Microsoft Graph, Fabric via the Fabric REST API — both with an identity that has
Group.ReadWrite.All (Graph) and Fabric workspace admin. Nothing here uses keys.

Env:
  GRAPH_TOKEN    token for https://graph.microsoft.com  (az account get-access-token --resource https://graph.microsoft.com)
  FABRIC_TOKEN   token for https://api.fabric.microsoft.com
  WORKSPACE_ID   Fabric workspace id (default: the NovaSteel dev workspace)

Usage:  python provision_entra_rbac.py [--apply]   # dry-run unless --apply is given
"""

from __future__ import annotations

import os
import sys

import requests

WORKSPACE_ID = os.getenv("WORKSPACE_ID", "9a005c2a-169c-4cd7-af65-7f097bd0c5b8")
GRAPH = "https://graph.microsoft.com/v1.0"
FABRIC = "https://api.fabric.microsoft.com/v1"

# Personas (NovaSteel.Contracts ReviewerRole) -> default Fabric workspace role.
PERSONA_ROLES = {
    "operator": "Viewer",
    "maintenance": "Viewer",
    "energy": "Viewer",
    "quality": "Viewer",
    "executive": "Viewer",
    "compliance": "Member",   # DPO needs broader read for audit/lineage
}
SITES = ["LU", "DE", "BE", "ES"]


def _graph_headers() -> dict:
    return {"Authorization": f"Bearer {os.environ['GRAPH_TOKEN']}", "Content-Type": "application/json"}


def _fabric_headers() -> dict:
    return {"Authorization": f"Bearer {os.environ['FABRIC_TOKEN']}", "Content-Type": "application/json"}


def ensure_group(name: str, apply: bool) -> str | None:
    """Create (or find) an Entra security group; return its object id."""
    r = requests.get(f"{GRAPH}/groups?$filter=displayName eq '{name}'", headers=_graph_headers())
    r.raise_for_status()
    found = r.json().get("value", [])
    if found:
        return found[0]["id"]
    if not apply:
        print(f"  [dry-run] would create group {name}")
        return None
    body = {
        "displayName": name,
        "mailEnabled": False,
        "mailNickname": name.lower().replace(" ", ""),
        "securityEnabled": True,
        "description": "NovaSteel per-persona/per-site access group (least-privilege, per-site isolation).",
    }
    created = requests.post(f"{GRAPH}/groups", headers=_graph_headers(), json=body)
    created.raise_for_status()
    gid = created.json()["id"]
    print(f"  created group {name} ({gid})")
    return gid


def assign_workspace_role(principal_id: str, role: str, apply: bool) -> None:
    if not apply or not principal_id:
        print(f"  [dry-run] would assign {role} to {principal_id or '<group>'}")
        return
    body = {"principal": {"id": principal_id, "type": "Group"}, "role": role}
    resp = requests.post(f"{FABRIC}/workspaces/{WORKSPACE_ID}/roleAssignments",
                         headers=_fabric_headers(), json=body)
    if resp.status_code not in (200, 201):
        print(f"  WARN role assign {resp.status_code}: {resp.text[:200]}")
    else:
        print(f"  assigned {role} to {principal_id}")


def main() -> int:
    apply = "--apply" in sys.argv
    print(f"Provisioning Entra RBAC ({'APPLY' if apply else 'dry-run'}) ...")
    for persona, role in PERSONA_ROLES.items():
        for site in SITES:
            name = f"ns-{persona}-{site}"
            gid = ensure_group(name, apply)
            assign_workspace_role(gid, role, apply)
    print("Done. Map users into the ns-<persona>-<site> groups; RLS in Power BI keys on [site].")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
