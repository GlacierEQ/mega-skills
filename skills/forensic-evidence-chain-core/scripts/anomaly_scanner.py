#!/usr/bin/env python3
"""Forensic anomaly scanner for evidentiary directories.

Detects zero-byte files, extension/magic-number mismatches, world-writable
permission drift, and byte-identical duplicate families. Reports only; never
modifies the scanned media.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

CHUNK_SIZE = 65536

MAGIC_SIGNATURES = {
    ".pdf": [(0, b"%PDF-")],
    ".zip": [(0, b"PK\x03\x04")],
    ".png": [(0, b"\x89PNG\r\x1a\n")],
    ".jpg": [(0, b"\xff\xd8\xff")],
    ".jpeg": [(0, b"\xff\xd8\xff")],
    ".mp3": [(0, b"ID3"), (0, b"\xff\xfb"), (0, b"\xff\xf3"), (0, b"\xff\xf2")],
    ".m4a": [(4, b"ftyp")],
    ".mp4": [(4, b"ftyp")],
    ".mov": [(4, b"ftyp")],
}


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _magic_matches(path, signatures):
    try:
        with Path(path).open("rb") as handle:
            head = handle.read(16)
    except OSError as exc:
        return f"unreadable: {exc}"
    for offset, signature in signatures:
        if head[offset:offset + len(signature)] == signature:
            return None
    return f"magic mismatch: expected one of {len(signatures)} signatures"


def scan(root, include_hidden=False):
    """Scan a directory tree and return an anomaly report."""
    root = Path(root)
    if not root.is_dir():
        raise SystemExit(f"scan root is not a directory: {root}")
    anomalies = []
    by_hash = {}
    file_count = 0
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        if not include_hidden and any(part.startswith(".") for part in Path(rel).parts):
            continue
        file_count += 1
        stat = path.stat()
        if stat.st_size == 0:
            anomalies.append({"path": rel, "kind": "zero_byte", "detail": "file has no content"})
            by_hash.setdefault("empty", []).append(rel)
            continue
        suffix = path.suffix.lower()
        if suffix in MAGIC_SIGNATURES:
            mismatch = _magic_matches(path, MAGIC_SIGNATURES[suffix])
            if mismatch:
                anomalies.append({"path": rel, "kind": "magic_mismatch", "detail": mismatch})
        if stat.st_mode & 0o002:
            anomalies.append({"path": rel, "kind": "permission_drift",
                              "detail": "world-writable evidentiary file"})
        by_hash.setdefault(_sha256(path), []).append(rel)
    duplicate_groups = [
        {"sha256": key, "paths": paths}
        for key, paths in sorted(by_hash.items())
        if key != "empty" and len(paths) > 1
    ]
    for group in duplicate_groups:
        anomalies.append({"path": group["paths"][0], "kind": "duplicate_family",
                          "detail": f"{len(group['paths'])} byte-identical files: {group['paths']}"})
    return {
        "schema_version": 1,
        "root": str(root),
        "file_count": file_count,
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
        "duplicate_groups": duplicate_groups,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in (Path(__file__).stem, Path(__file__).name):
        argv = argv[1:]
    parser = argparse.ArgumentParser(description="Forensic anomaly scanner.")
    parser.add_argument("--root", required=True)
    parser.add_argument("--out")
    parser.add_argument("--include-hidden", action="store_true")
    parser.add_argument("--fail-on-anomaly", action="store_true")
    args = parser.parse_args(argv)
    report = scan(args.root, args.include_hidden)
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.out:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text + "\n", encoding="utf-8")
    print(text)
    if args.fail_on_anomaly and report["anomaly_count"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
