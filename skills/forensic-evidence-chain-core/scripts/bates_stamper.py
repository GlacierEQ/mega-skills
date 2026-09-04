#!/usr/bin/env python3
"""Cryptographic Bates serial planner and contiguity verifier.

Assigns monotonic Bates serials ("<PREFIX>-<SERIAL>") to evidentiary items and
verifies existing plans for contiguity, collisions, and format drift. Serials
are assigned to derivative copies only; original media are never modified.
"""

import argparse
import json
import re
import sys
from pathlib import Path

SERIAL_PATTERN = re.compile(r"^([A-Z0-9][A-Z0-9_-]{0,31})-(\d{4,8})$")
DEFAULT_START = 1
DEFAULT_WIDTH = 6


def load_schema_defaults(path):
    defaults = {"start": DEFAULT_START, "width": DEFAULT_WIDTH}
    if not path:
        return defaults
    text = Path(path).read_text(encoding="utf-8")
    try:
        import yaml
        data = yaml.safe_load(text) or {}
    except ImportError:
        data = {}
        for line in text.splitlines():
            key, sep, value = line.partition(":")
            if sep and not line.startswith((" ", "#", "-")):
                data[key.strip()] = value.strip()
    for key in ("default_start", "default_width"):
        if key in data:
            try:
                defaults[key.replace("default_", "")] = int(data[key])
            except (TypeError, ValueError):
                continue
    return defaults


def assign_serials(paths, prefix, start=DEFAULT_START, width=DEFAULT_WIDTH):
    """Assign monotonic serials to a sorted set of relative paths."""
    plan = []
    serial = start
    for rel in sorted(paths):
        plan.append({"path": rel, "bates": f"{prefix}-{serial:0{width}d}"})
        serial += 1
    return plan


def validate_plan(plan):
    """Validate format, collisions, and contiguity of a Bates plan."""
    problems = []
    seen = {}
    serials = []
    for row in plan:
        bates = str(row.get("bates", ""))
        match = SERIAL_PATTERN.match(bates)
        if match is None:
            problems.append({"kind": "invalid_format", "bates": bates, "path": row.get("path")})
            continue
        if bates in seen:
            problems.append({"kind": "collision", "bates": bates,
                             "paths": [seen[bates], row.get("path")]})
        seen[bates] = row.get("path")
        serials.append(int(match.group(2)))
    gaps = []
    if serials:
        ordered = sorted(serials)
        expected = list(range(ordered[0], ordered[-1] + 1))
        gaps = sorted(set(expected) - set(ordered))
        if gaps:
            problems.append({"kind": "contiguity_gap", "missing_serials": gaps})
    return {
        "schema_version": 1,
        "entries": len(plan),
        "unique_serials": len(seen),
        "contiguous": not gaps and all(p["kind"] != "collision" for p in problems),
        "problems": problems,
        "mode": "derivative-stamping-plan",
        "original_media_modified": False,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in (Path(__file__).stem, Path(__file__).name):
        argv = argv[1:]
    parser = argparse.ArgumentParser(description="Bates serial planner and verifier.")
    parser.add_argument("--manifest", help="Digest manifest JSON providing file paths.")
    parser.add_argument("--prefix", default="EXHIBIT")
    parser.add_argument("--start", type=int)
    parser.add_argument("--width", type=int)
    parser.add_argument("--schema", help="Optional bates_serial_schema.yaml for defaults.")
    parser.add_argument("--out")
    parser.add_argument("--verify", help="Verify an existing Bates plan JSON.")
    args = parser.parse_args(argv)

    if args.verify:
        plan = json.loads(Path(args.verify).read_text(encoding="utf-8"))
        entries = plan.get("plan", plan if isinstance(plan, list) else [])
        report = validate_plan(entries)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["contiguous"] and not report["problems"] else 1

    if not args.manifest:
        parser.error("--manifest is required when not verifying")
    defaults = load_schema_defaults(args.schema)
    start = args.start if args.start is not None else defaults["start"]
    width = args.width if args.width is not None else defaults["width"]
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    paths = [entry["path"] for entry in manifest.get("files", [])]
    plan = assign_serials(paths, args.prefix, start, width)
    document = {
        "schema_version": 1,
        "prefix": args.prefix,
        "start": start,
        "width": width,
        "mode": "derivative-stamping-plan",
        "original_media_modified": False,
        "plan": plan,
        "validation": validate_plan(plan),
    }
    text = json.dumps(document, indent=2, sort_keys=True)
    if args.out:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
