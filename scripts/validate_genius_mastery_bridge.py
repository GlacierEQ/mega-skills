#!/usr/bin/env python3
"""Validate the pinned Genius-Mastery ↔ Mega-Skills operating-loop contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "integrations" / "genius-mastery-bridge.json"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_PHASES = ["mission", "context", "options", "impact", "action", "outcome"]
EXPECTED_EVIDENCE = [
    "known_from_context",
    "operator_reported",
    "retrieval_pending",
    "not_searched",
    "searched_found",
    "searched_not_found",
    "unavailable",
    "contradicted",
]
EXPECTED_OUTCOMES = ["pending", "observed", "verified", "contradicted"]
EXPECTED_STATUS_MAP = {
    "pending": "ready_to_act",
    "observed": "awaiting_verification",
    "verified": "verified",
    "contradicted": "contradicted",
}


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str):
    raise ValueError(message)


def require_hex(value: str, label: str):
    if not HEX40.fullmatch(value):
        fail(f"{label} is not a full Git SHA")


def expected_raw_url(record: dict, path: str) -> str:
    return f"{record['raw_base'].rstrip('/')}/{record['ref']}/{path}"


def check_local(bridge: dict):
    if bridge.get("schema_version") != 1 or bridge.get("contract_id") != "genius-mastery.operating-loop":
        fail("bridge identity/version mismatch")

    provider = bridge["provider"]
    source = bridge["source_contract"]
    consumer = bridge["consumer"]

    if provider["repository"] != "GlacierEQ/Genius-Mastery":
        fail("unexpected provider")
    for key in ("ref", "module_blob_sha", "schema_blob_sha"):
        require_hex(provider[key], f"provider.{key}")
    if source["repository"] != "GlacierEQ/Genius-Mastery":
        fail("unexpected source contract repository")
    for key in ("ref", "blob_sha", "schema_blob_sha"):
        require_hex(source[key], f"source_contract.{key}")
    if source["path"] != "interfaces/mega-skills-bridge.json":
        fail("source contract path drifted")
    if source["schema"] != "schemas/mega-skills-bridge.schema.json":
        fail("source contract schema path drifted")
    if bridge["$schema"] != expected_raw_url(source, source["schema"]):
        fail("consumer manifest does not point to the pinned source schema")

    if consumer["repository"] != "GlacierEQ/mega-skills" or consumer["combo_id"] != "mission-aware-operating-loop":
        fail("unexpected consumer route")
    if consumer["mega_routes"] != ["apex-adaptive-operations", "apex-genius-mastery"]:
        fail("Mega route set drifted")
    if bridge["compatibility"]["operating_loop_schema_version"] != 1:
        fail("unsupported upstream schema version")
    if bridge["phase_order"] != EXPECTED_PHASES:
        fail("phase order drifted")
    if bridge["evidence_states"] != EXPECTED_EVIDENCE:
        fail("evidence vocabulary drifted")
    if bridge["outcome_statuses"] != EXPECTED_OUTCOMES:
        fail("outcome status vocabulary drifted")
    if bridge["status_map"] != EXPECTED_STATUS_MAP:
        fail("status map drifted")
    if len(bridge.get("invariants", [])) < 4:
        fail("bridge invariants are incomplete")

    for path in (
        ROOT / "combo-skills" / "mission-aware-operating-loop" / "COMBO.md",
        ROOT / "mega-skills" / "apex-genius-mastery" / "MEGA.md",
        ROOT / "mega-skills" / "apex-adaptive-operations" / "MEGA.md",
    ):
        if not path.is_file():
            fail(f"missing integration surface: {path}")
    combo = (ROOT / "combo-skills" / "mission-aware-operating-loop" / "COMBO.md").read_text(encoding="utf-8")
    if "Genius-Mastery" not in combo or "MISSION_OPERATING_LOOP_RECORD.md" not in combo:
        fail("Combo does not declare upstream bridge")


def remote_bytes(record: dict, path: str) -> bytes:
    request = Request(
        expected_raw_url(record, path),
        headers={"User-Agent": "GlacierEQ-mega-skills-bridge-validator"},
    )
    with urlopen(request, timeout=20) as response:
        return response.read()


def check_source_contract(contract: dict, bridge: dict):
    if contract.get("schema_version") != bridge["schema_version"]:
        fail("source contract version mismatch")
    if contract.get("contract_id") != bridge["contract_id"]:
        fail("source contract identity mismatch")
    if contract.get("$schema") != "../schemas/mega-skills-bridge.schema.json":
        fail("source contract schema reference drifted")

    provider = bridge["provider"]
    source_provider = contract["provider"]
    for key in (
        "repository",
        "ref",
        "module",
        "schema",
        "module_blob_sha",
        "schema_blob_sha",
    ):
        if source_provider.get(key) != provider.get(key):
            fail(f"source contract provider mismatch for {key}")
    for key in ("consumer", "compatibility", "phase_order", "evidence_states", "outcome_statuses", "status_map"):
        if contract.get(key) != bridge.get(key):
            fail(f"source contract mismatch for {key}")


def check_bridge_schema(schema: dict, bridge: dict):
    properties = schema.get("properties", {})
    expected_consts = {
        "schema_version": 1,
        "contract_id": "genius-mastery.operating-loop",
        "phase_order": EXPECTED_PHASES,
        "evidence_states": EXPECTED_EVIDENCE,
        "outcome_statuses": EXPECTED_OUTCOMES,
        "status_map": EXPECTED_STATUS_MAP,
    }
    for name, expected in expected_consts.items():
        if properties.get(name, {}).get("const") != expected:
            fail(f"source bridge schema drifted for {name}")
    if properties.get("consumer", {}).get("properties", {}).get("mega_routes", {}).get("const") != bridge["consumer"]["mega_routes"]:
        fail("source bridge schema route contract drifted")


def check_remote(bridge: dict):
    provider = bridge["provider"]
    source = bridge["source_contract"]

    for path, key in (
        (provider["module"], "module_blob_sha"),
        (provider["schema"], "schema_blob_sha"),
    ):
        data = remote_bytes(provider, path)
        actual = git_blob_sha(data)
        if actual != provider[key]:
            fail(f"remote provider pin mismatch for {path}: expected {provider[key]}, got {actual}")

    contract_data = remote_bytes(source, source["path"])
    if git_blob_sha(contract_data) != source["blob_sha"]:
        fail("source bridge contract blob pin mismatch")
    schema_data = remote_bytes(source, source["schema"])
    if git_blob_sha(schema_data) != source["schema_blob_sha"]:
        fail("source bridge schema blob pin mismatch")

    contract = json.loads(contract_data)
    schema = json.loads(schema_data)
    check_source_contract(contract, bridge)
    check_bridge_schema(schema, bridge)

    operating_schema = json.loads(remote_bytes(provider, provider["schema"]))
    if operating_schema["properties"]["schema_version"]["const"] != bridge["compatibility"]["operating_loop_schema_version"]:
        fail("remote operating-loop schema version mismatch")
    if operating_schema["properties"]["phases"]["required"] != bridge["phase_order"]:
        fail("remote phase contract mismatch")
    if operating_schema["properties"]["evidence_state"]["enum"] != bridge["evidence_states"]:
        fail("remote evidence vocabulary mismatch")
    if operating_schema["properties"]["outcome_status"]["enum"] != bridge["outcome_statuses"]:
        fail("remote outcome vocabulary mismatch")
    if operating_schema["properties"]["status"]["enum"] != list(bridge["status_map"].values()):
        fail("remote status vocabulary mismatch")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--remote",
        action="store_true",
        help="retrieve both pinned source contracts and provider artifacts",
    )
    args = parser.parse_args()
    try:
        bridge = load(BRIDGE)
        check_local(bridge)
        if args.remote:
            check_remote(bridge)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        json.dumps(
            {
                "ok": True,
                "remote_verified": args.remote,
                "provider_ref": bridge["provider"]["ref"],
                "source_contract_ref": bridge["source_contract"]["ref"],
                "combo": bridge["consumer"]["combo_id"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
