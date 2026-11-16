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
BRIDGE = _load("n8n_stdio_bridge", ROOT / "ops" / "apex" / "n8n_stdio_bridge.py")
CACHE = _load("apex_memory_cache", ROOT / "scripts" / "apex_memory_cache.py")


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
        previous = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp:
            os.chdir(tmp)
            try:
                missing_parent = ROOT / "brand-new-untracked-dir" / "report.json"
                self.assertFalse(missing_parent.parent.exists())
                self.assertFalse(AUDIT.destination_is_safe(missing_parent))
                outside = Path(tmp) / "also-missing" / "out.json"
                self.assertTrue(AUDIT.destination_is_safe(outside))
            finally:
                os.chdir(previous)
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
            document = json.loads(body)
            self.assertEqual(document["sha256"], BOOT.receipt_digest(document["report"]))
            self.assertIn("missing", body)

    def test_report_leak_is_detected_before_any_write(self) -> None:
        raw = {"OPENAI_API_KEY": "sk-test-should-not-print"}
        report = {"canonical_names": ["OPENAI_API_KEY"], "note": raw["OPENAI_API_KEY"]}
        self.assertTrue(AUDIT.report_contains_secret(report, raw))
        self.assertFalse(AUDIT.report_contains_secret({"canonical_names": ["OPENAI_API_KEY"]}, raw))
        self.assertFalse(AUDIT.report_contains_secret({"canonical_names": ["DEBUG"], "raw_count": 1}, {"DEBUG": "1"}))

    def test_inline_comment_does_not_override_quoted_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text(
                'OPENAI_API_KEY=real # retired OPENAI_API_KEY=old\n'
                'SERVICE_PASSWORD="abc # def"\n',
                encoding="utf-8",
            )
            parsed = AUDIT.parse_env(env_path)
            self.assertEqual(parsed["OPENAI_API_KEY"], "real")
            self.assertNotIn("old", parsed.values())
            self.assertEqual(parsed["SERVICE_PASSWORD"], "abc # def")
            booted = BOOT.load_env(env_path)
            self.assertEqual(booted["OPENAI_API_KEY"], "real")
            destination = AUDIT.write_clean_env(env_path, parsed)
            self.assertEqual(AUDIT.parse_env(destination)["SERVICE_PASSWORD"], "abc # def")

    def test_mem0_account_keys_stay_distinct(self) -> None:
        canonical, _duplicates = AUDIT.dedupe(
            {"MEM0_PRO_API_KEY": "pro-account-key", "MEM0_REG_API_KEY": "reg-account-key", "MEM0_KEY": "fallback-key"}
        )
        self.assertEqual(canonical["MEM0_PRO_API_KEY"], "pro-account-key")
        self.assertEqual(canonical["MEM0_REG_API_KEY"], "reg-account-key")
        self.assertEqual(canonical["MEM0_API_KEY"], "fallback-key")

    def test_memory_cache_expires_and_scopes_pinecone(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "memory_hits.json"
            key = CACHE.mem0_cache_key("pro", "operator", "where is the brief")
            CACHE.cache_set(path, key, "old-hit", now=1_000.0)
            self.assertEqual(CACHE.cache_get(path, key, now=1_000.0 + CACHE.CACHE_TTL_SECONDS), "old-hit")
            self.assertIsNone(CACHE.cache_get(path, key, now=1_000.0 + CACHE.CACHE_TTL_SECONDS + 1))
            CACHE.cache_set(path, key, "fresh", now=2_000.0)
            self.assertEqual(CACHE.invalidate_prefix(path, CACHE.mem0_prefix("pro", "operator")), 1)
            self.assertIsNone(CACHE.cache_get(path, key, now=2_000.0))
            first = CACHE.pinecone_cache_key("index-a.example", "key-a", "query")
            second = CACHE.pinecone_cache_key("index-b.example", "key-a", "query")
            self.assertNotEqual(first, second)
            self.assertNotIn("key-a", first)

    def test_n8n_bridge_sends_bearer_header_and_keeps_it_out_of_argv(self) -> None:
        seen = {}

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                seen["path"] = self.path
                seen["authorization"] = self.headers.get("Authorization")
                length = int(self.headers.get("Content-Length", "0"))
                seen["body"] = self.rfile.read(length)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Mcp-Session-Id", "session-1")
                self.end_headers()
                self.wfile.write(b'{"jsonrpc":"2.0","id":1,"result":{"ok":true}}')

            def log_message(self, fmt, *args):
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f"http://127.0.0.1:{server.server_address[1]}/mcp-server/http"
            session, messages = BRIDGE.forward(url, "bridge-test-token", '{"jsonrpc":"2.0","id":1,"method":"ping"}', None)
        finally:
            server.shutdown()
            thread.join(timeout=2)
        self.assertEqual(session, "session-1")
        self.assertEqual(json.loads(messages[0])["result"]["ok"], True)
        self.assertEqual(seen["authorization"], "Bearer bridge-test-token")
        self.assertNotIn("bridge-test-token", seen["path"])
        config = json.loads((ROOT / "ops" / "apex" / "mcpServers.json").read_text(encoding="utf-8"))
        n8n = config["mcpServers"]["n8n-mcp"]
        self.assertNotIn("N8N_API_KEY", " ".join(n8n["args"]))
        self.assertEqual(n8n["env"]["N8N_API_KEY"], "${N8N_API_KEY}")
        self.assertEqual(BRIDGE.endpoint("https://example.n8n-host.com"), "https://example.n8n-host.com/mcp-server/http")
        self.assertEqual(BRIDGE.sse_payloads('event: message\ndata: {"ok":1}\n\n'), ['{"ok":1}'])


if __name__ == "__main__":
    unittest.main()
