#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "cultivate_main.py"
spec = importlib.util.spec_from_file_location("cultivate_main", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class CultivateMainTests(unittest.TestCase):
    def test_additive_docs_and_scripts_auto_merge(self) -> None:
        result = module.assess_change(
            title="Add cultivate-main assessor",
            files=["docs/CULTIVATE_MAIN.md", "scripts/cultivate_main.py", "tests/test_cultivate_main.py"],
            ahead_by=3,
            behind_by=0,
            mergeable=True,
        )
        self.assertEqual(result["decision"], "AUTO_MERGE")
        self.assertEqual(result["operator"], "assessor")
        self.assertEqual(result["merge_method"], "merge")

    def test_secret_patch_is_casey_class(self) -> None:
        result = module.assess_change(
            title="oops",
            files=["scripts/vault.py"],
            patch="token = 'ghp_notarealtokenbutmatchesmarker'",
            ahead_by=1,
            mergeable=True,
        )
        self.assertEqual(result["decision"], "CASEY")
        self.assertEqual(result["operator"], "casey")

    def test_force_push_or_replace_main_is_casey_class(self) -> None:
        result = module.assess_change(
            title="cut over to new trunk",
            files=["README.md"],
            replaces_main=True,
            ahead_by=20,
            mergeable=True,
        )
        self.assertEqual(result["decision"], "CASEY")

    def test_conflict_is_harvest_not_wait_forever(self) -> None:
        result = module.assess_change(
            title="audit fixes",
            files=["scripts/readiness_assay.py", "registry/skill-readiness.json"],
            ahead_by=12,
            behind_by=8,
            mergeable=False,
        )
        self.assertEqual(result["decision"], "HARVEST")
        self.assertEqual(result["operator"], "assessor")

    def test_identical_branch_is_redundant(self) -> None:
        result = module.assess_change(
            title="already landed",
            files=["docs/CULTIVATE_MAIN.md"],
            ahead_by=0,
            behind_by=0,
            already_in_main=True,
        )
        self.assertEqual(result["decision"], "REDUNDANT")

    def test_registry_deletion_is_harvest(self) -> None:
        result = module.assess_change(
            title="activate mesh",
            files=["registry/skills.json", "mega-skills/apex-casebuild-mesh/MEGA.md"],
            deletes_registry_entry=True,
            ahead_by=1,
            mergeable=True,
        )
        self.assertEqual(result["decision"], "HARVEST")


if __name__ == "__main__":
    unittest.main()
