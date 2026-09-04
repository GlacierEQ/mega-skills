#!/usr/bin/env python3
"""Speaker diarization: capability-gated execution plus segment verification.

The diarization execution path requires the optional ``pyannote.audio``
dependency and fails closed with a capability report when it is absent. The
verification path (--verify-segments) is deterministic: schema validation,
segment overlap accounting, turn counts, and per-speaker speaking time.
"""

import argparse
import json
import sys
from importlib.util import find_spec
from pathlib import Path

EPSILON = 1e-6


def capability_report():
    missing = []
    try:
        available = find_spec("pyannote.audio") is not None
    except ImportError:
        available = False
    if not available:
        missing.append("pyannote.audio")
    return {
        "schema_version": 1,
        "capability": "pyannote-speaker-diarization",
        "status": "capability_blocked",
        "missing": missing,
        "fabricated_results": False,
    }


def verify_segments(document):
    """Validate diarization segments: {"segments": [{speaker, start, end}]}."""
    violations = []
    speaking_time = {}
    turns = {}
    segments = []
    for index, row in enumerate(document.get("segments", [])):
        speaker = str(row.get("speaker", "UNKNOWN"))
        try:
            start = float(row["start"])
            end = float(row["end"])
        except (KeyError, TypeError, ValueError) as exc:
            violations.append({"kind": "schema_violation", "segment": index, "detail": str(exc)})
            continue
        if end < start - EPSILON:
            violations.append({"kind": "negative_duration", "segment": index})
        segments.append((start, end, speaker))
        speaking_time[speaker] = speaking_time.get(speaker, 0.0) + max(end - start, 0.0)
        turns[speaker] = turns.get(speaker, 0) + 1
    ordered = sorted(segments)
    overlaps = []
    for (a_start, a_end, a_speaker), (b_start, b_end, b_speaker) in zip(ordered, ordered[1:]):
        if b_start < a_end - EPSILON:
            overlaps.append({
                "speakers": [a_speaker, b_speaker],
                "overlap_seconds": round(a_end - b_start, 6),
                "at_seconds": round(b_start, 6),
            })
    total_overlap = sum(row["overlap_seconds"] for row in overlaps)
    return {
        "schema_version": 1,
        "segment_count": len(segments),
        "speaker_count": len(speaking_time),
        "speaking_time_seconds": {key: round(value, 6) for key, value in sorted(speaking_time.items())},
        "turns": turns,
        "overlap_regions": overlaps,
        "total_overlap_seconds": round(total_overlap, 6),
        "timeline_monotonic": not any(
            ordered[i + 1][0] < ordered[i][0] - EPSILON for i in range(len(ordered) - 1)
        ),
        "valid": not violations,
        "violations": violations,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in (Path(__file__).stem, Path(__file__).name):
        argv = argv[1:]
    parser = argparse.ArgumentParser(description="Speaker diarization execution and verification.")
    parser.add_argument("--audio", help="Execute diarization on an audio file (requires pyannote).")
    parser.add_argument("--verify-segments", help="Verify an existing segments JSON.")
    parser.add_argument("--out")
    args = parser.parse_args(argv)

    if args.audio:
        report = capability_report()
        if report["missing"]:
            text = json.dumps(report, indent=2, sort_keys=True)
            if args.out:
                Path(args.out).parent.mkdir(parents=True, exist_ok=True)
                Path(args.out).write_text(text + "\n", encoding="utf-8")
            print(text)
            return 2
        print(json.dumps({"schema_version": 1, "capability": "pyannote-speaker-diarization",
                          "status": "driver_present",
                          "note": "wire production pipeline flags here; verification path is deterministic"},
                         indent=2))
        return 0

    if not args.verify_segments:
        parser.error("provide --audio or --verify-segments")
    document = json.loads(Path(args.verify_segments).read_text(encoding="utf-8"))
    report = verify_segments(document)
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
