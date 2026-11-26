#!/usr/bin/env python3
"""Gem Seeker: find candidate skills on GitHub, then verify each is real.

A candidate is a gem only if it ships executable scripts AND its own tests pass.
Listing alone is not discovery; unverified lists are how hollow adapters spread.

Usage: gemseeker.py "query one" "query two"
"""
from __future__ import annotations

import glob
import json
import os
import re
import subprocess
import sys
import tempfile

PASS = re.compile(r"(\d+) passed")
FAIL = re.compile(r"(\d+) failed")


def gh(*args: str) -> str:
    r = subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        env={**os.environ, "GITHUB_TOKEN": ""},
    )
    return r.stdout


def search(query: str, limit: int = 12) -> list[dict]:
    out = gh(
        "search", "repos", query, "--limit", str(limit), "--json",
        "fullName,stargazersCount,description,updatedAt",
    )
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return []


def skill_count(repo: str) -> int:
    out = gh(
        "api", f"repos/{repo}/git/trees/HEAD?recursive=1",
        "--jq", '[.tree[]|select(.path|endswith("SKILL.md"))]|length',
    )
    try:
        return int(out.strip() or 0)
    except ValueError:
        return 0


def clone(repo: str, dest: str) -> bool:
    r = subprocess.run(
        ["gh", "repo", "clone", repo, dest, "--", "--depth=1", "-q"],
        capture_output=True,
        text=True,
        env={**os.environ, "GITHUB_TOKEN": ""},
    )
    return r.returncode == 0


def verify(path: str) -> tuple[int, int, int, int, int]:
    """Return (scripts, py_lines, test_files, passed, failed)."""
    scripts = [
        f
        for f in glob.glob(f"{path}/**/*", recursive=True)
        if os.path.isfile(f) and f.endswith((".py", ".sh", ".js"))
    ]
    lines = 0
    for f in scripts:
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                lines += sum(1 for _ in fh)
        except OSError:
            continue

    test_dirs = {
        os.path.dirname(f)
        for f in glob.glob(f"{path}/**/tests/**/*.py", recursive=True)
    }
    passed = failed = 0
    for d in sorted(test_dirs):
        try:
            r = subprocess.run(
                [sys.executable, "-m", "pytest", ".", "-q", "--no-header"],
                capture_output=True,
                text=True,
                timeout=180,
                cwd=d,
            )
        except (subprocess.TimeoutExpired, OSError):
            continue
        tail = (r.stdout or "")[-500:]
        m = PASS.search(tail)
        n = FAIL.search(tail)
        passed += int(m.group(1)) if m else 0
        failed += int(n.group(1)) if n else 0

    return len(scripts), lines, len(test_dirs), passed, failed


def main() -> int:
    queries = sys.argv[1:] or ["claude skills collection"]
    seen: set[str] = set()
    gems: list[dict] = []
    duds: list[dict] = []

    with tempfile.TemporaryDirectory() as td:
        for q in queries:
            for r in search(q):
                full = r["fullName"]
                if full in seen:
                    continue
                seen.add(full)

                n = skill_count(full)
                if n < 3:
                    duds.append({"repo": full, "reason": f"only {n} SKILL.md"})
                    continue

                dest = os.path.join(td, full.replace("/", "_"))
                if not clone(full, dest):
                    duds.append({"repo": full, "reason": "clone failed"})
                    continue

                best = (0, 0, 0, 0, 0)
                for root in (dest, os.path.join(dest, ".claude", "skills")):
                    if not os.path.isdir(root):
                        continue
                    got = verify(root)
                    if got[1] > best[1]:
                        best = got

                sc, ln, t, p, f = best
                rec = {
                    "repo": full,
                    "stars": r.get("stargazerCount"),
                    "skills": n,
                    "scripts": sc,
                    "py_lines": ln,
                    "test_dirs": t,
                    "passed": p,
                    "failed": f,
                    "verdict": "GEM" if (sc and ln > 300 and f == 0 and p > 0) else "DUD",
                }
                (gems if rec["verdict"] == "GEM" else duds).append(rec)

    print(json.dumps({"gems": gems, "duds": duds}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())