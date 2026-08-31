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
    description: {description}
    ---

    # {title}

    ## Use this skill when

    {use_when}

    ## Decision gate

    Proceed only when the requested outcome is clearly bounded and the required inputs are available.

    ## Creation workflow

    1. Inspect context and existing related skills.
    2. Draft the contract and resource surface.
    3. Implement focused scripts under scripts/.
    4. Add structural and behavioral tests.
    5. Validate and release deliberately.

    ## Resources

    | Resource | Use |
    |---|---|
    | `resources/{name}_config.yaml` | Runtime configuration. |
    | `resources/{name}_schema.json` | Input/output schema. |

    ## Commands

    ```
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
        print(json.dumps({
            "skill": "{name}",
            "status": "ready",
            "generated_by": "local-skill",
            "timestamp": "{timestamp}",
        }, indent=2))
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
    from pathlib import Path

    def main():
        print(f"Executing run.py for {name}")
        # TODO: implement real logic
        return 0

    if __name__ == "__main__":
        sys.exit(main())
    """),

    "resources/config.yaml": textwrap.dedent("""\
    # Configuration for {name}
    version: '1.0.0'
    enabled: true
    settings:
      strict_validation: true
    """),

    "resources/schema.json": textwrap.dedent("""\
    {{
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "title": "{title}",
      "type": "object",
      "properties": {{
        "status": {{"type": "string"}},
        "artifacts": {{"type": "array"}}
      }}
    }}
    """),

    "tests/test_skill.py": textwrap.dedent("""\
    #!/usr/bin/env python3
    \"\"\"
    L2 Behavioral tests for {name}.
    Run with: python -m pytest tests/ -v
    \"\"\"

    import pytest
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))

    class Test{class_name}:
        def test_skill_entry_point_exists(self):
            skill_py = Path(__file__).parent.parent / "skill.py"
            assert skill_py.exists()
            assert skill_py.stat().st_mode & 0o111

        def test_scripts_exist(self):
            scripts_dir = Path(__file__).parent.parent / "scripts"
            for script in {commands!r}:
                p = scripts_dir / script
                assert p.exists(), f"Missing script: {{script}}"

        def test_resources_exist(self):
            resources_dir = Path(__file__).parent.parent / "resources"
            assert (resources_dir / "{name}_config.yaml").exists() or (resources_dir / "config.yaml").exists()

        def test_requirements_exist(self):
            assert (Path(__file__).parent.parent / "requirements.txt").exists()

    if __name__ == "__main__":
        pytest.main([__file__, "-v"])
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
