#!/usr/bin/env python3
"""Generate a truthful candidate skill package from repository conventions."""
from __future__ import annotations

import argparse
import json
import re
import textwrap
from pathlib import Path


SKILL_TEMPLATE = textwrap.dedent("""\
---
name: {name}
description: "{description}"
---

# {title}

## Purpose

{description}

## Use When

Use this skill when the requested task matches the capability described above and this package is the most specific available skill.

## Operating Method

1. Inspect the relevant inputs and current project state.
2. Implement the domain operation in scripts/run.py or replace that candidate entrypoint with focused scripts.
3. Add deterministic tests that exercise the stated domain behavior, not merely file existence.
4. Run the package tests and the repository readiness assay.
5. Describe the skill as executable only after behavioral evidence supports that claim.

## Progressive Disclosure

Keep this file concise. Put detailed references in references/, reusable code in scripts/, and output assets/templates in assets/ or resources/.

## Generated State

This package is generated as a candidate scaffold. Generation proves package structure only; it does not prove domain execution.

## Commands

- {name} this-skill
- {name} run

## Verification

The self-description command reports candidate/L1 until domain implementation and behavioral tests exist. The run command fails with execution_unavailable until it is replaced by real domain logic.
""")

SKILL_PY_TEMPLATE = textwrap.dedent("""\
#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

COMMANDS = {{
    "this-skill": "this_skill.py",
    "this_skill": "this_skill.py",
    "run": "run.py",
}}

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: {name} <this-skill|run> [args...]")
        return 1
    script = COMMANDS.get(sys.argv[1])
    if not script:
        print(f"Unknown command: {{sys.argv[1]}}")
        return 1
    path = Path(__file__).parent / "scripts" / script
    return subprocess.run([sys.executable, str(path), *sys.argv[2:]], check=False).returncode

if __name__ == "__main__":
    raise SystemExit(main())
""")

THIS_SKILL_TEMPLATE = textwrap.dedent("""\
#!/usr/bin/env python3
import json

def main() -> int:
    print(json.dumps({{
        "skill": "{name}",
        "status": "candidate",
        "epistemic_tier": "L1",
        "capability_executed": False,
        "generated_by": "local-skill",
        "reason": "Package structure exists; domain behavior has not yet earned L2 proof."
    }}, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
""")

RUN_TEMPLATE = textwrap.dedent("""\
#!/usr/bin/env python3
import json

def main() -> int:
    print(json.dumps({{
        "skill": "{name}",
        "status": "execution_unavailable",
        "capability_executed": False,
        "reason": "Replace scripts/run.py with real domain implementation and add behavioral tests before activation."
    }}, indent=2, sort_keys=True))
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
""")

TEST_TEMPLATE = textwrap.dedent("""\
#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_candidate_self_description_is_truthful():
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "this_skill.py")], text=True, capture_output=True, check=False)
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "candidate"
    assert payload["epistemic_tier"] == "L1"
    assert payload["capability_executed"] is False

def test_unimplemented_run_fails_clearly():
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "run.py")], text=True, capture_output=True, check=False)
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "execution_unavailable"
    assert payload["capability_executed"] is False
""")

CONFIG_TEMPLATE = textwrap.dedent("""\
version: '1.0.0'
enabled: true
generated_state: candidate
epistemic_tier: L1
settings:
  strict_validation: true
  false_ready_forbidden: true
""")

SCHEMA_TEMPLATE = """{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "{title}",
  "type": "object",
  "properties": {
    "skill": {"type": "string"},
    "status": {"type": "string"},
    "capability_executed": {"type": "boolean"}
  },
  "required": ["skill", "status", "capability_executed"]
}
"""


def normalize_name(raw: str) -> str:
    name = raw.strip().lower().replace("_", "-")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("skill name must be lowercase kebab-case")
    return name


def generate_skill(name: str, description: str, output_root: Path) -> Path:
    name = normalize_name(name)
    description = description.strip()
    if not description:
        raise ValueError("description is required")
    target = output_root / name
    if target.exists():
        raise FileExistsError(f"refusing to overwrite existing skill at {target}")

    for directory in ("scripts", "resources", "tests"):
        (target / directory).mkdir(parents=True, exist_ok=True)

    title = name.replace("-", " ").title()
    files = {
        "SKILL.md": SKILL_TEMPLATE.format(name=name, title=title, description=description),
        "skill.py": SKILL_PY_TEMPLATE.format(name=name),
        "__init__.py": f'"""Package init for {name}."""\n',
        "requirements.txt": "",
        "scripts/this_skill.py": THIS_SKILL_TEMPLATE.format(name=name),
        "scripts/run.py": RUN_TEMPLATE.format(name=name),
        f"resources/{name}_config.yaml": CONFIG_TEMPLATE,
        f"resources/{name}_schema.json": json.dumps({
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": title,
            "type": "object",
            "properties": {
                "skill": {"type": "string"},
                "status": {"type": "string"},
                "capability_executed": {"type": "boolean"},
            },
            "required": ["skill", "status", "capability_executed"],
        }, indent=2) + "\n",
        f"tests/test_{name.replace('-', '_')}.py": TEST_TEMPLATE,
    }
    for relative, content in files.items():
        path = target / relative
        path.write_text(content, encoding="utf-8")
        if path.suffix == ".py":
            path.chmod(0o755)
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("description", nargs="+")
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args()

    here = Path(__file__).resolve()
    skills_root = args.output_root.resolve() if args.output_root else here.parents[2]
    try:
        target = generate_skill(args.name, " ".join(args.description), skills_root)
    except (ValueError, FileExistsError) as exc:
        print(str(exc))
        return 1

    print(json.dumps({
        "status": "candidate_generated",
        "skill": target.name,
        "path": str(target),
        "next": "implement domain behavior, add behavioral tests, then run readiness assay"
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
