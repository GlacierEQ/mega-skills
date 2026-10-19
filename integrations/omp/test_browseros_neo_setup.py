import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from browseros_neo_setup import merge_config, write_config_atomically, ValidationError, install_skill_command


class MergeConfigTests(unittest.TestCase):
    def test_preserves_other_mcp_entries_and_top_level_configuration(self):
        original = {"mcpServers": {"github": {"type": "http", "url": "https://example.test/mcp"}}, "disabledServers": ["unused"], "custom": {"owner": "geq"}}
        result = merge_config(original, "http://127.0.0.1:9012/mcp")
        self.assertEqual(result["mcpServers"]["github"], original["mcpServers"]["github"])
        self.assertEqual(result["mcpServers"]["browseros-neo"], {"type": "http", "url": "http://127.0.0.1:9012/mcp"})
        self.assertEqual(result["custom"], {"owner": "geq"})
        self.assertEqual(original["mcpServers"].keys(), {"github"})

    def test_repeat_merge_is_idempotent(self):
        merged = merge_config({}, "http://127.0.0.1:9012/mcp")
        self.assertEqual(merge_config(merged, "http://127.0.0.1:9012/mcp"), merged)

    def test_never_replaces_existing_different_browseros_endpoint(self):
        source = {"mcpServers": {"browseros-neo": {"type": "http", "url": "http://127.0.0.1:9200/mcp"}}}
        with self.assertRaises(ValidationError):
            merge_config(source, "http://127.0.0.1:9012/mcp")

    def test_refuses_malformed_configuration(self):
        for invalid in ([], {"mcpServers": []}, {"disabledServers": "bad"}):
            with self.subTest(invalid=invalid), self.assertRaises(ValidationError):
                merge_config(invalid, "http://127.0.0.1:9012/mcp")

    def test_removes_only_neo_from_disabled_set(self):
        source = {"disabledServers": ["github", "browseros-neo", "other"]}
        got = merge_config(source, "http://127.0.0.1:9012/mcp")
        self.assertEqual(got["disabledServers"], ["github", "other"])

    def test_refuses_nonlocal_endpoint(self):
        with self.assertRaises(ValidationError):
            merge_config({}, "https://external.example/mcp")

    def test_atomic_writer_creates_recoverable_backup_on_update(self):
        with tempfile.TemporaryDirectory() as td:
            config = Path(td) / "mcp.json"
            config.write_text('{"mcpServers":{"old":{"command":"thing"}}}\n')
            initial = config.read_bytes()
            data = merge_config(json.loads(initial), "http://127.0.0.1:9012/mcp")
            backup = write_config_atomically(config, data)
            self.assertIsNotNone(backup)
            self.assertEqual(backup.read_bytes(), initial)
            self.assertEqual(json.loads(config.read_text())["mcpServers"]["old"], {"command": "thing"})
            self.assertEqual(json.loads(config.read_text())["mcpServers"]["browseros-neo"]["url"], "http://127.0.0.1:9012/mcp")

    def test_skill_installer_exactly_matches_single_skill_and_global_mode(self):
        self.assertEqual(install_skill_command(), ["npx", "skills", "add", "browseros-ai/browseros", "--skill", "browseros-neo", "-g", "-y"])


if __name__ == '__main__':
    unittest.main()
