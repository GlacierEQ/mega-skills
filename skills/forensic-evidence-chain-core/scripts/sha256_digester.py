#!/usr/bin/env python3
"""Deterministic SHA-256 digest engine for evidentiary file trees.

Computes NIST-standard SHA-256 digests in 64KB chunks over every file under a
root directory, emits a sorted manifest, and verifies a live tree against a
previously recorded manifest. Original media are read, never modified.
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CHUNK_SIZE = 65536  # 64KB
ALGORITHM = "sha256"


def compute_sha256(path):
    """Compute a deterministic SHA-256 digest in 64KB chunks."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest_tree(root, include_hidden=False):
    """Digest every file under root. Returns records sorted by relative path."""
    root = Path(root)
    if not root.is_dir():
        raise SystemExit(f"digest root is not a directory: {root}")
    records = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        if not include_hidden and any(part.startswith(".") for part in Path(rel).parts):
            continue
        stat = path.stat()
        records.append({
            "path": rel,
            "sha256": compute_sha256(path),
            "size_bytes": stat.st_size,
            "mtime_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        })
    return records


def build_manifest(root, records):
    return {
        "schema_version": 1,
        "algorithm": ALGORITHM,
        "chunk_size": CHUNK_SIZE,
        "root": str(root),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "file_count": len(records),
        "files": records,
    }


def verify_against_manifest(root, manifest):
    """Re-digest the tree and diff against a recorded manifest."""
    recorded = {entry["path"]: entry["sha256"] for entry in manifest.get("files", [])}
    current = {entry["path"]: entry["sha256"] for entry in digest_tree(root)}
    shared = recorded.keys() & current.keys()
    report = {
        "missing": sorted(p for p in recorded if p not in current),
        "added": sorted(p for p in current if p not in recorded),
        "mismatched": sorted(p for p in shared if recorded[p] != current[p]),
        "checked": len(shared),
    }
    report["verified"] = not report["missing"] and not report["added"] and not report["mismatched"]
    return report


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in (Path(__file__).stem, Path(__file__).name):
        argv = argv[1:]
    parser = argparse.ArgumentParser(description="SHA-256 digest engine (64KB chunks).")
    parser.add_argument("--root", required=True, help="Directory tree to digest.")
    parser.add_argument("--out", help="Write manifest JSON to this path.")
    parser.add_argument("--verify", help="Verify the tree against this manifest JSON.")
    parser.add_argument("--include-hidden", action="store_true")
    args = parser.parse_args(argv)

    if args.verify:
        manifest = json.loads(Path(args.verify).read_text(encoding="utf-8"))
        report = verify_against_manifest(args.root, manifest)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["verified"] else 1

    manifest = build_manifest(args.root, digest_tree(args.root, args.include_hidden))
    text = json.dumps(manifest, indent=2, sort_keys=True)
    if args.out:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
