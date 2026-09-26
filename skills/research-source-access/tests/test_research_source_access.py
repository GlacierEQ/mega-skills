#!/usr/bin/env python3
"""Tests for research-source-access.

The safety guarantees are the point of this skill, so they are tested
directly: read-only receipts, method restriction, scheme restriction,
embedded-credential rejection, and private-address refusal (SSRF guard).
No test performs real network I/O.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import skill as rsa  # noqa: E402


class TestSearchWorkspace(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "a.md").write_text("firewall boundary and merge safety", encoding="utf-8")
        (self.root / "b.txt").write_text("unrelated content", encoding="utf-8")
        (self.root / "skip.bin").write_bytes(b"\x00binary")
        (self.root / ".git").mkdir()
        (self.root / ".git" / "config.md").write_text("firewall", encoding="utf-8")
        self.addCleanup(self.tmp.cleanup)

    def test_finds_matching_file(self):
        r = rsa.search_workspace({"root": str(self.root), "query": "firewall"})
        self.assertTrue(r["ok"])
        self.assertTrue(any("a.md" in x["path"] for x in r["results"]))

    def test_is_read_only(self):
        r = rsa.search_workspace({"root": str(self.root), "query": "firewall"})
        self.assertTrue(r["read_only"])
        self.assertFalse(r["mutated"])
        self.assertFalse(r["transmitted"])

    def test_skips_git_and_binary(self):
        r = rsa.search_workspace({"root": str(self.root), "query": "firewall"})
        paths = " ".join(x["path"] for x in r["results"])
        self.assertNotIn(".git", paths)
        self.assertNotIn("skip.bin", paths)

    def test_empty_query_refused(self):
        r = rsa.search_workspace({"root": str(self.root), "query": "  "})
        self.assertFalse(r["ok"])
        self.assertEqual(r["reason"], "empty_query")


class TestUrlGuard(unittest.TestCase):
    """_safe_url is the SSRF / exfiltration boundary."""

    def test_rejects_non_https_by_default(self):
        _, reason = rsa._safe_url("http://example.com", allow_insecure_http=False)
        self.assertEqual(reason, "scheme_not_allowed:http")

    def test_allows_http_when_explicitly_enabled(self):
        with patch.object(rsa, "_host_is_public", return_value=(True, "")):
            url, reason = rsa._safe_url("http://example.com", allow_insecure_http=True)
        self.assertTrue(url)
        self.assertEqual(reason, "")

    def test_rejects_embedded_credentials(self):
        _, reason = rsa._safe_url("https://user:pass@example.com", False)
        self.assertEqual(reason, "embedded_credentials_rejected")

    def test_rejects_missing_host(self):
        _, reason = rsa._safe_url("https://", False)
        self.assertEqual(reason, "missing_host")

    def test_rejects_loopback(self):
        _, reason = rsa._safe_url("https://127.0.0.1/x", False)
        self.assertIn("non_public_address", reason)

    def test_rejects_private_range(self):
        _, reason = rsa._safe_url("https://10.0.0.5/x", False)
        self.assertIn("non_public_address", reason)

    def test_rejects_link_local(self):
        _, reason = rsa._safe_url("https://169.254.169.254/latest/meta-data", False)
        self.assertIn("non_public_address", reason)

    def test_rejects_file_scheme(self):
        _, reason = rsa._safe_url("file:///etc/passwd", False)
        self.assertEqual(reason, "scheme_not_allowed:file")

    def test_public_host_accepted(self):
        with patch.object(rsa, "_host_is_public", return_value=(True, "")):
            url, reason = rsa._safe_url("https://example.com/a", False)
        self.assertEqual(url, "https://example.com/a")
        self.assertEqual(reason, "")


class TestLoadPublicSources(unittest.TestCase):
    def test_refuses_private_url_without_network(self):
        r = rsa.load_public_sources({"urls": ["https://127.0.0.1/secret"]})
        self.assertTrue(r["ok"])           # the batch ran
        self.assertEqual(r["refused"], 1)  # the URL was refused
        self.assertIn("non_public_address", r["sources"][0]["reason"])

    def test_empty_url_list_refused(self):
        r = rsa.load_public_sources({"urls": []})
        self.assertFalse(r["ok"])
        self.assertEqual(r["reason"], "no_urls")

    def test_receipt_declares_no_transmission(self):
        r = rsa.load_public_sources({"urls": ["https://127.0.0.1/x"]})
        self.assertFalse(r["transmitted"])
        self.assertFalse(r["mutated"])


class TestConnectedSources(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cfg = Path(self.tmp.name) / "connectors.json"
        self.addCleanup(self.tmp.cleanup)

    def _write(self, connectors):
        self.cfg.write_text(json.dumps({"connectors": connectors}), encoding="utf-8")

    def test_rejects_non_get_method(self):
        self._write({"db": {"base_url": "https://x", "read_only": True}})
        r = rsa.read_connected_sources({
            "connector": "db", "connectors_path": str(self.cfg),
            "request": {"method": "POST"}})
        self.assertFalse(r["ok"])
        self.assertEqual(r["reason"], "method_not_allowed:POST")

    def test_rejects_write_connector(self):
        self._write({"db": {"base_url": "https://x", "read_only": False}})
        r = rsa.read_connected_sources({
            "connector": "db", "connectors_path": str(self.cfg), "request": {}})
        self.assertFalse(r["ok"])
        self.assertEqual(r["reason"], "connector_not_read_only")

    def test_rejects_write_capability(self):
        self._write({"db": {"base_url": "https://x", "read_only": True,
                            "capabilities": ["read", "write"]}})
        r = rsa.read_connected_sources({
            "connector": "db", "connectors_path": str(self.cfg), "request": {}})
        self.assertFalse(r["ok"])
        self.assertEqual(r["reason"], "connector_declares_write_capability")

    def test_rejects_unconfigured_connector(self):
        self._write({})
        r = rsa.read_connected_sources({
            "connector": "nope", "connectors_path": str(self.cfg), "request": {}})
        self.assertFalse(r["ok"])
        self.assertEqual(r["reason"], "connector_not_configured")

    def test_inherits_url_guard(self):
        self._write({"db": {"base_url": "https://127.0.0.1", "read_only": True,
                            "capabilities": ["read"]}})
        r = rsa.read_connected_sources({
            "connector": "db", "connectors_path": str(self.cfg), "request": {}})
        self.assertFalse(r["ok"])
        self.assertIn("non_public_address", r["reason"])


class TestReceiptShape(unittest.TestCase):
    def test_receipt_declares_read_only(self):
        r = rsa._receipt("x", {}, ok=True)
        self.assertTrue(r["read_only"])
        self.assertFalse(r["mutated"])
        self.assertFalse(r["transmitted"])
        self.assertEqual(r["schema"], "glaciereq.research-source-access.receipt.v1")

    def test_stdlib_only(self):
        src = (HERE.parent / "skill.py").read_text(encoding="utf-8")
        for mod in ("import requests", "import httpx", "import aiohttp", "import numpy"):
            self.assertNotIn(mod, src)


if __name__ == "__main__":
    unittest.main()
