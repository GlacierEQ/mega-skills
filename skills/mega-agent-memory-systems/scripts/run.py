#!/usr/bin/env python3
"""Behavioral verifier for mega-agent-memory-systems."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

MEGA_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = MEGA_DIR.parent
ATOMIC_DIR = SKILLS_DIR / "agent-memory-systems"

if str(ATOMIC_DIR) not in sys.path:
    sys.path.insert(0, str(ATOMIC_DIR))

from continuity import (
    add_peer,
    add_source,
    hydration_packet,
    load_projection,
    new_projection,
    record_transition,
    save_projection,
    set_next_action,
    validate_projection,
)


def verify_behavior() -> dict[str, object]:
    checks: list[str] = []

    with tempfile.TemporaryDirectory(prefix="mega-agent-memory-verify-") as tmp:
        state_path = Path(tmp) / "continuation.json"

        state = new_projection(
            mission_id="selftest",
            operator_intent="Verify durable continuation behavior.",
            active_target="Complete a source-backed persistence and hydration round-trip.",
        )
        checks.append("projection_created")

        source_id = add_source(
            state,
            provider="selftest",
            locator="memory://behavioral-verification",
            scope="self-test transition evidence",
            truth_state="behavior_verified",
            source_id="src-selftest",
        )
        add_peer(
            state,
            provider="peer-selftest",
            locator="projection://peer",
            relationship="peer",
            revision="1",
        )
        set_next_action(
            state,
            action="Record and persist the verified self-test transition.",
            why="Source-bearing evidence is attached; persistence is the next dependency.",
            critical_path=["record transition", "persist", "reload", "hydrate"],
        )
        checks.append("source_and_peer_bound")

        first_digest = save_projection(state_path, state)
        checks.append("atomic_persist")

        loaded = load_projection(state_path)
        validate_projection(loaded)
        if loaded["state_digest"] != first_digest:
            raise RuntimeError("persisted digest changed during reload")
        checks.append("integrity_reload")

        receipt_id = record_transition(
            loaded,
            action="Verify continuation round-trip",
            observed_result="Projection persisted, reloaded, and retained source-bound state.",
            after_state="continuation round-trip behavior verified",
            evidence_refs=[source_id],
            completed_description="Durable continuation round-trip verified",
            next_action={
                "action": "Hydrate the persisted projection.",
                "why": "The verified snapshot must produce a usable continuation packet.",
                "requires_authority": False,
                "blocked_by": [],
                "critical_path": ["hydrate", "assert continuation cursor"],
            },
        )
        second_digest = save_projection(
            state_path,
            loaded,
            previous_digest=first_digest,
        )
        checks.append("verified_transition_receipt")

        reloaded = load_projection(state_path)
        packet = hydration_packet(reloaded)

        if packet["last_verified_state"] != "continuation round-trip behavior verified":
            raise RuntimeError("hydration did not preserve last verified state")
        if packet["state_digest"] != second_digest:
            raise RuntimeError("hydration packet digest does not match persisted state")
        if not packet["source_pointers"]:
            raise RuntimeError("hydration lost source pointers")
        if not packet["peer_projections"]:
            raise RuntimeError("hydration lost peer projections")
        if not packet["transition_receipts"]:
            raise RuntimeError("hydration lost verification receipts")
        checks.append("hydration_cursor_verified")

        return {
            "skill": "mega-agent-memory-systems",
            "status": "BEHAVIOR_VERIFIED",
            "continuation_schema_version": reloaded["schema_version"],
            "projection_digest": second_digest,
            "previous_digest": reloaded["lineage"]["previous_digest"],
            "receipt_id": receipt_id,
            "checks": checks,
            "atomic_engine": str(ATOMIC_DIR),
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Behaviorally verify mega-agent-memory-systems continuity composition."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON receipt.")
    args = parser.parse_args(argv)

    try:
        receipt = verify_behavior()
        if args.json:
            print(json.dumps(receipt, indent=2, sort_keys=True))
        else:
            print(
                "mega-agent-memory-systems: BEHAVIOR_VERIFIED "
                f"[{', '.join(receipt['checks'])}]"
            )
        return 0
    except Exception as exc:
        receipt = {
            "skill": "mega-agent-memory-systems",
            "status": "FAILED",
            "error": str(exc),
            "atomic_engine": str(ATOMIC_DIR),
        }
        if args.json:
            print(json.dumps(receipt, indent=2, sort_keys=True))
        else:
            print(f"mega-agent-memory-systems: FAILED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
