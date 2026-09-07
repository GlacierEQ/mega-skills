#!/usr/bin/env python3
"""Behavioral tests for mega-agent-memory-systems composition."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

MEGA_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = MEGA_DIR.parent.parent
ENTRYPOINT = MEGA_DIR / "skill.py"
ATOMIC_DIR = MEGA_DIR.parent / "agent-memory-systems"


def _run(*args: str):
    return subprocess.run(
        [sys.executable, str(ENTRYPOINT), *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def test_required_composed_engine_exists():
    assert ENTRYPOINT.exists()
    assert (ATOMIC_DIR / "skill.py").exists()
    assert (ATOMIC_DIR / "continuity.py").exists()


def test_verify_is_behavioral_not_markdown_hash_ceremony():
    result = _run("verify", "--json")
    assert result.returncode == 0, result.stderr
    receipt = json.loads(result.stdout)

    assert receipt["status"] == "BEHAVIOR_VERIFIED"
    assert receipt["continuation_schema_version"] == "2.0.0"
    assert "atomic_persist" in receipt["checks"]
    assert "integrity_reload" in receipt["checks"]
    assert "verified_transition_receipt" in receipt["checks"]
    assert "hydration_cursor_verified" in receipt["checks"]
    assert receipt["projection_digest"] != receipt["previous_digest"]


def test_mega_entrypoint_can_initialize_and_hydrate_continuation(tmp_path: Path):
    state = tmp_path / "continuation.json"

    created = _run(
        "init",
        str(state),
        "--mission-id",
        "mega-test",
        "--intent",
        "Resume without reconstruction.",
        "--target",
        "Hydrate from durable continuation state.",
    )
    assert created.returncode == 0, created.stderr
    init_receipt = json.loads(created.stdout)
    assert init_receipt["status"] == "initialized"

    hydrated = _run("hydrate", str(state))
    assert hydrated.returncode == 0, hydrated.stderr
    packet = json.loads(hydrated.stdout)

    assert packet["mission"]["mission_id"] == "mega-test"
    assert packet["mission"]["operator_intent"] == "Resume without reconstruction."
    assert packet["state_digest"] == init_receipt["state_digest"]
    assert packet["next_action"]["action"]
    assert "Do not treat the packet as a substitute" in packet["boot_rule"]


def test_unknown_command_does_not_false_positive():
    result = _run("definitely-not-a-command")
    assert result.returncode != 0
    assert "Unknown command" in result.stderr
