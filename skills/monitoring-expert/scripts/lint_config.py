#!/usr/bin/env python3
"""Config linter for the observability stack: Prometheus, Alertmanager, OTel.

Static checks only — never contacts a running collector. Each finding names
the file, the line, the rule and the fix, so a config can be corrected before
it is deployed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PROM_RULES = [
    (
        "scrape_interval_too_long",
        re.compile(r"scrape_interval:\s*(\d+)([smh])"),
        lambda m: int(m.group(1)) * {"s": 1, "m": 60, "h": 3600}[m.group(2)] > 300,
        "high",
        "scrape_interval above 5m makes alerting latency unacceptable; use 15-60s.",
    ),
]

ALERT_RULES = [
    (
        "alert_without_for",
        re.compile(r"- alert:\s*(\S+)"),
        None,
        "medium",
        "Add `for:` so a transient spike does not page; 1-5m is typical.",
    ),
    (
        "no_severity_label",
        re.compile(r"severity:"),
        None,
        "low",
        "Annotate severity so routing can page the right rotation.",
    ),
    (
        "hardcoded_threshold",
        re.compile(r">\s*\d+(\.\d+)?"),
        None,
        "low",
        "Prefer a recorded SLO burn-rate over a magic number that rots.",
    ),
]


def check_prom(path: Path, text: str) -> list[dict]:
    out = []
    if not re.search(r"job_name:", text):
        out.append({"file": str(path), "line": 1, "rule": "missing_job_name",
                    "severity": "high",
                    "fix": "Every scrape_configs entry needs job_name."})
    if "scrape_timeout:" not in text:
        out.append({"file": str(path), "line": 1, "rule": "no_scrape_timeout",
                    "severity": "low",
                    "fix": "Set scrape_timeout explicitly (below scrape_interval)."})
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        for name, pat, pred, sev, fix in PROM_RULES:
            m = pat.search(line)
            if not m:
                continue
            if pred and not pred(m):
                continue
            out.append({"file": str(path), "line": i, "rule": name,
                        "severity": sev, "fix": fix})
    return out


def check_alerts(path: Path, text: str) -> list[dict]:
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        for name, pat, _p, sev, fix in ALERT_RULES:
            if pat.search(line):
                out.append({"file": str(path), "line": i, "rule": name,
                            "severity": sev, "fix": fix})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Static observability config lint.")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    findings = []
    for p in a.paths:
        path = Path(p)
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "scrape_configs" in text:
            findings += check_prom(path, text)
        if re.search(r"^\s*-\s*alert:", text, re.M):
            findings += check_alerts(path, text)

    if a.json:
        print(json.dumps({"findings": findings, "total": len(findings)}, indent=2))
    else:
        for f in findings:
            print(f"{f['file']}:{f['line']} [{f['severity']}] {f['rule']}: {f['fix']}")
        print(f"total: {len(findings)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())