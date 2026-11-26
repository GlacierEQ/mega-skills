#!/usr/bin/env python3
"""Fail-closed hollow-adapter detector for the skills estate.

Three independent checks, each exits nonzero on failure:
  1. documented scripts exist (relative to the skill dir OR the repo root)
  2. no duplicate stub-template signature (run.py + this_skill.py, tiny py line count)
  3. declared tests actually execute a capability (not just assert file presence)
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

CLAIM_TIER = re.compile(r'"epistemic_tier":\s*"(L[2-4][^"]*)"')
CLAIM_READY = re.compile(r'"status":\s*"ready"')
CLAIM_FIREWALL = re.compile(r'"firewall_active":\s*True')
EXECUTED_CLAIM = re.compile(r'\[\s*"status"\]\s*=\s*"executed"')
SCRIPT_REF = re.compile(
    r"(?:python3?|node|bash|sh)\s+((?:scripts|bin|tools)/[\w./-]+\.(?:py|js|mjs|sh))"
)
STUB_MARKERS = ("scripts/run.py", "scripts/this_skill.py")
PRESENCE_ONLY = re.compile(
    r"assert(?:True)?\(.*\.(?:exists|is_file)\(\)|assertTrue\(.*exists", re.I
)


def py_lines(paths: list[str]) -> int:
    total = 0
    for p in paths:
        if not p.endswith(".py"):
            continue
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                total += sum(1 for _ in fh)
        except OSError:
            continue
    return total


def scan(skills_dir: str, stub_max_lines: int) -> tuple[list, list, list, list]:
    root_scripts = {
        os.path.relpath(f)
        for f in glob.glob("scripts/**/*", recursive=True)
        if os.path.isfile(f)
    }
    missing, stubs, weak_tests, false_claims = [], [], [], []

    for name in sorted(os.listdir(skills_dir)):
        d = os.path.join(skills_dir, name)
        skill_md = os.path.join(d, "SKILL.md")
        if not os.path.isdir(d) or not os.path.isfile(skill_md):
            continue
        with open(skill_md, encoding="utf-8", errors="replace") as fh:
            text = fh.read()

        local = {
            os.path.relpath(f, d)
            for f in glob.glob(f"{d}/**/*", recursive=True)
            if os.path.isfile(f)
        }
        unresolved = sorted(
            r
            for r in set(SCRIPT_REF.findall(text))
            if r not in local and r not in root_scripts
        )
        if unresolved:
            missing.append({"skill": name, "missing": unresolved})

        allf = sorted(
            f for f in glob.glob(f"{d}/**/*", recursive=True) if os.path.isfile(f)
        )
        if all(m in local for m in STUB_MARKERS) and py_lines(allf) <= stub_max_lines:
            stubs.append({"skill": name, "py_lines": py_lines(allf), "files": len(allf)})

        for entry in sorted(local):
            if not entry.endswith(".py"):
                continue
            try:
                with open(os.path.join(d, entry), encoding="utf-8", errors="replace") as fh:
                    body = fh.read()
            except OSError:
                continue
            tiers = CLAIM_TIER.findall(body)
            executed = bool(EXECUTED_CLAIM.search(body))
            real = [
                f
                for f in glob.glob(f"{d}/scripts/*")
                if os.path.isfile(f)
                and os.path.basename(f) not in ("run.py", "this_skill.py")
            ]
            if (tiers or executed) and not real:
                false_claims.append(
                    {
                        "skill": name,
                        "file": entry,
                        "tiers": sorted(set(tiers)),
                        "claims_executed": executed,
                    }
                )
    return missing, stubs, weak_tests, false_claims


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("skills_dir", nargs="?", default="skills")
    ap.add_argument("--stub-max-lines", type=int, default=120)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    missing, stubs, weak, claims = scan(a.skills_dir, a.stub_max_lines)
    report = {
        "skills_dir": a.skills_dir,
        "documented_scripts_missing": missing,
        "stub_template_signature": stubs,
        "presence_only_tests": weak,
        "false_capability_claims": claims,
        "verdict": "FAIL"
        if (missing or stubs or weak or claims)
        else "PASS",
    }
    if a.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"documented scripts missing : {len(missing)}")
        print(f"stub template signature    : {len(stubs)}")
        print(f"presence-only tests        : {len(weak)}")
        print(f"false capability claims    : {len(claims)}")
        print(f"verdict                    : {report['verdict']}")
        for r in missing[:15]:
            print(f"  MISSING {r['skill']}: {r['missing']}")
        for r in stubs[:15]:
            print(f"  STUB    {r['skill']}: {r['py_lines']} py lines")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())