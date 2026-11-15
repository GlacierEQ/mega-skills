#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import stat
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


AUDIT = _load("apex_key_audit", ROOT / "scripts" / "apex_key_audit.py")
BOOT = _load("apex_boot_unified", ROOT / "scripts" / "apex_boot_unified.py")


class AuditTests(unittest.TestCase):
    def test_one_line_lump_parses_and_collapses_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text(
                'GITHUB_TOKEN="gh-canonical" GITHUB_TOKEN_ALT1="gh-canonical" '
                'NOTION_API_KEY="notion-canonical" GROQ_SECONDARY_KEY="groq-only"\n',
                encoding="utf-8",
            )
            parsed = AUDIT.parse_env(env_path)
            self.assertEqual(parsed["GITHUB_TOKEN"], "gh-canonical")
            canonical, duplicates = AUDIT.dedupe(parsed)
            self.assertEqual(canonical["GH_TOKEN"], "gh-canonical")
            self.assertNotIn("GITHUB_TOKEN", canonical)
            self.assertEqual(canonical["NOTION_TOKEN"], "notion-canonical")
            self.assertEqual(canonical["GROQ_API_KEY"], "groq-only")
            self.assertTrue(duplicates)
            blob = json.dumps({"canonical_names": sorted(canonical), "duplicates": duplicates})
            self.assertNotIn("gh-canonical", blob)
            self.assertNotIn("notion-canonical", blob)

    def test_exact_canonical_beats_alias(self) -> None:
        canonical, _duplicates = AUDIT.dedupe(
            {"GH_TOKEN": "from-canonical", "GITHUB_TOKEN": "from-alias"}
        )
        self.assertEqual(canonical["GH_TOKEN"], "from-canonical")

    def test_clean_env_refuses_tracked_path_and_allows_ignored_home(self) -> None:
        self.assertFalse(AUDIT.destination_is_safe(ROOT / "secrets" / "catalog.json"))
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / ".env"
            source.write_text('OPENAI_API_KEY="sk-test-value"\n', encoding="utf-8")
            destination = AUDIT.write_clean_env(source, {"OPENAI_API_KEY": "sk-test-value"})
            self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o600)
            self.assertIn("OPENAI_API_KEY=sk-test-value", destination.read_text(encoding="utf-8"))

    def test_probe_pass_and_auth_fail_without_leaking_header(self) -> None:
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802
                if self.headers.get("Authorization") == "Bearer good":
                    self.send_response(200)
                else:
                    self.send_response(401)
                self.end_headers()
                self.wfile.write(b"ok")

            def log_message(self, fmt, *args):
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f"http://127.0.0.1:{server.server_address[1]}/user"
            passed = AUDIT.probe("github", url, {"Authorization": "Bearer good"})
            failed = AUDIT.probe("github", url, {"Authorization": "Bearer bad"})
        finally:
            server.shutdown()
            thread.join(timeout=2)
        self.assertEqual(passed, {"provider": "github", "status": "PASS", "http_code": 200})
        self.assertEqual(failed["status"], "AUTH_FAIL")
        self.assertNotIn("Bearer", json.dumps(failed))

    def test_gemini_check_keeps_key_out_of_url(self) -> None:
        checks = AUDIT._checks({"GEMINI_API_KEY": "gemini-test-key"})
        self.assertEqual(len(checks), 1)
        _name, url, headers = checks[0]
        self.assertNotIn("gemini-test-key", url)
        self.assertEqual(headers["x-goog-api-key"], "gemini-test-key")

    def test_shipped_files_have_no_live_secret_markers(self) -> None:
        markers = ("github_pat_", "sk-proj-", "sk-ant-", "AKIA", "sbp_v0_", "xoxe-", "BEGIN PRIVATE")
        paths = [
            ROOT / "scripts" / "apex_key_audit.py",
            ROOT / "scripts" / "apex_boot_unified.py",
            ROOT / "scripts" / "unified_memory_mcp.py",
            ROOT / "ops" / "apex" / "mcpServers.json",
            ROOT / "secrets" / "catalog.json",
        ]
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for marker in markers:
                self.assertNotIn(marker, text, f"{marker} in {path}")

    def test_boot_receipt_counts_names_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text('OPENAI_API_KEY="sk-test-boot"\n', encoding="utf-8")
            previous = os.environ.get("OPENAI_API_KEY")
            os.environ.pop("OPENAI_API_KEY", None)
            try:
                loaded = BOOT.load_env(env_path)
                report = {"core_keys": BOOT.verify_keys(), "env_loaded": len(loaded)}
                receipt = BOOT.write_boot_receipt(report, Path(tmp))
                body = receipt.read_text(encoding="utf-8")
            finally:
                if previous is None:
                    os.environ.pop("OPENAI_API_KEY", None)
                else:
                    os.environ["OPENAI_API_KEY"] = previous
            self.assertNotIn("sk-test-boot", body)
            self.assertIn("sha256", body)
            self.assertIn("missing", body)


if __name__ == "__main__":
    unittest.main()
