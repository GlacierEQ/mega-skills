#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("key_hierarchy", ROOT / "scripts" / "key_hierarchy.py")
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class KeyHierarchyTests(unittest.TestCase):
    def test_github_prefers_canonical_token(self) -> None:
        present = {"GITHUB_PAT", "GITHUB_TOKEN", "GITHUB_MASTER_PAT"}
        self.assertEqual(module.pick_winner("github", present), "GITHUB_TOKEN")

    def test_stripe_ignores_publishable_aliases(self) -> None:
        present = {"STRIPE_PUB", "STRIPE_PUBLIC_KEY", "STRIPE_SECRET_KEY"}
        self.assertEqual(module.pick_winner("stripe", present), "STRIPE_SECRET_KEY")

    def test_missing_family_is_none(self) -> None:
        self.assertIsNone(module.pick_winner("buildkite", {"GITHUB_TOKEN"}))


if __name__ == "__main__":
    unittest.main()
