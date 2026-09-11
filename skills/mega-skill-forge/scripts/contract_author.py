#!/usr/bin/env python3
"""
Copy templates/MEGA.md, write route algorithm via Combo artifacts
Part of mega-skill-forge skill.
"""

import argparse
import sys
from pathlib import Path


def render_mega_contract(
    display_name: str,
    mission_description: str,
    required_combos: list[str],
    conditional_combos: list[str] | None = None,
    integration_delta: str | None = None,
    template_path: Path | None = None,
) -> str:
    """Render canonical MEGA.md contract markdown."""
    if len(required_combos) < 2:
        raise ValueError("At least two required Combos are mandatory for a Mega Skill")

    conds = conditional_combos or ["capability-readiness"]
    delta = integration_delta or f"End-to-end orchestration and artifact synthesis across {', '.join(required_combos)}"

    table_rows = []
    table_rows.append(f"| `{required_combos[0]}` | `capability-readiness` when prerequisite verification is needed | Mission readiness check and gatekeeping. |")
    for i in range(1, len(required_combos)):
        cond = conds[i % len(conds)]
        table_rows.append(f"| `{required_combos[i]}` | `{cond}` when operational requirements trigger | {delta} |")

    table_content = "\n".join(table_rows)

    content = f"""# {display_name} Mega Skill

## Mission

{mission_description}

## Compounding structure

| Mandatory route | Conditional route | What the Mega layer adds |
|---|---|---|
{table_content}

## Route algorithm

1. Begin with named mission state and the required Combo artifacts.
2. Run readiness before selecting an advanced route with unverified conditions.
3. Select only the conditional Combos whose documented criteria match observed mission facts.
4. Reconcile named Combo artifacts into durable state; do not consume undocumented history.
5. Apply named gates, disclose residual uncertainty, preserve approval state, and write a recoverable handoff.

## Durable state

`MISSION.md`, `ROADMAP.md`, `CONTEXT.md`, `EVIDENCE.md`, and `HANDOFF.md` are the Mega layer source of truth.
"""
    return content


def author_contract(
    output_path: Path,
    display_name: str,
    mission_description: str,
    required_combos: list[str],
    conditional_combos: list[str] | None = None,
    integration_delta: str | None = None,
) -> Path:
    """Write rendered contract to output path."""
    text = render_mega_contract(display_name, mission_description, required_combos, conditional_combos, integration_delta)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Author MEGA.md contract from template")
    parser.add_argument("--name", required=True, help="Display name of the Mega Skill")
    parser.add_argument("--mission", required=True, help="Mission-level outcome description")
    parser.add_argument("--combos", nargs="+", required=True, help="Required combo IDs")
    parser.add_argument("--output", type=Path, default=Path("MEGA.md"), help="Output markdown path")
    args = parser.parse_args()

    out = author_contract(args.output, args.name, args.mission, args.combos)
    print(f"Authored Mega contract at {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
