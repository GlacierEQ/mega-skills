#!/usr/bin/env python3
"""Court-format transcript compiler for evidentiary audio.

Compiles a phonetically aligned word stream (WhisperX-style alignment JSON)
into a line-numbered, paginated, timestamped transcript and verifies the
formatting invariants a court transcript must hold: sequential line numbers
within each page, bounded lines per page, monotonic timestamps, and complete
word coverage in spoken order.
"""

import argparse
import json
import sys
import textwrap
from pathlib import Path

DEFAULTS = {
    "lines_per_page": 25,
    "line_width": 72,
    "speaker_delimiter": ":",
    "require_case_caption": True,
    "require_certification_block": True,
}


def _coerce(value):
    for cast in (int, float):
        try:
            return cast(value)
        except (TypeError, ValueError):
            continue
    mapping = {"true": True, "yes": True, "false": False, "no": False}
    if isinstance(value, str) and value.lower() in mapping:
        return mapping[value.lower()]
    return value


def _minimal_yaml(text):
    """Parse flat 'section: key: value' YAML when PyYAML is unavailable."""
    data = {}
    current = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        key, sep, value = line.strip().partition(":")
        if not sep:
            continue
        if indent == 0:
            if value.strip():
                data[key] = _coerce(value.strip())
                current = None
            else:
                data[key] = {}
                current = key
        elif current is not None:
            data[current][key] = _coerce(value.strip())
    return data


def load_rules(path=None):
    rules = dict(DEFAULTS)
    if not path:
        return rules
    text = Path(path).read_text(encoding="utf-8")
    try:
        import yaml
        parsed = yaml.safe_load(text) or {}
    except ImportError:
        parsed = _minimal_yaml(text)
    section = parsed.get("transcript", {}) if isinstance(parsed, dict) else {}
    for key in DEFAULTS:
        if key in section:
            rules[key] = section[key]
    return rules


def format_timestamp(seconds):
    seconds = max(float(seconds), 0.0)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"[{hours:02d}:{minutes:02d}:{secs:02d}]"


def _segment_lines(segment, rules):
    label = str(segment.get("speaker", "UNKNOWN"))
    words = [str(word.get("w", "")) for word in segment.get("words", [])]
    text = " ".join(word for word in words if word)
    prefix = f"{format_timestamp(segment.get('start', 0.0))} {label}{rules['speaker_delimiter']} "
    width = max(int(rules["line_width"]), 24)
    wrapped = textwrap.wrap(text, width=max(width - 8, 16),
                            subsequent_indent=" " * 8) or [""]
    lines = []
    for index, chunk in enumerate(wrapped):
        head = prefix if index == 0 else " " * len(prefix)
        lines.append(((head + chunk).rstrip(), float(segment.get("start", 0.0))))
    return lines


def format_transcript(alignment, rules, case_number="", caption="", date="",
                      source_sha256=""):
    """Compile the full paginated transcript text. Returns (text, meta)."""
    lines_per_page = max(int(rules["lines_per_page"]), 1)
    body = []
    for segment in alignment.get("segments", []):
        body.extend(_segment_lines(segment, rules))
    pages = [body[i:i + lines_per_page] for i in range(0, len(body), lines_per_page)] or [[]]
    out = []
    if rules.get("require_case_caption"):
        out.append("=" * rules["line_width"])
        out.append("CERTIFIED PROCEEDING TRANSCRIPT")
        if caption:
            out.append(f"CAPTION: {caption}")
        if case_number:
            out.append(f"CASE NO.: {case_number}")
        if date:
            out.append(f"DATE: {date}")
        if source_sha256:
            out.append(f"SOURCE AUDIO SHA-256: {source_sha256}")
        out.append("=" * rules["line_width"])
        out.append("")
    line_map = []
    for page_index, page in enumerate(pages, start=1):
        out.append(f"--- Page {page_index} ---")
        for line_number, (line, moment) in enumerate(page, start=1):
            out.append(f"{line_number:>4}  {line}")
            line_map.append({"page": page_index, "line": line_number,
                             "timestamp": moment, "text": line})
        out.append("")
    if rules.get("require_certification_block"):
        out.append("TRANSCRIPT CERTIFICATION")
        out.append("Prepared under the governing court's transcript formatting rules.")
        out.append(f"Source digest: {source_sha256 or 'not supplied'}")
    text = "\n".join(out).rstrip() + "\n"
    meta = {"pages": len(pages), "body_lines": len(body), "line_map": line_map}
    return text, meta


def verify_transcript(text, meta, rules, alignment):
    """Verify numbering, pagination, timestamp monotonicity, word coverage."""
    violations = []
    lines_per_page = max(int(rules["lines_per_page"]), 1)
    line_map = meta.get("line_map", [])
    for page in sorted({row["page"] for row in line_map}):
        numbers = [row["line"] for row in line_map if row["page"] == page]
        if numbers != list(range(1, len(numbers) + 1)):
            violations.append({"kind": "numbering_sequence", "page": page})
        if len(numbers) > lines_per_page:
            violations.append({"kind": "page_overflow", "page": page,
                               "lines": len(numbers), "limit": lines_per_page})
    stamps = [row["timestamp"] for row in line_map]
    if any(b < a for a, b in zip(stamps, stamps[1:])):
        violations.append({"kind": "timestamp_regression"})
    rendered = " ".join(row["text"] for row in line_map)
    position = 0
    missing_words = 0
    for segment in alignment.get("segments", []):
        for word in segment.get("words", []):
            token = str(word.get("w", ""))
            if not token:
                continue
            found = rendered.find(token, position)
            if found < 0:
                missing_words += 1
            else:
                position = found + len(token)
    if missing_words:
        violations.append({"kind": "word_coverage_gap", "missing": missing_words})
    return {
        "schema_version": 1,
        "pages": meta.get("pages", 0),
        "body_lines": meta.get("body_lines", 0),
        "numbering_sequential": not any(v["kind"] == "numbering_sequence" for v in violations),
        "timestamps_monotonic": not any(v["kind"] == "timestamp_regression" for v in violations),
        "word_coverage_complete": not missing_words,
        "format_compliant": not violations,
        "violations": violations,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in (Path(__file__).stem, Path(__file__).name):
        argv = argv[1:]
    parser = argparse.ArgumentParser(description="Court-format transcript compiler.")
    parser.add_argument("--alignment", required=True, help="Alignment JSON with segments.")
    parser.add_argument("--rules", help="Court formatting rules YAML.")
    parser.add_argument("--case-number", default="")
    parser.add_argument("--caption", default="")
    parser.add_argument("--date", default="")
    parser.add_argument("--source-sha256", default="")
    parser.add_argument("--out")
    parser.add_argument("--verify", help="Write the format verification report here.")
    args = parser.parse_args(argv)

    alignment = json.loads(Path(args.alignment).read_text(encoding="utf-8"))
    rules = load_rules(args.rules)
    text, meta = format_transcript(alignment, rules, args.case_number, args.caption,
                                   args.date, args.source_sha256)
    if args.out:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    report = verify_transcript(text, meta, rules, alignment)
    if args.verify:
        target = Path(args.verify)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(text if not args.out else json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["format_compliant"] else 1


if __name__ == "__main__":
    sys.exit(main())
