from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from omp_runtime_audit import audit_omp, extract_config_value  # noqa: E402


class OmpRuntimeAuditTests(unittest.TestCase):
    def test_nested_yaml_scalar_no_arbitrary_fields(self):
        source = '''tools:
  approvalMode: "yolo" # danger
memory:
  backend: hindsight
providers:
  secret: NEVER_ECHO_THIS
'''
        self.assertEqual(extract_config_value(source, "tools.approvalMode"), "yolo")
        self.assertEqual(extract_config_value(source, "memory.backend"), "hindsight")
        self.assertIsNone(extract_config_value(source, "tools.nonexistent"))

    def test_yolo_sensitive_git_paths_and_memory_are_not_execution_proof(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            base = home / ".omp" / "agent"
            base.mkdir(parents=True)
            (base / "config.yml").write_text(
                "tools:\n  approvalMode: yolo\nmemory:\n  backend: hindsight\nproviders:\n  token: SECRET_CANARY_NOT_IN_OUTPUT\n"
            )
            (base / ".gitignore").write_text(".env\npgdata/\n")
            subprocess.run(["git", "init", "-q", str(base)], check=True)
            (base / "agent.db").write_text("DUMMY_CANARY")
            out = audit_omp(home=home, free_gib=21, load_1=400, cpu_count=4, executable=Path("/does/not/exist"))
            findings = {x["id"]: x for x in out["findings"]}
            self.assertEqual(findings["approval_mode_yolo"]["severity"], "HIGH")
            self.assertEqual(findings["secrets_unignored"]["severity"], "HIGH")
            self.assertEqual(findings["load_pressure"]["severity"], "HIGH")
            self.assertEqual(out["acceptance"]["provider_readback"], "UNVERIFIED")
            self.assertEqual(out["acceptance"]["context_applied"], "UNVERIFIED")
            payload = json.dumps(out)
            self.assertNotIn("SECRET_CANARY", payload)
            self.assertNotIn("DUMMY_CANARY", payload)

    def test_safe_repo_and_write_mode_not_high_risk(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            base = home / ".omp" / "agent"
            base.mkdir(parents=True)
            (base / "config.yml").write_text(
                "tools:\n  approvalMode: write\nmemory:\n  backend: off\n"
            )
            (base / ".gitignore").write_text("agent.db\nconfig.yml\nsessions/\nsecret-placeholder.key\ncred-candidates.json\n")
            subprocess.run(["git", "init", "-q", str(base)], check=True)
            binary = home / ".local" / "bin" / "omp"
            binary.parent.mkdir(parents=True)
            binary.write_text("#!/bin/sh\nexit 0\n")
            binary.chmod(0o755)
            out = audit_omp(home=home, free_gib=30, load_1=1, cpu_count=4, executable=binary)
            ids = [x["id"] for x in out["findings"]]
            self.assertNotIn("approval_mode_yolo", ids)
            self.assertNotIn("secrets_unignored", ids)
            self.assertNotIn("disk_pressure", ids)
            self.assertEqual(out["status"], "BASELINE_ONLY")
            self.assertTrue(all(v == "UNVERIFIED" for v in out["acceptance"].values()))

    def test_tracked_sensitive_path_is_flagged_even_when_gitignore_added(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / ".omp" / "agent"
            base.mkdir(parents=True)
            subprocess.run(["git", "init", "-q", str(base)], check=True)
            (base / "agent.db").write_text("placeholder")
            subprocess.run(["git", "-C", str(base), "add", "agent.db"], check=True)
            (base / ".gitignore").write_text("agent.db\nconfig.yml\nsessions/\nsecret-placeholder.key\ncred-candidates.json\n")
            out = audit_omp(home=Path(tmp), free_gib=30, load_1=1, cpu_count=4, executable=Path("/nonexistent"))
            self.assertIn("sensitive_files_tracked", {f["id"] for f in out["findings"]})

    def test_unknown_configuration_is_not_reported_as_secure(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = audit_omp(home=Path(tmp), free_gib=None, load_1=None, cpu_count=None, executable=Path("/nonexistent"))
            self.assertEqual(out["status"], "NEEDS_ATTENTION")
            self.assertIn("config_unavailable", {f["id"] for f in out["findings"]})
            self.assertIn("omp_missing", {f["id"] for f in out["findings"]})


if __name__ == "__main__":
    unittest.main()
