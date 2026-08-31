#!/usr/bin/env python3
"""
Maintain / emit the living pattern catalog.
Part of local-skill.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

def main():
    catalog_path = Path(__file__).parent.parent / "references" / "pattern-catalog.md"
    catalog_path.parent.mkdir(exist_ok=True)

    # Prefer last_inspect.json if present
    inspect_path = Path(__file__).parent.parent / "resources" / "last_inspect.json"
    summary = {}
    if inspect_path.exists():
        summary = json.loads(inspect_path.read_text())

    lines = [
        "# Pattern Catalog (local-skill)",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Dominant conventions observed in mega-skills",
        "",
        "- Directory name: hyphenated lowercase (`my-skill-name`)",
        "- Required: `SKILL.md` (YAML front-matter with `name` + `description`), `skill.py` (executable dispatcher)",
        "- Strongly preferred: `scripts/`, `resources/`, `tests/`, `__init__.py`, `requirements.txt`",
        "- Optional: `templates/`, `references/`",
        "- skill.py pattern: thin CLI dispatcher that `exec`s scripts/<command>.py",
        "- Scripts are executable (`chmod +x`) and contain a `main()` + `if __name__ == \"__main__\"`",
        "- Tests: `tests/test_<name>.py` with a class and structural assertions",
        "- Resources: YAML config + JSON schema is the most common pair",
        "",
    ]

    if summary:
        lines.extend([
            "## Last inspect snapshot",
            "",
            f"- Skill count: {summary.get('skill_count')}",
            f"- skill.py ratio: {summary.get('has_skill_py_ratio'):.2f}",
            f"- tests ratio: {summary.get('has_tests_ratio'):.2f}",
            "",
            "### Top script names",
            "",
        ])
        for name, cnt in summary.get("top_scripts", [])[:15]:
            lines.append(f"- `{name}` ({cnt})")

    catalog_path.write_text("\n".join(lines) + "\n")
    print(f"Wrote {catalog_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
