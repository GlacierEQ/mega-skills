#!/usr/bin/env python3
"""Always-on hidden-harm counter-wave router.

Selects domain specialists from work signals, requires remainder cover when
needed, and emits a recursive meta-harm checklist so remediations cannot
quietly introduce new silent losses.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "integrations" / "hidden-harm-skill-matrix.json"

DOMAIN_HINTS: dict[str, tuple[str, ...]] = {
    "hidden-harm-github": (
        "github",
        "git ",
        "branch",
        "pull request",
        " pr ",
        "ci",
        "release",
        "deploy",
        "merge",
        "force-push",
    ),
    "hidden-harm-context": (
        "context",
        "memory",
        "summary",
        "continuity",
        "handoff",
        "supermemory",
        "mem0",
        "operator word",
        "correction",
    ),
    "hidden-harm-connectors": (
        "connector",
        "mcp",
        "plugin",
        "provider",
        "iceberg",
        "gatekeeper",
        "keymaster",
        "pinecone",
        "notion",
        "supabase",
    ),
    "hidden-harm-casebuild": (
        "casebuild",
        "evidence",
        "legal",
        "court",
        "allegation",
        "docket",
        "filing",
        "remedy",
        "juggernaut",
    ),
}

META_HARMS = (
    "fix_theater",
    "verification_capture",
    "convenience_centralization",
    "bureaucracy_capture",
    "peak_language",
    "dual_surfaces",
    "correction_resurrection",
)


def load_matrix() -> dict[str, Any]:
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def _normalize(text: str) -> str:
    return f" {re.sub(r'\s+', ' ', text.lower())} "


def select_specialists(work: str, tags: list[str] | None = None) -> list[str]:
    blob = _normalize(work + " " + " ".join(tags or []))
    selected: list[str] = []
    for skill_id, hints in DOMAIN_HINTS.items():
        if any(h in blob for h in hints):
            selected.append(skill_id)
    if not selected:
        selected.append("hidden-harm-cross-domain")
    elif "hidden-harm-cross-domain" not in selected:
        # Remainder cover when specialists fire but work may spill outside them.
        selected.append("hidden-harm-cross-domain")
    # Always compose the counter-wave itself as the cruise layer.
    if "hidden-harm-counter-wave" not in selected:
        selected.insert(0, "hidden-harm-counter-wave")
    return selected


def compose_plan(work: str, tags: list[str] | None = None) -> dict[str, Any]:
    matrix = load_matrix()
    specialists = select_specialists(work, tags)
    skill_index = {s["id"]: s for s in matrix.get("skills", [])}
    composed = []
    for sid in specialists:
        if sid == "hidden-harm-counter-wave":
            composed.append(
                {
                    "id": sid,
                    "role": "always_on_counter_wave",
                    "path": "skills/hidden-harm-counter-wave/SKILL.md",
                }
            )
            continue
        meta = skill_index.get(sid, {})
        composed.append(
            {
                "id": sid,
                "role": "domain_specialist",
                "path": meta.get("path", f"skills/{sid}/SKILL.md"),
                "protects": meta.get("protects", []),
            }
        )
    return {
        "schema": "glaciereq.hidden-harm-counter-wave.plan.v1",
        "counter_pattern": matrix.get(
            "counter_pattern",
            "DETECT LOSS -> NAME LOST DIMENSION -> PRESERVE STRONGER STATE -> ROUTE AROUND -> VERIFY -> PERSIST",
        ),
        "always_on": True,
        "dynamic_recursive": True,
        "work": work.strip(),
        "composed": composed,
        "recursive_meta_harms_to_counter": list(META_HARMS),
        "routing_rule": matrix.get("routing_rule", ""),
        "success": (
            "Stronger living continuation with protected dimensions preserved; "
            "not a longer audit checklist."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Hidden-harm counter-wave router")
    parser.add_argument("work", nargs="?", default="", help="Work unit description")
    parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Optional domain tag (repeatable)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    args = parser.parse_args()
    work = args.work or "general GlacierEQ material work"
    plan = compose_plan(work, args.tag)
    if args.json:
        print(json.dumps(plan, indent=2, sort_keys=True))
    else:
        print("HIDDEN-HARM COUNTER-WAVE PLAN")
        print(f"work: {plan['work']}")
        print("compose:")
        for item in plan["composed"]:
            print(f"  - {item['id']} ({item['role']})")
        print("recursive meta-harms:")
        for harm in plan["recursive_meta_harms_to_counter"]:
            print(f"  - {harm}")
        print(f"pattern: {plan['counter_pattern']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
