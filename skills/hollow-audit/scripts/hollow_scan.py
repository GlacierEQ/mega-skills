#!/usr/bin/env python3
"""Scan a skill package for hollow-adapter defects. Exit 1 on any finding."""
from __future__ import annotations

import glob
import json
import os
import re
import sys

SCRIPT_REF = re.compile(
    r"(?:python3?|node|bash|sh)\s+((?:scripts|bin|tools)/[\w./-]+\.(?:py|js|mjs|sh))"
)
STUB = {"run.py", "this_skill.py"}
PRESENCE = re.compile(r"assert(True)?\(.*\.(?:exists|is_file)\(\)", re.I)


def _read(path: str) -> str:
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def scan(skill_dir: str) -> dict:
    md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(md):
        return {"skill": os.path.basename(skill_dir), "error": "no SKILL.md"}
    text = open(md, encoding="utf-8", errors="replace").read()
    local = {
        os.path.relpath(f, skill_dir)
        for f in glob.glob(f"{skill_dir}/**/*", recursive=True)
        if os.path.isfile(f)
    }
    missing = sorted(set(SCRIPT_REF.findall(text)) - local)
    scripts = [
        f
        for f in local
        if f.endswith((".py", ".sh", ".js"))
        and os.path.basename(f) not in STUB
        and f != "skill.py"
    ]
    weak = []
    for t in glob.glob(f"{skill_dir}/**/tests/**/*.py", recursive=True):
        body = open(t, encoding="utf-8", errors="replace").read()
        if PRESENCE.search(body) and "subprocess" not in body:
            weak.append(os.path.relpath(t, skill_dir))
    all_py = [f for f in local if f.endswith(".py")]
    py_lines = 0
    for f in all_py:
        try:
            with open(os.path.join(skill_dir, f), encoding="utf-8", errors="replace") as fh:
                py_lines += sum(1 for _ in fh)
        except OSError:
            continue
    entry = _read(os.path.join(skill_dir, "scripts", "run.py")) or _read(
        os.path.join(skill_dir, "skill.py")
    )
    adapter = bool(
        re.search(
            r"capability_executed\s*:\s*False|adapter_ready|execution_unavailable"
            r"|no domain execution",
            entry,
        )
    )
    stub_sig = (
        ("scripts/run.py" in local and "scripts/this_skill.py" in local and py_lines <= 120)
        or adapter
    ) and not scripts
    return {
        "skill": os.path.basename(skill_dir),
        "documented_scripts_missing": missing,
        "real_scripts": len(scripts),
        "presence_only_tests": weak,
        "stub_template_signature": stub_sig,
        "py_lines": py_lines,
        "verdict": "FAIL" if (missing or weak or stub_sig) else "PASS",
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    result = scan(target)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("verdict") == "PASS" else 1)