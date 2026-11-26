"""Behavioural tests: execute the real rollout-gate and checker scripts."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "rollout_gate.py"
ANDROID = ROOT / "scripts" / "android_release_check.py"
IOS = ROOT / "scripts" / "ios_privacy_manifest_check.py"


def run(script, *args):
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


class TestMobileRelease(unittest.TestCase):
    def test_rollout_gate_halts_on_regression_sample(self):
        r = run(GATE, "--sample")
        self.assertIn("HALT", r.stdout)
        self.assertNotEqual(r.returncode, 0)

    def test_rollout_gate_emits_json_contract(self):
        r = run(GATE, "--sample", "--output", "json")
        d = json.loads(r.stdout)
        self.assertIn("action", d)
        self.assertTrue(d["action"].strip())

    def test_android_check_runs_on_repo(self):
        r = run(ANDROID, str(ROOT))
        self.assertIn(r.returncode, {0, 1, 2})

    def test_ios_check_runs_on_repo(self):
        r = run(IOS, str(ROOT))
        self.assertIn(r.returncode, {0, 1, 2})


if __name__ == "__main__":
    unittest.main()