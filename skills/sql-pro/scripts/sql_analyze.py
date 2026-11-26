#!/usr/bin/env python3
"""Static SQL analysis: find anti-patterns without executing the query.

Reads .sql files (or stdin), applies rule packs, emits a JSON or text report.
Rules are conservative and dialect-aware: a finding names the rule, the line,
and the rewrite to apply.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RULES = [
    (
        "select_star",
        re.compile(r"\bselect\s+\*", re.I),
        "medium",
        "Project explicit columns; SELECT * breaks on schema change and hides index-only scans.",
    ),
    (
        "leading_wildcard_like",
        re.compile(r"\blike\s+'%", re.I),
        "high",
        "Leading wildcard prevents index use; use a trigram index or full-text search.",
    ),
    (
        "function_on_column",
        re.compile(r"\bwhere\s+(lower|upper|date|cast|coalesce)\s*\(", re.I),
        "medium",
        "Function on the column blocks a plain index; add a functional index or compare canonically.",
    ),
    (
        "or_in_where",
        re.compile(r"\bwhere\b[^;]*\bor\b[^;]*\band\b", re.I),
        "low",
        "OR across columns often defeats the planner; consider UNION ALL or an index merge.",
    ),
    (
        "not_in_with_nulls",
        re.compile(r"\bnot\s+in\s*\(", re.I),
        "high",
        "NOT IN with NULLs returns no rows; use NOT EXISTS or add NOT NULL filters.",
    ),
    (
        "offset_pagination",
        re.compile(r"\boffset\s+\d+", re.I),
        "medium",
        "Large OFFSET scans and discards rows; use keyset pagination on an indexed column.",
    ),
    (
        "count_distinct_wide",
        re.compile(r"\bcount\s*\(\s*distinct\b", re.I),
        "low",
        "COUNT(DISTINCT) on wide sets is expensive; pre-aggregate or use HyperLogLog.",
    ),
    (
        "implicit_cast",
        re.compile(r"\bwhere\s+\w+\s*=\s*'\d{4}-\d{2}-\d{2}", re.I),
        "medium",
        "String literal against a date/timestamp column can force a cast; use a typed literal.",
    ),
]


def analyze(text: str) -> list[dict]:
    findings = []
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        for name, pat, sev, fix in RULES:
            if pat.search(line):
                findings.append(
                    {
                        "rule": name,
                        "severity": sev,
                        "line": lineno,
                        "evidence": stripped[:120],
                        "fix": fix,
                    }
                )
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description="Static SQL anti-pattern analysis.")
    ap.add_argument("paths", nargs="*", help=".sql files; default stdin")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    targets = []
    if a.paths:
        for p in a.paths:
            path = Path(p)
            if path.is_dir():
                targets += sorted(path.rglob("*.sql"))
            else:
                targets.append(path)
    else:
        targets = [Path("<stdin>")]

    report = {}
    total = 0
    for path in targets:
        text = sys.stdin.read() if str(path) == "<stdin>" else path.read_text(
            encoding="utf-8", errors="replace"
        )
        findings = analyze(text)
        report[str(path)] = findings
        total += len(findings)

    if a.json:
        print(json.dumps({"files": report, "total_findings": total}, indent=2))
    else:
        for f, items in report.items():
            print(f"{f}: {len(items)} finding(s)")
            for i in items:
                print(f"  L{i['line']} [{i['severity']}] {i['rule']}: {i['fix']}")
        print(f"total: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())