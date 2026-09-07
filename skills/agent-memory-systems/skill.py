#!/usr/bin/env python3
"""Executable continuation-state interface for agent-memory-systems."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from continuity import (
    ContinuityError,
    add_source,
    hydration_packet,
    load_projection,
    mark_complete,
    new_projection,
    record_transition,
    save_projection,
    set_next_action,
    validate_projection,
)


def _dump(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-memory-systems",
        description="Persist and hydrate source-bearing continuation projections.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Create a new continuation projection.")
    init.add_argument("state_file")
    init.add_argument("--mission-id", required=True)
    init.add_argument("--intent", required=True)
    init.add_argument("--target", required=True)

    validate = sub.add_parser("validate", help="Validate state and its integrity digest.")
    validate.add_argument("state_file")

    hydrate = sub.add_parser(
        "hydrate",
        help="Emit the minimal continuation packet needed to resume logical progress.",
    )
    hydrate.add_argument("state_file")

    source = sub.add_parser("add-source", help="Attach a provenance-bound source pointer.")
    source.add_argument("state_file")
    source.add_argument("--provider", required=True)
    source.add_argument("--locator", required=True)
    source.add_argument("--scope", required=True)
    source.add_argument("--truth-state", required=True)
    source.add_argument("--revision")
    source.add_argument("--content-hash")
    source.add_argument("--source-id")

    next_cmd = sub.add_parser("set-next", help="Set the current strongest next action.")
    next_cmd.add_argument("state_file")
    next_cmd.add_argument("--action", required=True)
    next_cmd.add_argument("--why", required=True)
    next_cmd.add_argument("--requires-authority", action="store_true")
    next_cmd.add_argument("--blocked-by", action="append", default=[])
    next_cmd.add_argument("--critical-path", action="append")

    transition = sub.add_parser(
        "transition",
        help="Record a verified state transition with source-backed evidence.",
    )
    transition.add_argument("state_file")
    transition.add_argument("--action", required=True)
    transition.add_argument("--result", required=True)
    transition.add_argument("--after-state", required=True)
    transition.add_argument("--evidence-ref", action="append", required=True)
    transition.add_argument("--completed-description")
    transition.add_argument("--next-action")
    transition.add_argument("--next-why")
    transition.add_argument("--next-requires-authority", action="store_true")
    transition.add_argument("--next-blocked-by", action="append", default=[])
    transition.add_argument("--next-critical-path", action="append")

    complete = sub.add_parser("complete", help="Mark a mission complete using verified evidence.")
    complete.add_argument("state_file")
    complete.add_argument("--final-state", required=True)
    complete.add_argument("--evidence-ref", action="append", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "init":
            state = new_projection(
                mission_id=args.mission_id,
                operator_intent=args.intent,
                active_target=args.target,
            )
            digest = save_projection(args.state_file, state)
            _dump({"status": "initialized", "state_file": args.state_file, "state_digest": digest})
            return 0

        state = load_projection(args.state_file)

        if args.command == "validate":
            validate_projection(state)
            _dump({
                "status": "valid",
                "projection_id": state["projection_id"],
                "state_digest": state["state_digest"],
            })
            return 0

        if args.command == "hydrate":
            _dump(hydration_packet(state))
            return 0

        if args.command == "add-source":
            prior = state["state_digest"]
            source_id = add_source(
                state,
                provider=args.provider,
                locator=args.locator,
                scope=args.scope,
                truth_state=args.truth_state,
                revision=args.revision,
                content_hash=args.content_hash,
                source_id=args.source_id,
            )
            digest = save_projection(args.state_file, state, previous_digest=prior)
            _dump({"status": "source_added", "source_id": source_id, "state_digest": digest})
            return 0

        if args.command == "set-next":
            prior = state["state_digest"]
            set_next_action(
                state,
                action=args.action,
                why=args.why,
                requires_authority=args.requires_authority,
                blocked_by=args.blocked_by,
                critical_path=args.critical_path,
            )
            digest = save_projection(args.state_file, state, previous_digest=prior)
            _dump({"status": "next_action_set", "state_digest": digest})
            return 0

        if args.command == "transition":
            prior = state["state_digest"]
            next_action = None
            if args.next_action:
                if not args.next_why:
                    raise ContinuityError("--next-why is required when --next-action is supplied")
                next_action = {
                    "action": args.next_action,
                    "why": args.next_why,
                    "requires_authority": args.next_requires_authority,
                    "blocked_by": args.next_blocked_by,
                    "critical_path": args.next_critical_path,
                }
            receipt_id = record_transition(
                state,
                action=args.action,
                observed_result=args.result,
                after_state=args.after_state,
                evidence_refs=args.evidence_ref,
                completed_description=args.completed_description,
                next_action=next_action,
            )
            digest = save_projection(args.state_file, state, previous_digest=prior)
            _dump({
                "status": "transition_verified",
                "receipt_id": receipt_id,
                "state_digest": digest,
            })
            return 0

        if args.command == "complete":
            prior = state["state_digest"]
            receipt_id = mark_complete(
                state,
                final_state=args.final_state,
                evidence_refs=args.evidence_ref,
            )
            digest = save_projection(args.state_file, state, previous_digest=prior)
            _dump({
                "status": "complete",
                "receipt_id": receipt_id,
                "state_digest": digest,
            })
            return 0

        raise ContinuityError(f"unsupported command: {args.command}")
    except (ContinuityError, OSError, json.JSONDecodeError) as exc:
        _dump({"status": "error", "error": str(exc)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
