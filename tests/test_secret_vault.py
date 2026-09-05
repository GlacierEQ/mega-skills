#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("secret_vault", ROOT / "scripts" / "secret_vault.py")
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class SecretVaultTests(unittest.TestCase):
    def test_round_trip_does_not_echo_plaintext_in_store(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wrap = module.ensure_wrap_key(root)
            store = {"schema_version": 1, "values": {}}
            secret = "xai-unit-test-not-a-real-key"
            store["values"]["XAI_API_KEY"] = {
                "use": "runtime",
                "env": "XAI_API_KEY",
                "envelope": module.seal_value(wrap, secret),
            }
            module.write_store(root, store)
            raw = (root / module.SEALED_NAME).read_text(encoding="utf-8")
            self.assertNotIn(secret, raw)
            loaded = module.load_store(root)
            self.assertEqual(module.unseal_value(wrap, loaded["values"]["XAI_API_KEY"]["envelope"]), secret)

    def test_status_lists_names_not_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            os.environ["BUILDKITE_API_TOKEN"] = "bk-unit-test"
            try:
                module.bind_from_environ(root)
                report = module.status_report(root)
            finally:
                os.environ.pop("BUILDKITE_API_TOKEN", None)
            blob = json.dumps(report)
            self.assertNotIn("bk-unit-test", blob)
            self.assertIn("BUILDKITE_API_TOKEN", blob)

    def test_force_push_is_rejected(self) -> None:
        with self.assertRaises(module.VaultError):
            module.assert_never_force_push(["git", "push", "--force", "origin", "main"])


if __name__ == "__main__":
    unittest.main()
