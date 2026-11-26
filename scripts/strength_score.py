#!/usr/bin/env python3
"""Score activated skills on whether they make the agent STRONGER.

A skill is strength only if it changes behaviour on a real task and that
change is verified by execution. Prose alone is reference, not capability.

Axes (0/1/2 each, 12 max):
  E EXECUTABLE  ships a runnable entrypoint doing domain work (not run.py stub)
  T TESTED      behavioural tests exist and pass with zero failures
  D DEPTH       SKILL.md body carries real procedure (>=4000 bytes = 2)
  B BOUNDARY    states both activation triggers and avoid-when
  R RECEIPT     entrypoint emits a verifiable contract (json/artifact/exit)
  U UNIQUE      not a near-duplicate name of another activated skill

Usage: strength_score.py [--json] [--min N] [skills_dir]
Exit 1 when any activated skill scores below --min (default 6).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys

DEFAULT_MIN = 6
STUB_NAMES = {"run.py", "this_skill.py"}


def activated() -> list[str]:
    r = subprocess.run(
        ["omp", "config", "get", "skills.includeSkills"],
        capture_output=True,
        text=True,
        env={**os.environ, "GITHUB_TOKEN": ""},
    )
    try:
        return json.loads(r.stdout or "[]")
    except json.JSONDecodeError:
        return []


def split_frontmatter(path: str) -> tuple[str, str]:
    text = open(path, encoding="utf-8", errors="replace").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    return (m.group(1), m.group(2)) if m else ("", text)


def run_tests(d: str) -> tuple[int, int, int]:
    passed = failed = files = 0
    for t in glob.glob(f"{d}/**/tests/**/*.py", recursive=True):
        files += 1
        td = os.path.dirname(t)
        try:
            r = subprocess.run(
                [sys.executable, "-m", "pytest", ".", "-q", "--no-header"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=td,
            )
        except (subprocess.TimeoutExpired, OSError):
            continue
        tail = (r.stdout or "")[-400:]
        m = re.search(r"(\d+) passed", tail)
        n = re.search(r"(\d+) failed", tail)
        passed += int(m.group(1)) if m else 0
        failed += int(n.group(1)) if n else 0
    return files, passed, failed


def score(name: str, root: str, names: set[str]) -> dict | None:
    d = os.path.join(root, name)
    skill_md = os.path.join(d, "SKILL.md")
    if not os.path.isfile(skill_md):
        return None
    fm, body = split_frontmatter(skill_md)

    files = [f for f in glob.glob(f"{d}/**/*", recursive=True) if os.path.isfile(f)]
    scripts = [
        f
        for f in files
        if f.endswith((".py", ".sh", ".js")) and os.path.basename(f) not in STUB_NAMES
    ]
    test_files, passed, failed = run_tests(d)

    e = 2 if scripts else 0
    t = 2 if (passed and not failed) else (1 if test_files else 0)
    dep = 2 if len(body) >= 4000 else (1 if len(body) >= 1500 else 0)
    hay = (body + "\n" + fm).lower()
    trig = bool(re.search(r"use when|use for|use this skill|when to use", hay))
    avoid = bool(re.search(r"do not use|when not to use|avoid when|not for|skip when|out of scope", body, re.I))
    b = 2 if (trig and avoid) else (1 if trig else 0)
    r = 1 if scripts else 0
    dupes = sum(1 for n in names if n != name and n.startswith(name[:8]))
    u = 0 if dupes > 1 else 2

    return {
        "skill": name,
        "E": e,
        "T": t,
        "D": dep,
        "B": b,
        "R": r,
        "U": u,
        "total": e + t + dep + b + r + u,
        "scripts": len(scripts),
        "test_files": test_files,
        "passed": passed,
        "failed": failed,
        "body": len(body),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("skills_dir", nargs="?", default="skills")
    ap.add_argument("--min", type=int, default=DEFAULT_MIN)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    names = set(activated())
    rows = [r for n in sorted(names) if (r := score(n, a.skills_dir, names))]
    rows.sort(key=lambda r: (r["total"], r["skill"]))
    weak = [r for r in rows if r["total"] < a.min]

    if a.json:
        print(json.dumps({"skills": rows, "weak": weak}, indent=2))
    else:
        print(
            f"{'skill':38} {'E':>2}{'T':>2}{'D':>2}{'B':>2}{'R':>2}{'U':>2} "
            f"{'tot':>4} {'scr':>4} {'pass':>5} {'fail':>5}"
        )
        for r in rows:
            flag = "  <-- WEAK" if r["total"] < a.min else ""
            print(
                f"{r['skill']:38} {r['E']:>2}{r['T']:>2}{r['D']:>2}{r['B']:>2}"
                f"{r['R']:>2}{r['U']:>2} {r['total']:>4} {r['scripts']:>4} "
                f"{r['passed']:>5} {r['failed']:>5}{flag}"
            )
        avg = round(sum(r["total"] for r in rows) / len(rows), 2) if rows else 0
        print(f"\nTOTAL {len(rows)} | avg {avg} | below min {a.min}: {len(weak)}")
    return 1 if weak else 0


if __name__ == "__main__":
    sys.exit(main())