"""Behavioural tests: run the mapper on a fixture tree, assert structure."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAPPER = ROOT / "scripts" / "map_codebase.py"


def run(target):
    return subprocess.run(
        [sys.executable, str(MAPPER), str(target), "--json"],
        capture_output=True, text=True, timeout=120,
    )


FIXTURE = {
    "pkg/core.py": "import os\n\nCONST = 1\n\ndef alpha(x):\n    return x\n\nclass Beta:\n    def method(self):\n        pass\n",
    "pkg/util.py": "from pkg.core import alpha\n\ndef beta():\n    return alpha(1)\n",
    "pkg/skip.txt": "not code\n",
}


class TestMapCodebase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        for rel, body in FIXTURE.items():
            p = Path(self.tmp.name) / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body)

    def tearDown(self):
        self.tmp.cleanup()

    def test_finds_only_code_files(self):
        d = json.loads(run(self.tmp.name).stdout)
        paths = {f["path"] for f in d["files"]}
        self.assertIn("pkg/core.py", paths)
        self.assertNotIn("pkg/skip.txt", paths)

    def test_extracts_defs_with_methods(self):
        d = json.loads(run(self.tmp.name).stdout)
        core = next(f for f in d["files"] if f["path"] == "pkg/core.py")
        names = {x["name"]: x for x in core["defs"]}
        self.assertEqual(names["alpha"]["kind"], "function")
        self.assertEqual(names["Beta"]["kind"], "class")
        self.assertIn("method", names["Beta"]["methods"])

    def test_extracts_import_edges(self):
        d = json.loads(run(self.tmp.name).stdout)
        util = next(f for f in d["files"] if f["path"] == "pkg/util.py")
        self.assertIn("pkg.core", util["imports"])

    def test_counts_lines(self):
        d = json.loads(run(self.tmp.name).stdout)
        self.assertGreater(d["total_lines"], 5)


if __name__ == "__main__":
    unittest.main()
