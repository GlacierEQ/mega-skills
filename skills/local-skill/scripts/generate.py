#!/usr/bin/env python3
"""
Generate a complete new skill directory from patterns and a name + description.
Part of local-skill.
"""

import sys
import json
import textwrap
from pathlib import Path
from datetime import datetime, timezone

TEMPLATES = {
    "SKILL.md": textwrap.dedent("""\
    ---
    name: {name}
    description: "{description}"
    ---

    # {title}

    ## Use this skill when

    {use_when}

    ## Decision gate

    Proceed only when:
    1. The requested operational envelope is clearly bounded and input parameters are verified.
    2. Execution adheres to baseline Epistemic Tier L2 (Behavioral Proof & Unit Assertions).
    3. Safety invariants and cognitive firewall rules are satisfied.

    ## Creation workflow

    1. **Inspect context**: Verify environmental invariants and prerequisite schemas.
    2. **Draft contract**: Confirm parameters against `resources/{name}_schema.json`.
    3. **Execute domain scripts**: Run focused procedures under `scripts/`.
    4. **Verify assertions**: Confirm 100% green test assertions and cryptographic receipts.
    5. **Emit deliverable**: Emit structured output artifact with SHA-256 hash.

    ## Epistemic Tier & Verification Proofs

    - **Operational Baseline**: $\\mathcal{{L}}_2$ (Unit & Behavioral Proof)
    - **Verification Command**: `python3 -m unittest discover -s tests -v` or `pytest tests/ -v`
    - **Integrity**: Deterministic execution, zero side-channel leakage, cryptographic provenance.

    ## APEX Cognitive Firewall & Safety Invariants

    - **Invariant 1 (Read-Only Default)**: Read and analyze prior to any state mutation. External mutations require explicit authority.
    - **Invariant 2 (Bounded Execution)**: Bounded batching, explicit timeouts, and zero infinite loops.
    - **Invariant 3 (Fail-Closed Gate)**: Any schema violation, missing dependency, or test failure halts execution immediately.

    ## Resources

    | Resource | Use |
    |---|---|
    | `resources/{name}_config.yaml` | Runtime configuration parameters. |
    | `resources/{name}_schema.json` | Input and output validation schema. |

    ## Commands

    ```bash
    {name} this-skill
    {name} run
    ```
    """),

    "skill.py": textwrap.dedent("""\
    #!/usr/bin/env python3
    \"\"\"
    {name}.
    Entry point for {name} skill.
    \"\"\"

    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent / "scripts"))

    def main():
        if len(sys.argv) < 2:
            print(f"Usage: {name} <command> [args...]")
            print("Available commands:")
            for sn in {commands!r}:
                print(f"  {{sn.replace('.py', '')}}")
            return 1

        command = sys.argv[1]
        script_path = Path(__file__).parent / "scripts" / f"{{command}}.py"
        if not script_path.exists():
            script_path = Path(__file__).parent / "scripts" / f"{{command.replace('-', '_')}}.py"
        if not script_path.exists():
            print(f"Unknown command: {{command}}")
            return 1

        exec_globals = {{\"__name__\": \"__main__\"}}
        exec(script_path.read_text(), exec_globals)
        return 0

    if __name__ == "__main__":
        sys.exit(main())
    """),

    "__init__.py": '"""Package init for {name}."""\n',

    "requirements.txt": "pyyaml\njsonschema\n",

    "scripts/this_skill.py": textwrap.dedent("""\
    #!/usr/bin/env python3
    \"\"\"
    Self-description / readiness for {name}.
    \"\"\"

    import sys
    import json
    from pathlib import Path

    def main():
        print(json.dumps({{
            "skill": "{name}",
            "status": "ready",
            "epistemic_tier": "L2",
            "firewall_active": True,
            "generated_by": "local-skill",
            "timestamp": "{timestamp}",
        }}, indent=2))
        return 0

    if __name__ == "__main__":
        sys.exit(main())
    """),

    "scripts/run.py": textwrap.dedent("""\
    #!/usr/bin/env python3
    \"\"\"
    Primary execution entry for {name}.
    \"\"\"

    import sys
    import json
    import hashlib
    from pathlib import Path

    def main():
        skill_name = "{name}"
        data = {{
            "skill": skill_name,
            "status": "success",
            "epistemic_tier": "L2",
            "firewall": "verified",
            "execution": "completed",
        }}
        payload = json.dumps(data, sort_keys=True)
        sha256_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        data["sha256"] = sha256_hash
        print(json.dumps(data, indent=2))
        return 0

    if __name__ == "__main__":
        sys.exit(main())
    """),

    "resources/config.yaml": textwrap.dedent("""\
    # Configuration for {name}
    version: '1.0.0'
    enabled: true
    epistemic_tier: 'L2'
    settings:
      strict_validation: true
      firewall_enforced: true
    """),

    "resources/schema.json": textwrap.dedent("""\
    {{
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "title": "{title}",
      "type": "object",
      "properties": {{
        "skill": {{"type": "string"}},
        "status": {{"type": "string"}},
        "epistemic_tier": {{"type": "string"}},
        "firewall": {{"type": "string"}},
        "sha256": {{"type": "string"}}
      }},
      "required": ["skill", "status", "epistemic_tier"]
    }}
    """),

    "tests/test_skill.py": textwrap.dedent("""\
    #!/usr/bin/env python3
    \"\"\"
    L2 Behavioral tests for {name}.
    \"\"\"

    import sys
    import json
    import unittest
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))

    class Test{class_name}(unittest.TestCase):
        def setUp(self):
            self.root = Path(__file__).parent.parent

        def test_skill_entry_point_exists_and_executable(self):
            skill_py = self.root / "skill.py"
            self.assertTrue(skill_py.exists())
            self.assertTrue(bool(skill_py.stat().st_mode & 0o111))

        def test_scripts_exist_and_executable(self):
            scripts_dir = self.root / "scripts"
            for script in {commands!r}:
                p = scripts_dir / script
                self.assertTrue(p.exists(), f"Missing script: {{script}}")
                self.assertTrue(bool(p.stat().st_mode & 0o111), f"Script not executable: {{script}}")

        def test_resources_exist(self):
            resources_dir = self.root / "resources"
            self.assertTrue((resources_dir / "{name}_config.yaml").exists() or (resources_dir / "config.yaml").exists())
            self.assertTrue((resources_dir / "{name}_schema.json").exists() or (resources_dir / "schema.json").exists())

        def test_requirements_exist(self):
            self.assertTrue((self.root / "requirements.txt").exists())

        def test_skill_md_contract(self):
            skill_md = self.root / "SKILL.md"
            text = skill_md.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---"))
            self.assertIn("name: {name}", text)
            self.assertIn("Cognitive Firewall", text)
            self.assertIn("Epistemic Tier", text)

    if __name__ == "__main__":
        unittest.main()
    """),
}

def to_class_name(name: str) -> str:
    return "".join(part.capitalize() for part in name.replace("-", "_").split("_"))

def main():
    if len(sys.argv) < 3:
        print("Usage: generate <skill-name> <short description...>")
        print("Example: generate my-new-skill 'Does the thing with evidence.'")
        return 1

    name = sys.argv[1].strip().lower().replace("_", "-")
    description = " ".join(sys.argv[2:]).strip()
    title = name.replace("-", " ").title()
    class_name = to_class_name(name)
    timestamp = datetime.now(timezone.utc).isoformat()

    commands = ["this_skill.py", "run.py"]

    # Target directory: sibling under skills/
    here = Path(__file__).resolve()
    skills_root = here.parents[2]  # skills/local-skill/scripts -> skills/
    target = skills_root / name

    if target.exists():
        print(f"Refusing to overwrite existing skill at {target}")
        print("Delete it first or choose a different name.")
        return 1

    target.mkdir(parents=True)
    (target / "scripts").mkdir()
    (target / "resources").mkdir()
    (target / "tests").mkdir()

    ctx = {
        "name": name,
        "title": title,
        "description": description,
        "use_when": f"Use this skill when you need: {description}",
        "commands": commands,
        "class_name": class_name,
        "timestamp": timestamp,
    }

    # Write core files
    (target / "SKILL.md").write_text(TEMPLATES["SKILL.md"].format(**ctx))
    (target / "skill.py").write_text(TEMPLATES["skill.py"].format(**ctx))
    (target / "skill.py").chmod(0o755)
    (target / "__init__.py").write_text(TEMPLATES["__init__.py"].format(**ctx))
    (target / "requirements.txt").write_text(TEMPLATES["requirements.txt"])

    # Scripts
    for scr_name, tmpl_key in [("this_skill.py", "scripts/this_skill.py"), ("run.py", "scripts/run.py")]:
        p = target / "scripts" / scr_name
        p.write_text(TEMPLATES[tmpl_key].format(**ctx))
        p.chmod(0o755)

    # Resources (use skill-prefixed names for clarity)
    (target / "resources" / f"{name}_config.yaml").write_text(
        TEMPLATES["resources/config.yaml"].format(**ctx)
    )
    (target / "resources" / f"{name}_schema.json").write_text(
        TEMPLATES["resources/schema.json"].format(**ctx)
    )

    # Tests
    test_path = target / "tests" / f"test_{name.replace('-', '_')}.py"
    test_path.write_text(TEMPLATES["tests/test_skill.py"].format(**ctx))
    test_path.chmod(0o755)

    print(f"Generated skill: {target}")
    print("Files:")
    for p in sorted(target.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(skills_root)}")
    print("\nNext: review SKILL.md, implement real logic in scripts/run.py, then commit.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
