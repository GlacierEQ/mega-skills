#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate.py"

class TestLocalSkill:
    def test_skill_entry_point_exists(self):
        skill_py = ROOT / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111

    def test_scripts_exist(self):
        for script in ["inspect.py","extract.py","generate.py","validate.py","pattern_catalog.py","this_skill.py"]:
            path = ROOT / "scripts" / script
            assert path.exists(), f"Missing script: {script}"
            assert path.stat().st_mode & 0o111

    def test_resources_exist(self):
        for resource in ["local_skill_config.yaml","local_skill_schema.json","SKILL.md.template","skill.py.template"]:
            assert (ROOT / "resources" / resource).exists()

    def test_skill_md_front_matter(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        assert text.lstrip().startswith("---")
        assert "name: local-skill" in text

    def test_generator_emits_truthful_candidate(self, tmp_path):
        result = subprocess.run(
            [sys.executable, str(GENERATOR), "swarm-proof-demo", "Demonstrate a generated candidate skill.", "--output-root", str(tmp_path)],
            text=True, capture_output=True, check=False
        )
        assert result.returncode == 0, result.stdout + result.stderr
        root = tmp_path / "swarm-proof-demo"
        self_check = subprocess.run([sys.executable, str(root / "scripts" / "this_skill.py")], text=True, capture_output=True, check=False)
        payload = json.loads(self_check.stdout)
        assert payload["status"] == "candidate"
        assert payload["epistemic_tier"] == "L1"
        assert payload["capability_executed"] is False

        run = subprocess.run([sys.executable, str(root / "scripts" / "run.py")], text=True, capture_output=True, check=False)
        run_payload = json.loads(run.stdout)
        assert run.returncode == 2
        assert run_payload["status"] == "execution_unavailable"
        assert run_payload["capability_executed"] is False

    def test_generator_never_embeds_false_ready_claims(self):
        text = GENERATOR.read_text(encoding="utf-8")
        assert '"status": "ready"' not in text
        assert '"execution": "completed"' not in text
