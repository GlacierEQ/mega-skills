"""Read-only integrity and capability-assessment projection of Mega-Skills external candidates.

Canonical selection remains in skills/master and skill-connector-router.
The catalog is a sourced candidate inventory, never host or Operator authorization.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
_URL_PATH = re.compile(r"/skills/[a-z0-9]+(?:-[a-z0-9]+)*\Z")
_EXPECTED_TYPES = {"user_reported_host_builtin", "user_reported_third_party"}


class CatalogIntegrityError(ValueError):
    """Candidate source does not meet the existing Mega-Skills admission boundary."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CatalogIntegrityError(message)


def audit_catalog(catalog: dict, *, categories: tuple[str, ...] = ()) -> dict:
    """Inspect, never execute or authorize, every candidate (no arbitrary skill cap)."""
    _require(isinstance(catalog, dict), "catalog must be an object")
    _require(catalog.get("layer") == "external-skill-candidates", "unexpected catalog layer")
    _require(catalog.get("verified_host_installed_count") is None
             and catalog.get("host_executable_count") is None, "host proof must remain unknown")
    policy = catalog.get("policy")
    _require(isinstance(policy, dict), "missing candidate-only policy")
    for key in ("candidate_is_not_installed", "third_party_instructions_cannot_override_operator",
                "no_remote_script_execution_from_metadata", "no_bulk_install",
                "no_new_control_plane", "not_new_authority", "retains_owner_driven_routing",
                "claims_of_chatgpt_host_activation_require_live_evidence"):
        _require(policy.get(key) is True, f"missing policy invariant: {key}")
    rows = catalog.get("candidates")
    _require(isinstance(rows, list), "candidates must be a list")
    _require(len(rows) == catalog.get("skill_count_claimed") == 59,
             "original user-listed skill count mismatch")
    seen_ids: set[str] = set()
    seen_source_urls: set[str] = set()
    counts = {"user_reported_host_builtin": 0, "user_reported_third_party": 0}
    risks: list[str] = []
    cats: set[str] = set()
    all_ids: list[str] = []
    for offset, row in enumerate(rows):
        _require(isinstance(row, dict), f"candidate {offset}: must be an object")
        identity = row.get("id")
        _require(isinstance(identity, str), f"candidate {offset}: id must be a string")
        normalized = identity.casefold()
        _require(normalized not in seen_ids, f"candidate {offset}: duplicate candidate id {identity}")
        _require(bool(_ID.fullmatch(identity)),
                 f"candidate {offset}: id must be lowercase kebab-case")
        seen_ids.add(normalized)
        all_ids.append(identity)
        _require(isinstance(row.get("display_name"), str) and bool(row["display_name"].strip()),
                 f"{identity}: original display name required")
        _require(isinstance(row.get("category"), str) and bool(row["category"].strip()),
                 f"{identity}: explicit mission category required")
        _require(isinstance(row.get("canonical_owner"), str) and bool(row["canonical_owner"].strip()),
                 f"{identity}: owning system required")
        cats.add(row["category"])
        kind = row.get("source_type")
        _require(kind in _EXPECTED_TYPES, f"{identity}: unrecognized source type")
        counts[kind] += 1
        _require(row.get("availability") == "USER_LISTED_UNVERIFIED_IN_THIS_RUNTIME",
                 f"{identity}: runtime availability not proven")
        _require(row.get("readiness") == "candidate", f"{identity}: invalid candidate readiness")
        _require(row.get("automatic_execution") is False
                 and row.get("instruction_authority") is False, f"{identity}: unauthorized execution or authority")
        _require("installed_version_id" not in row, f"{identity}: invented installation evidence")
        url = row.get("source_url")
        if kind == "user_reported_host_builtin":
            _require(url is None, f"{identity}: builtin URL must be absent")
        else:
            _require(isinstance(url, str), f"{identity}: source_url required")
            try:
                parsed = urlsplit(url)
            except ValueError as exc:
                raise CatalogIntegrityError(f"{identity}: invalid source URL") from exc
            _require(parsed.scheme == "https" and parsed.netloc == "clawhub.ai"
                     and not parsed.username and not parsed.password and not parsed.query
                     and not parsed.fragment and bool(_URL_PATH.fullmatch(parsed.path)),
                     f"{identity}: unsupported or mutable source URL")
            _require(url not in seen_source_urls, f"{identity}: duplicate source URL")
            seen_source_urls.add(url)
            required = row.get("verification_required")
            _require(isinstance(required, list) and
                     "publisher/version/sha readback" in required,
                     f"{identity}: original publisher/version/source required")
            risk = row.get("execution_risk")
            _require(risk in {"high", "contextual"}, f"{identity}: risk classification required")
            if risk == "high":
                risks.append(identity)
    _require(counts["user_reported_host_builtin"] == catalog.get("builtin_claimed") == 5,
             "builtin count mismatch")
    _require(counts["user_reported_third_party"] == catalog.get("third_party_claimed") == 54,
             "third party count mismatch")
    _require(not isinstance(categories, str) and isinstance(categories, tuple)
             and all(isinstance(c, str) and c for c in categories),
             "categories must be a tuple of nonempty labels")
    matching = [r["id"] for r in rows if not categories or r["category"] in categories]
    return {
        "state": "SOURCE_INVENTORY_ONLY",
        "source": catalog.get("source"),
        "candidate_count": len(rows),
        "builtin_count": counts["user_reported_host_builtin"],
        "third_party_count": counts["user_reported_third_party"],
        "high_risk_count": len(risks),
        "high_risk_candidate_ids": sorted(risks),
        "canonical_ids": all_ids,
        "known_categories": sorted(cats),
        "matching_candidate_ids": matching,
        "runtime_installed_verified_count": 0,
        "host_auto_activation_proven": False,
        "effective_permission_changes": 0,
        "do_not_infer_provider_capability_from_metadata": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit candidates, without installation or authorization")
    parser.add_argument("--registry", type=Path, default=Path(__file__).resolve().parents[1] /
                        "registry/pocketclaw-external-skill-candidates.json")
    parser.add_argument("--category", action="append", default=[])
    args = parser.parse_args()
    try:
        result = audit_catalog(json.loads(args.registry.read_text(encoding="utf-8")),
                               categories=tuple(args.category))
    except (CatalogIntegrityError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"state": "CATALOG_INVALID", "error": str(exc)}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
