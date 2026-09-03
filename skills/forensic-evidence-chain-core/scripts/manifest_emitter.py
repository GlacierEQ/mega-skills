#!/usr/bin/env python3
"""Tamper-evident manifest emitter for forensic evidence chains.

Combines digest, Bates, anomaly, and timeline reports into a single
BATES_MANIFEST.json whose entries are hash-chained (each entry commits to its
predecessor), plus a merged 00_FORENSIC_MASTER_TIMELINE.json. Any later edit
to any entry breaks the chain root.
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

GENESIS = "0" * 64


def _canonical(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def chain_entries(entries):
    """Attach a rolling hash chain to an ordered list of entries."""
    previous = GENESIS
    chained = []
    for entry in entries:
        body = dict(entry)
        body["previous_hash"] = previous
        entry_hash = hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()
        body["entry_hash"] = entry_hash
        chained.append(body)
        previous = entry_hash
    root = hashlib.sha256("".join(
        row["entry_hash"] for row in chained
    ).encode("utf-8")).hexdigest()
    return chained, root


def verify_chain(chained, expected_root):
    """Recompute the rolling chain and compare against the recorded root."""
    recomputed, root = chain_entries([
        {key: value for key, value in row.items() if key not in ("previous_hash", "entry_hash")}
        for row in chained
    ])
    matches = [a["entry_hash"] == b["entry_hash"] for a, b in zip(recomputed, chained)]
    return {
        "entries_checked": len(chained),
        "chain_intact": all(matches) and len(recomputed) == len(chained),
        "root_match": root == expected_root,
        "recomputed_root": root,
    }


def emit(digests, bates, anomalies, timestamps):
    bates_by_path = {row["path"]: row["bates"] for row in (bates or {}).get("plan", [])}
    entries = []
    for record in (digests or {}).get("files", []):
        entries.append({
            "type": "exhibit",
            "path": record["path"],
            "sha256": record["sha256"],
            "size_bytes": record.get("size_bytes"),
            "mtime_utc": record.get("mtime_utc"),
            "bates": bates_by_path.get(record["path"]),
        })
    for anomaly in (anomalies or {}).get("anomalies", []):
        entries.append({"type": "anomaly", **anomaly})
    chained, root = chain_entries(entries)
    manifest = {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "entry_count": len(chained),
        "chain_root_sha256": root,
        "timestamp_report": timestamps or {"verified": None, "note": "no event log supplied"},
        "entries": chained,
    }
    timeline_rows = []
    for record in (digests or {}).get("files", []):
        timeline_rows.append({
            "type": "file_witness",
            "id": record["path"],
            "timestamp_utc": record.get("mtime_utc"),
            "sha256": record["sha256"],
        })
    for event in (timestamps or {}).get("events_normalized", []):
        timeline_rows.append(event)
    timeline_rows.sort(key=lambda row: str(row.get("timestamp_utc")))
    timeline = {
        "schema_version": 1,
        "row_count": len(timeline_rows),
        "rows": timeline_rows,
    }
    return manifest, timeline


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in (Path(__file__).stem, Path(__file__).name):
        argv = argv[1:]
    parser = argparse.ArgumentParser(description="Hash-chained manifest emitter.")
    parser.add_argument("--digests")
    parser.add_argument("--bates")
    parser.add_argument("--anomalies")
    parser.add_argument("--timestamps")
    parser.add_argument("--out")
    parser.add_argument("--timeline")
    parser.add_argument("--verify", help="Verify an existing BATES_MANIFEST.json chain.")
    args = parser.parse_args(argv)

    if args.verify:
        manifest = json.loads(Path(args.verify).read_text(encoding="utf-8"))
        report = verify_chain(manifest.get("entries", []), manifest.get("chain_root_sha256", ""))
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["chain_intact"] and report["root_match"] else 1

    def load(path):
        return json.loads(Path(path).read_text(encoding="utf-8")) if path else None

    if not args.out:
        parser.error("--out is required when not verifying")

    manifest, timeline = emit(load(args.digests), load(args.bates),
                              load(args.anomalies), load(args.timestamps))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.timeline:
        target = Path(args.timeline)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(timeline, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(out), "entries": manifest["entry_count"],
                      "chain_root_sha256": manifest["chain_root_sha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
