#!/usr/bin/env python3
"""Chain-of-custody audit for evidentiary audio artifacts.

Links each processing stage (raw recording, derivatives, transcripts) with
deterministic SHA-256 digests and a rolling chain hash, so any later
modification of any stage artifact is detectable. Files are read only.
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CHUNK_SIZE = 65536
GENESIS = "0" * 64


def compute_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_chain(stages):
    """stages: ordered list of (stage_name, path). Returns custody record."""
    previous = GENESIS
    links = []
    for stage, raw_path in stages:
        path = Path(raw_path)
        if not path.is_file():
            raise SystemExit(f"stage artifact missing for {stage}: {path}")
        digest = compute_sha256(path)
        link = {
            "stage": stage,
            "path": str(path),
            "sha256": digest,
            "size_bytes": path.stat().st_size,
            "previous_hash": previous,
        }
        link["link_hash"] = hashlib.sha256(
            (previous + digest).encode("utf-8")
        ).hexdigest()
        links.append(link)
        previous = link["link_hash"]
    chain_root = hashlib.sha256(
        "".join(link["link_hash"] for link in links).encode("utf-8")
    ).hexdigest()
    return {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "stage_count": len(links),
        "chain_root_sha256": chain_root,
        "links": links,
    }


def verify_chain(record, check_files=True):
    """Recompute a custody chain; optionally re-digest the underlying files."""
    problems = []
    previous = GENESIS
    for index, link in enumerate(record.get("links", [])):
        expected_link = hashlib.sha256(
            (previous + link["sha256"]).encode("utf-8")
        ).hexdigest()
        if link.get("link_hash") != expected_link:
            problems.append({"index": index, "stage": link.get("stage"),
                             "kind": "chain_link_mismatch"})
        if link.get("previous_hash") != previous:
            problems.append({"index": index, "stage": link.get("stage"),
                             "kind": "previous_hash_break"})
        if check_files:
            path = Path(link.get("path", ""))
            if not path.is_file():
                problems.append({"index": index, "stage": link.get("stage"),
                                 "kind": "artifact_missing"})
            else:
                actual = compute_sha256(path)
                if actual != link["sha256"]:
                    problems.append({"index": index, "stage": link.get("stage"),
                                     "kind": "content_modified",
                                     "recorded": link["sha256"], "actual": actual})
        previous = link.get("link_hash", previous)
    root = hashlib.sha256(
        "".join(link.get("link_hash", "") for link in record.get("links", [])).encode("utf-8")
    ).hexdigest()
    root_match = root == record.get("chain_root_sha256")
    if not root_match:
        problems.append({"kind": "chain_root_mismatch"})
    return {
        "schema_version": 1,
        "stages_checked": len(record.get("links", [])),
        "chain_intact": not problems,
        "root_match": root_match,
        "problems": problems,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in (Path(__file__).stem, Path(__file__).name):
        argv = argv[1:]
    parser = argparse.ArgumentParser(description="Audio chain-of-custody audit.")
    parser.add_argument("--stage", action="append", default=[],
                        help="Stage binding in the form name=/path/to/file (repeatable, ordered).")
    parser.add_argument("--root", help="Digest every file under a directory as one custody set.")
    parser.add_argument("--out")
    parser.add_argument("--verify", help="Verify an existing custody record JSON.")
    parser.add_argument("--self-check", action="store_true",
                        help="Verify chain structure without re-reading stage files.")
    args = parser.parse_args(argv)

    if args.verify:
        record = json.loads(Path(args.verify).read_text(encoding="utf-8"))
        report = verify_chain(record, check_files=not args.self_check)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["chain_intact"] else 1

    stages = []
    for binding in args.stage:
        name, sep, path = binding.partition("=")
        if not sep:
            parser.error(f"invalid --stage binding (need name=path): {binding}")
        stages.append((name, path))
    if args.root:
        root = Path(args.root)
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            rel = path.relative_to(root).as_posix()
            if any(part.startswith(".") for part in Path(rel).parts):
                continue
            stages.append(("tree", str(path)))
    if not stages:
        record = {"schema_version": 1, "generated_utc": datetime.now(timezone.utc).isoformat(),
                  "stage_count": 0, "chain_root_sha256": hashlib.sha256(b"").hexdigest(),
                  "links": [], "note": "empty custody set"}
    else:
        record = build_chain(stages)
    text = json.dumps(record, indent=2, sort_keys=True)
    if args.out:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
