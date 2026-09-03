#!/usr/bin/env python3
"""Air-gapped PII scrubber for evidentiary text surfaces.

Detects US SSNs, phone numbers, and email addresses in text-like files and
emits a findings report that records match digests and line numbers without
copying the sensitive values. With ``--redact`` it writes redacted derivative
copies; originals are never modified in place.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

PATTERNS = {
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "phone": re.compile(r"\b(?:\+1[\s.\-]?)?\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}\b"),
    "email": re.compile(r"\b[\w.+\-]+@[\w\-]+\.[\w.]+\b"),
}
TEXT_SUFFIXES = {".txt", ".md", ".json", ".csv", ".log", ".xml", ".yaml", ".yml", ".html"}


def scan_file(path):
    """Return findings for one file without exposing matched values."""
    findings = []
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return [{"kind": "read_error", "detail": str(exc), "line": 0}]
    for line_number, line in enumerate(lines, start=1):
        for kind, pattern in PATTERNS.items():
            for match in pattern.finditer(line):
                digest = hashlib.sha256(match.group().encode("utf-8")).hexdigest()[:12]
                findings.append({
                    "kind": kind,
                    "line": line_number,
                    "match_sha256_12": digest,
                    "column": match.start(),
                })
    return findings


def redact_text(text):
    """Return redacted text and the count of substitutions per kind."""
    counts = {}
    redacted = text
    for kind, pattern in PATTERNS.items():
        redacted, count = pattern.subn(f"[REDACTED-{kind.upper()}]", redacted)
        counts[kind] = count
    return redacted, counts


def scan_tree(root, include_hidden=False):
    root = Path(root)
    if not root.is_dir():
        raise SystemExit(f"scrub root is not a directory: {root}")
    files = []
    total = 0
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        if not include_hidden and any(part.startswith(".") for part in Path(rel).parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        findings = scan_file(path)
        if findings:
            files.append({"path": rel, "finding_count": len(findings), "findings": findings})
            total += len(findings)
    return {
        "schema_version": 1,
        "root": str(root),
        "files_with_findings": len(files),
        "finding_count": total,
        "values_copied_into_report": 0,
        "files": files,
    }


def redact_tree(root, out_dir, include_hidden=False):
    root = Path(root)
    out_dir = Path(out_dir)
    written = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root)
        if not include_hidden and any(part.startswith(".") for part in rel.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        redacted, counts = redact_text(path.read_text(encoding="utf-8", errors="replace"))
        if sum(counts.values()):
            target = out_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(redacted, encoding="utf-8")
            written.append({"path": rel.as_posix(), "redactions": counts,
                            "derivative": True, "source_modified": False})
    return written


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in (Path(__file__).stem, Path(__file__).name):
        argv = argv[1:]
    parser = argparse.ArgumentParser(description="Air-gapped PII scrubber.")
    parser.add_argument("--root", required=True)
    parser.add_argument("--report")
    parser.add_argument("--redact", action="store_true")
    parser.add_argument("--out-dir")
    parser.add_argument("--include-hidden", action="store_true")
    args = parser.parse_args(argv)
    report = scan_tree(args.root, args.include_hidden)
    if args.redact:
        if not args.out_dir:
            parser.error("--redact requires --out-dir")
        report["redacted_copies"] = redact_tree(args.root, args.out_dir, args.include_hidden)
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.report:
        target = Path(args.report)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
