import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_genius_mastery_bridge.py"
spec = importlib.util.spec_from_file_location("bridge_validator", SCRIPT)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


def current_contract_from_bridge(bridge: dict) -> dict:
    provider = dict(bridge["provider"])
    provider.pop("raw_base")
    return {
        "$schema": "../schemas/mega-skills-bridge.schema.json",
        "schema_version": bridge["schema_version"],
        "contract_id": bridge["contract_id"],
        "provider": provider,
        "consumer": bridge["consumer"],
        "compatibility": bridge["compatibility"],
        "phase_order": bridge["phase_order"],
        "evidence_states": bridge["evidence_states"],
        "outcome_statuses": bridge["outcome_statuses"],
        "status_map": bridge["status_map"],
        "invariants": bridge["invariants"],
    }


def authority_fixture():
    bridge = validator.load(validator.BRIDGE)
    contract_data = (
        json.dumps(current_contract_from_bridge(bridge), separators=(",", ":")) + "\n"
    ).encode()
    schema_data = b'{"schema":"current-authority-fixture"}\n'
    bridge = copy.deepcopy(bridge)
    bridge["source_contract"]["blob_sha"] = validator.git_blob_sha(contract_data)
    bridge["source_contract"]["schema_blob_sha"] = validator.git_blob_sha(schema_data)
    return bridge, contract_data, schema_data


def test_current_authority_can_intentionally_pin_older_provider_ref():
    bridge, contract_data, schema_data = authority_fixture()
    head = "a" * 40
    assert bridge["provider"]["ref"] != head
    state = validator.check_freshness_state(bridge, contract_data, schema_data, head)
    assert state["source_ref_is_authority_head"] is False
    assert state["provider_ref"] == bridge["provider"]["ref"]
    assert (
        state["freshness_basis"]
        == "current_upstream_contract_content_and_authorization"
    )


def test_stale_contract_blob_is_rejected_even_if_pin_is_structurally_valid():
    bridge, contract_data, schema_data = authority_fixture()
    bridge["source_contract"]["blob_sha"] = "0" * 40
    with pytest.raises(
        ValueError,
        match="stale-provider provenance: current upstream bridge contract blob",
    ):
        validator.check_freshness_state(bridge, contract_data, schema_data, "a" * 40)


def test_current_authority_provider_change_rejects_old_provider_pin():
    bridge, contract_data, schema_data = authority_fixture()
    contract = json.loads(contract_data)
    contract["provider"]["ref"] = "b" * 40
    changed = (json.dumps(contract, separators=(",", ":")) + "\n").encode()
    bridge["source_contract"]["blob_sha"] = validator.git_blob_sha(changed)
    with pytest.raises(ValueError, match="source contract provider mismatch for ref"):
        validator.check_freshness_state(bridge, changed, schema_data, "a" * 40)
