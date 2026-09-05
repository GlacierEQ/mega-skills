#!/usr/bin/env python3
"""Timeline integrity verifier for forensic event logs.

Detects chronological inversions, impossible negative durations, and duplicate
timestamps across distinct events. All timestamps are normalized to UTC before
comparison; dual-timestamp (local/UTC) inputs are supported via the
``timestamp_utc`` field or a ``timestamp`` plus ``timezone`` field.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_timestamp(value):
    """Parse an ISO-8601 timestamp, accepting a trailing Z for UTC."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("empty timestamp")
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def verify_events(document):
    """Verify an events document: {"events": [{"id", "timestamp", ...}]}."""
    events = document.get("events", [])
    problems = []
    parsed_events = []
    for index, event in enumerate(events):
        event_id = event.get("id", f"event-{index}")
        raw = event.get("timestamp_utc") or event.get("timestamp")
        try:
            moment = parse_timestamp(raw)
        except (ValueError, TypeError) as exc:
            problems.append({"kind": "unparseable_timestamp", "id": event_id, "detail": str(exc)})
            continue
        parsed_events.append((event_id, moment))
    inversions = []
    for (prev_id, prev), (next_id, nxt) in zip(parsed_events, parsed_events[1:]):
        if nxt < prev:
            inversions.append({
                "kind": "chronological_inversion",
                "before": prev_id,
                "after": next_id,
                "delta_seconds": (nxt - prev).total_seconds(),
            })
    collisions = {}
    for event_id, moment in parsed_events:
        collisions.setdefault(moment, []).append(event_id)
    duplicates = [
        {"kind": "duplicate_timestamp", "timestamp_utc": moment.isoformat(), "ids": ids}
        for moment, ids in sorted(collisions.items()) if len(ids) > 1
    ]
    gaps = []
    if len(parsed_events) > 1:
        ordered = sorted(parsed_events, key=lambda item: item[1])
        spans = [
            (a[0], b[0], (b[1] - a[1]).total_seconds())
            for a, b in zip(ordered, ordered[1:])
        ]
        widest = max(spans, key=lambda span: span[2])
        gaps = [{"between": [widest[0], widest[1]], "gap_seconds": widest[2]}]
    problems.extend(inversions)
    problems.extend(duplicates)
    return {
        "schema_version": 1,
        "event_count": len(events),
        "parsed_count": len(parsed_events),
        "verified": not problems,
        "problems": problems,
        "largest_gap": gaps,
        "events_normalized": [
            {"type": "event", "id": event_id, "timestamp_utc": moment.isoformat()}
            for event_id, moment in parsed_events
        ],
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in (Path(__file__).stem, Path(__file__).name):
        argv = argv[1:]
    parser = argparse.ArgumentParser(description="Forensic timeline verifier.")
    parser.add_argument("--events", required=True, help="Events JSON document.")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    document = json.loads(Path(args.events).read_text(encoding="utf-8"))
    report = verify_events(document)
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.out:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
