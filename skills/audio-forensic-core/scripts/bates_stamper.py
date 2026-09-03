#!/usr/bin/env python3
"""Exhibit serial and transcript pagination planner for audio evidence.

Assigns contiguous exhibit serials to audio exhibits and computes the page
span each exhibit's certified transcript occupies at a fixed lines-per-page
rate. Planning metadata only; source audio and transcripts are never modified.
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

SERIAL_PATTERN = re.compile(r"^([A-Z0-9][A-Z0-9_-]{0,31})-(\d{4,8})$")
DEFAULT_LINES_PER_PAGE = 25


def assign_exhibit_serials(exhibits, prefix, start=1, width=4):
    plan = []
    serial = start
    for exhibit in sorted(exhibits, key=lambda row: str(row.get("id", ""))):
        plan.append({
            "exhibit_id": exhibit.get("id"),
            "bates": f"{prefix}-{serial:0{width}d}",
            "source_path": exhibit.get("path"),
            "transcript_lines": int(exhibit.get("transcript_lines", 0)),
        })
        serial += 1
    return plan


def paginate(plan, lines_per_page=DEFAULT_LINES_PER_PAGE):
    """Assign page spans per exhibit in plan order. Returns annotated plan."""
    page_cursor = 1
    paginated = []
    for row in plan:
        lines = max(int(row.get("transcript_lines", 0)), 0)
        pages = max(math.ceil(lines / lines_per_page), 1)
        paginated.append({
            **row,
            "pages": pages,
            "page_start": page_cursor,
            "page_end": page_cursor + pages - 1,
            "lines_per_page": lines_per_page,
        })
        page_cursor += pages
    return paginated


def validate_plan(paginated):
    problems = []
    serials = []
    seen = set()
    previous_end = 0
    for row in paginated:
        bates = str(row.get("bates", ""))
        match = SERIAL_PATTERN.match(bates)
        if match is None:
            problems.append({"kind": "invalid_format", "bates": bates})
            continue
        if bates in seen:
            problems.append({"kind": "collision", "bates": bates})
        seen.add(bates)
        serials.append(int(match.group(2)))
        if int(row.get("page_start", 0)) != previous_end + 1:
            problems.append({"kind": "page_gap_or_overlap", "bates": bates,
                             "expected_start": previous_end + 1,
                             "actual_start": row.get("page_start")})
        previous_end = int(row.get("page_end", previous_end))
    if serials:
        ordered = sorted(serials)
        missing = sorted(set(range(ordered[0], ordered[-1] + 1)) - set(ordered))
        if missing:
            problems.append({"kind": "serial_gap", "missing_serials": missing})
    return {
        "schema_version": 1,
        "exhibits": len(paginated),
        "total_pages": previous_end,
        "contiguous": not problems,
        "problems": problems,
        "planning_only": True,
        "sources_modified": False,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in (Path(__file__).stem, Path(__file__).name):
        argv = argv[1:]
    parser = argparse.ArgumentParser(description="Audio exhibit serial and pagination planner.")
    parser.add_argument("--exhibits", help="JSON document with an 'exhibits' array.")
    parser.add_argument("--prefix", default="EX-AUDIO")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--lines-per-page", type=int, default=DEFAULT_LINES_PER_PAGE)
    parser.add_argument("--out")
    parser.add_argument("--verify", help="Verify an existing pagination plan JSON.")
    args = parser.parse_args(argv)

    if args.verify:
        document = json.loads(Path(args.verify).read_text(encoding="utf-8"))
        report = validate_plan(document.get("plan", []))
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["contiguous"] else 1

    if not args.exhibits:
        parser.error("--exhibits is required when not verifying")
    document = json.loads(Path(args.exhibits).read_text(encoding="utf-8"))
    plan = assign_exhibit_serials(document.get("exhibits", []), args.prefix, args.start)
    paginated = paginate(plan, args.lines_per_page)
    output = {
        "schema_version": 1,
        "prefix": args.prefix,
        "lines_per_page": args.lines_per_page,
        "plan": paginated,
        "validation": validate_plan(paginated),
    }
    text = json.dumps(output, indent=2, sort_keys=True)
    if args.out:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
