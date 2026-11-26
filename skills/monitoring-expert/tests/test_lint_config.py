"""Behavioural tests: run the linter on fixtures, assert findings."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINTER = ROOT / "scripts" / "lint_config.py"

BAD_PROM = """scrape_configs:
  - job_name: api
    scrape_interval: 10m
    static_configs:
      - targets: ['a:9090']
"""

BAD_ALERT = """groups:
  - name: g
    rules:
      - alert: HighLatency
        expr: latency > 5
"""


def run(path):
    return subprocess.run(
        [sys.executable, str(LINTER), str(path), "--json"],
        capture_output=True, text=True, timeout=60,
    )


class TestLintConfig(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, body):
        p = Path(self.tmp.name) / name
        p.write_text(body)
        return p

    def test_flags_long_scrape_interval(self):
        d = json.loads(run(self.write("p.yml", BAD_PROM)).stdout)
        rules = {f["rule"] for f in d["findings"]}
        self.assertIn("scrape_interval_too_long", rules)

    def test_flags_alert_without_for(self):
        d = json.loads(run(self.write("a.yml", BAD_ALERT)).stdout)
        rules = {f["rule"] for f in d["findings"]}
        self.assertIn("alert_without_for", rules)

    def test_clean_config_has_no_findings(self):
        clean = "scrape_configs:\n  - job_name: api\n    scrape_interval: 30s\n    scrape_timeout: 10s\n"
        d = json.loads(run(self.write("ok.yml", clean)).stdout)
        self.assertEqual(d["total"], 0)


if __name__ == "__main__":
    unittest.main()
