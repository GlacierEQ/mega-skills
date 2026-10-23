#!/usr/bin/env python3
"""REA installation identity verification and doctor-output triage.

The supply-chain discipline of the rea-operator skill, made executable:
- A candidate npm package is accepted only when name, version pin,
  license, and repository all match the canonical record (morluto/rea).
  Lookalike packages are a live hazard; a copied README proves nothing.
- Doctor output is classified per provider: healthy / degraded /
  missing with its named remedy. Doctor readiness is not session
  connection - the two are reported separately, always.
- The recovery ladder maps a failure class to its remedy; setup is
  never the remedy for a PATH, approval, or engine problem.
"""
from __future__ import annotations

CANONICAL = {
    "name": "rea-agents",
    "license": "MIT",
    "repository_url_fragment": "github.com/morluto/rea",
}


def verify_package_identity(package_json: dict, pinned_version: str) -> dict:
    """Verify an installed package.json against the canonical identity."""
    problems = []
    if package_json.get("name") != CANONICAL["name"]:
        problems.append(f"name is {package_json.get('name')!r}, expected 'rea-agents'")
    if package_json.get("version") != pinned_version:
        problems.append(f"version is {package_json.get('version')!r}, expected pinned {pinned_version!r}")
    if package_json.get("license") != CANONICAL["license"]:
        problems.append(f"license is {package_json.get('license')!r}, expected 'MIT'")
    repository = package_json.get("repository", {})
    url = repository.get("url", "") if isinstance(repository, dict) else str(repository)
    if CANONICAL["repository_url_fragment"] not in url:
        problems.append(f"repository {url!r} does not point at morluto/rea")
    return {"accepted": not problems, "problems": problems,
            "identity": {"name": package_json.get("name"),
                         "version": package_json.get("version"),
                         "repository": url}}


def classify_doctor(text: str) -> list[dict]:
    """Classify `rea doctor` provider lines: '- name: X' blocks carrying
    an ok flag and a classification. Returns one record per provider."""
    providers = []
    current = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- name:"):
            current = {"name": stripped.split(":", 1)[1].strip(), "ok": None,
                       "classification": None, "detail": None}
            providers.append(current)
        elif current is not None and stripped.startswith("ok:"):
            current["ok"] = stripped == "ok: true"
        elif current is not None and stripped.startswith("classification:"):
            current["classification"] = stripped.split(":", 1)[1].strip()
        elif current is not None and stripped.startswith("detail:"):
            current["detail"] = stripped.split(":", 1)[1].strip()
    return providers


def summarize_doctor(text: str) -> dict:
    providers = classify_doctor(text)
    return {
        "providers": providers,
        "healthy": [p["name"] for p in providers if p["classification"] == "healthy"],
        "missing": [p["name"] for p in providers if p["classification"] != "healthy"],
        "session_connected": None,  # doctor cannot prove this; set only from a live tools/list
        "note": "doctor inspects registration and engines; it cannot prove the current session is connected",
    }


RECOVERY_LADDER = {
    "client_approval_pending": "approve the client prompt; do not re-run setup",
    "path_missing": "fix the shell PATH for the client process; do not re-run setup",
    "registration_absent": "prepare the setup dry-run plan, obtain approval, then apply it",
    "engine_missing": "supply the caller-owned engine (Ghidra/JADX/...) or proceed with static readers",
    "connection_dropped": "retry once when the call is safe to repeat; otherwise restart the client",
    "host_timeout": "check whether the target-side work completed before repeating an unchanged call",
}


def remedy_for(failure_class: str) -> dict:
    if failure_class not in RECOVERY_LADDER:
        return {"failure_class": failure_class, "remedy": None,
                "reason": "unclassified failure; diagnose before repairing"}
    return {"failure_class": failure_class, "remedy": RECOVERY_LADDER[failure_class]}


def main(argv=None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Verify a rea-agents package.json identity.")
    parser.add_argument("package_json")
    parser.add_argument("--pinned", required=True)
    args = parser.parse_args(argv)
    result = verify_package_identity(json.load(open(args.package_json)), args.pinned)
    print(json.dumps(result, indent=2))
    return 0 if result["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
