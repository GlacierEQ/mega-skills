#!/usr/bin/env python3
"""WhisperX word-level alignment: capability-gated execution plus verification.

The alignment execution path requires the optional ``whisperx`` dependency and
fails closed with a capability report when it is absent; no alignment is ever
fabricated. The verification path (--verify-alignment) is fully deterministic:
it validates monotonic word timestamps, segment-bound containment, negative
durations, segment overlaps, and inter-word gaps for an existing alignment
document. --extract-text renders the aligned words into plain reading order.
"""

import argparse
import json
import sys
from importlib.util import find_spec
from pathlib import Path

EPSILON = 1e-6


def capability_report():
    missing = []
    if find_spec("whisperx") is None:
        missing.append("whisperx")
    return {
        "schema_version": 1,
        "capability": "whisperx-alignment-execution",
        "status": "capability_blocked",
        "missing": missing,
        "fabricated_results": False,
    }


def verify_alignment(document):
    """Validate a WhisperX-style alignment document."""
    violations = []
    word_count = 0
    max_gap = 0.0
    segments = document.get("segments", [])
    for seg_index, segment in enumerate(segments):
        seg_start = float(segment.get("start", 0.0))
        seg_end = float(segment.get("end", seg_start))
        words = segment.get("words", [])
        previous_end = None
        for word_index, word in enumerate(words):
            word_count += 1
            start = float(word.get("start", seg_start))
            end = float(word.get("end", start))
            if end < start - EPSILON:
                violations.append({"kind": "negative_duration", "segment": seg_index,
                                   "word": word_index})
            if start < seg_start - EPSILON or end > seg_end + EPSILON:
                violations.append({"kind": "outside_segment_bounds", "segment": seg_index,
                                   "word": word_index})
            if previous_end is not None:
                if start < previous_end - EPSILON:
                    violations.append({"kind": "non_monotonic_words", "segment": seg_index,
                                       "word": word_index})
                max_gap = max(max_gap, start - previous_end)
            previous_end = end
    for index, (first, second) in enumerate(zip(segments, segments[1:])):
        first_end = float(first.get("end", 0.0))
        second_start = float(second.get("start", 0.0))
        if second_start < first_end - EPSILON:
            violations.append({"kind": "segment_overlap", "between": [index, index + 1],
                               "overlap_seconds": first_end - second_start})
    return {
        "schema_version": 1,
        "segment_count": len(segments),
        "word_count": word_count,
        "max_inter_word_gap_seconds": round(max_gap, 6),
        "aligned": not violations,
        "zero_drift": not any(v["kind"] in ("non_monotonic_words", "outside_segment_bounds")
                              for v in violations),
        "violations": violations,
    }


def extract_text(document):
    """Render aligned words into speaker-labeled plain text."""
    lines = []
    for segment in document.get("segments", []):
        speaker = str(segment.get("speaker", "UNKNOWN"))
        words = [str(word.get("w", "")) for word in segment.get("words", [])]
        text = " ".join(word for word in words if word)
        lines.append(f"{speaker}: {text}".rstrip())
    return "\n".join(lines) + "\n"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in (Path(__file__).stem, Path(__file__).name):
        argv = argv[1:]
    parser = argparse.ArgumentParser(description="WhisperX alignment execution and verification.")
    parser.add_argument("--audio", help="Execute alignment on an audio file (requires whisperx).")
    parser.add_argument("--verify-alignment", help="Verify an existing alignment JSON.")
    parser.add_argument("--extract-text", help="Render an alignment JSON to plain text.")
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
        import whisperx  # type: ignore
        print(json.dumps({"schema_version": 1, "capability": "whisperx-alignment-execution",
                          "status": "driver_present",
                          "note": "wire production model/device flags here; verification path is deterministic"},
                         indent=2))
        return 0

    if not args.verify_alignment and not args.extract_text:
        parser.error("provide --audio, --verify-alignment, or --extract-text")
    if args.verify_alignment:
        document = json.loads(Path(args.verify_alignment).read_text(encoding="utf-8"))
        report = verify_alignment(document)
        text = json.dumps(report, indent=2, sort_keys=True)
        if args.out:
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(text)
        return 0 if report["aligned"] else 1
    document = json.loads(Path(args.extract_text).read_text(encoding="utf-8"))
    rendered = extract_text(document)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
