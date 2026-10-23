#!/usr/bin/env python3
"""RE safety gate: authorization, exclusion, and effect classification.

Implements the gate discipline of the re-safety-gate skill as executable
checks. A plan is admitted only when (a) an authority basis is recorded,
(b) the purpose is not on REA's disclaimer exclusion list, and (c) every
operation that executes foreign code or is destructive is confined to a
throwaway environment. Inspection authority never implies execution
authority; each is decided separately.
"""
from __future__ import annotations

import hashlib
import json

# REA DISCLAIMER exclusion list (paraphrased category keys; the gate refuses
# these purposes outright, per target, without renegotiation).
EXCLUDED_PURPOSES = {
    "drm_circumvention": "circumventing DRM, license checks, anti-cheat, or other technical protection measures",
    "game_cheats": "developing game cheats or tampering with online services",
    "unauthorized_access_bypass": "bypassing authentication, bot protection, or access controls on systems the operator is not authorized to test",
    "proprietary_copying": "copying proprietary software or reproducing its protected code and assets",
    "provider_policy_evasion": "evading AI provider usage policies",
    "account_resale": "reselling or sharing AI accounts or API access",
}

AUTHORIZED_BASES = {
    "owned_software",
    "authorized_security_research",
    "malware_incident_analysis",
    "vulnerability_research",
    "ctf_education",
    "interoperability",
    "preservation",
    "debugging_owned_systems",
}

# Operation classes that execute foreign code or mutate state. Per REA's
# tool-effect flags, these require a throwaway environment.
EXECUTING_OPERATIONS = {
    "capture_process_scenario",
    "run_executable_scenario",
    "instrument_with_frida",
    "start_gdb_session",
    "start_lldb_session",
    "inspect_recorded_crash",
    "analyze_javascript_application_runtime",
}
DESTRUCTIVE_OPERATIONS = {"delete_analysis_target", "remove_evidence_record"}


def classify_operation(operation: str) -> dict:
    """Return the effect classification for one planned operation."""
    if operation in DESTRUCTIVE_OPERATIONS:
        return {"operation": operation, "executes_foreign_code": False,
                "destructive": True, "requires_throwaway": True}
    if operation in EXECUTING_OPERATIONS:
        return {"operation": operation, "executes_foreign_code": True,
                "destructive": False, "requires_throwaway": True}
    return {"operation": operation, "executes_foreign_code": False,
            "destructive": False, "requires_throwaway": False}


def evaluate_gate(request: dict) -> dict:
    """Decide a gate request.

    request keys: authority_basis, purpose, operations (list of tool names),
    environment ({'throwaway': bool}), execute (bool — execution authority
    sought separately from inspection authority).
    Returns a decision record; 'admitted' is true only when every check
    passes. The record digest makes the decision citable in the ledger.
    """
    reasons: list[str] = []
    basis = request.get("authority_basis")
    if basis not in AUTHORIZED_BASES:
        reasons.append(f"no valid authority basis recorded: {basis!r}")
    purpose = request.get("purpose")
    if purpose in EXCLUDED_PURPOSES:
        reasons.append(f"purpose is on the disclaimer exclusion list: {EXCLUDED_PURPOSES[purpose]}")
    environment = request.get("environment") or {}
    effects = [classify_operation(op) for op in request.get("operations", [])]
    needs_throwaway = any(e["requires_throwaway"] for e in effects)
    if needs_throwaway and not environment.get("throwaway"):
        reasons.append("executing/destructive operations require a throwaway environment")
    if request.get("execute") and not request.get("execution_authorized"):
        reasons.append("execution authority was not granted separately from inspection authority")
    decision = {
        "admitted": not reasons,
        "authority_basis": basis,
        "purpose": purpose,
        "refusal_reasons": reasons,
        "operation_effects": effects,
        "environment": {"throwaway": bool(environment.get("throwaway"))},
    }
    canonical = json.dumps(decision, sort_keys=True, separators=(",", ":"))
    decision["decision_digest"] = hashlib.sha256(canonical.encode()).hexdigest()
    return decision


def main(argv=None) -> int:
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Evaluate an RE safety-gate request given as JSON on stdin; print the decision record.")
    parser.parse_args(argv)
    request = json.load(sys.stdin)
    decision = evaluate_gate(request)
    print(json.dumps(decision, indent=2, sort_keys=True))
    return 0 if decision["admitted"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
