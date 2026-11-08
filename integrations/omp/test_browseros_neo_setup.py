import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from browseros_neo_setup import (
    ValidationError, validate_endpoint, merge_config, resolve_config_path,
    write_config_atomically, restore_backup, skill_installed,
    probe_mcp, install_skill_command,
)

ENDPOINT = 'http://127.0.0.1:9012/mcp'

class BrowserOSNeoTests(unittest.TestCase):
    def test_preserves_existing_config_without_mutating_input(self):
        original = {'mcpServers': {'github': {'command': 'gh', 'args': ['mcp']}}, 'custom': {'enabled': True}}
        merged = merge_config(original, ENDPOINT)
        self.assertEqual(merged['mcpServers']['github'], original['mcpServers']['github'])
        self.assertEqual(merged['mcpServers']['browseros-neo'], {'type': 'http', 'url': ENDPOINT})
        self.assertEqual(original['mcpServers'].keys(), {'github'})
        self.assertEqual(merged['custom'], original['custom'])

    def test_repeated_merge_idempotent(self):
        v = merge_config({}, ENDPOINT)
        self.assertEqual(merge_config(v, ENDPOINT), v)

    def test_conflicting_entry_preserved_and_rejected(self):
        original = {'mcpServers': {'browseros-neo': {'type': 'stdio', 'command': 'other'}}}
        with self.assertRaises(ValidationError): merge_config(original, ENDPOINT)
        self.assertEqual(original['mcpServers']['browseros-neo']['command'], 'other')

    def test_invalid_shapes_rejected(self):
        for shape in (None, [], {'mcpServers': None}, {'disabledServers': 12}, {'enabledServers': None}):
            with self.subTest(shape=shape), self.assertRaises(ValidationError): merge_config(shape, ENDPOINT)

    def test_denied_neo_removed_without_altering_others(self):
        got = merge_config({'disabledServers': ['other', 'browseros-neo'], 'enabledServers': ['foo']}, ENDPOINT)
        self.assertEqual(got['disabledServers'], ['other'])
        self.assertEqual(got['enabledServers'], ['foo'])

    def test_url_rejects_remote_and_ambiguous_addresses(self):
        for url in ('http://localhost:9012/mcp', 'http://127.0.0.2:9012/mcp',
                    'http://127.0.0.1/mcp', 'http://127.0.0.1:0/mcp',
                    'http://127.0.0.1:9012/mcp?a=1', 'http://user@127.0.0.1:9012/mcp',
                    'https://127.0.0.1:9012/mcp', 'http://127.0.0.1:9012/other',
                    'http://127.0.0.1:9012/mcp#test', 'http://127.0.0.1:99999/mcp'):
            with self.subTest(url=url), self.assertRaises(ValidationError): validate_endpoint(url)

    def test_explicit_nondefault_port_supported(self):
        self.assertEqual(validate_endpoint('http://127.0.0.1:9200/mcp'), ('127.0.0.1', 9200))

    def test_default_and_named_profile_config_resolution(self):
        home = Path('/Users/test')
        self.assertEqual(resolve_config_path(home, {}), home/'.omp/agent/mcp.json')
        self.assertEqual(resolve_config_path(home, {'OMP_PROFILE': 'work'}), home/'.omp/profiles/work/agent/mcp.json')
        self.assertEqual(resolve_config_path(home, {'PI_PROFILE': 'legacy'}), home/'.omp/profiles/legacy/agent/mcp.json')
        self.assertEqual(resolve_config_path(home, {'OMP_PROFILE': '', 'PI_PROFILE': 'legacy'}), home/'.omp/agent/mcp.json')
        self.assertEqual(resolve_config_path(home, {'PI_CONFIG_DIR': '.custom', 'OMP_PROFILE': 'case'}), home/'.custom/profiles/case/agent/mcp.json')
        self.assertEqual(resolve_config_path(home, {'PI_CODING_AGENT_DIR': '/opt/omp-user'}), Path('/opt/omp-user/mcp.json'))

    def test_rejects_unsafe_profile_names(self):
        for value in ('../parent', 'foo/bar', '/root', '.', '..', 'a\\b'):
            with self.subTest(profile=value), self.assertRaises(ValidationError): resolve_config_path(Path('/tmp/home'), {'OMP_PROFILE': value})

    def test_atomic_write_retains_old_config_and_permissions(self):
        with tempfile.TemporaryDirectory() as temp:
            cfg = Path(temp)/'mcp.json'
            original = '{"mcpServers":{"legacy":{"command":"legacy"}}}\n'
            cfg.write_text(original)
            cfg.chmod(0o600)
            backup = write_config_atomically(cfg, merge_config(json.loads(original), ENDPOINT))
            self.assertEqual(backup.read_text(), original)
            self.assertEqual(cfg.stat().st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(cfg.read_text())['mcpServers']['legacy']['command'], 'legacy')

    def test_atomic_write_refuses_symlink_and_preserves_target(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)/'source.json'; target.write_text('{}')
            symlink = Path(temp)/'mcp.json'; symlink.symlink_to(target)
            with self.assertRaises(ValidationError): write_config_atomically(symlink, merge_config({}, ENDPOINT))
            self.assertEqual(target.read_text(), '{}')

    def test_restore_backup_reverts_existing_and_no_clobber_on_conflict(self):
        with tempfile.TemporaryDirectory() as temp:
            cfg = Path(temp)/'mcp.json'; cfg.write_text('{"x":1}\n')
            backup = write_config_atomically(cfg, {'x': 2})
            self.assertEqual(json.loads(cfg.read_text()), {'x': 2})
            restore_backup(cfg, backup, expected_current={'x': 2})
            self.assertEqual(cfg.read_text(), '{"x":1}\n')
            with self.assertRaises(ValidationError): restore_backup(cfg, backup, expected_current={'x': 2})

    def test_installed_skill_respects_supported_roots(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            self.assertFalse(skill_installed(home))
            skill = home/'.agents/skills/browseros-neo/SKILL.md'
            skill.parent.mkdir(parents=True); skill.write_text('---\nname: browseros-neo\n---\n')
            self.assertTrue(skill_installed(home))
            skill.write_text('not a skill')
            self.assertFalse(skill_installed(home))

    def test_npx_installs_only_neo(self):
        self.assertEqual(install_skill_command(), ['npx', 'skills', 'add', 'browseros-ai/browseros', '--skill', 'browseros-neo', '-g', '-y'])

    def test_mcp_protocol_tools_list_verified_with_fake_transport(self):
        calls=[]
        def fake_send(endpoint, method, params, request_id, session_id=None):
            calls.append((method, session_id))
            if method == 'initialize':
                return {'jsonrpc': '2.0', 'id': request_id, 'result': {'protocolVersion': '2025-06-18', 'capabilities': {}, 'serverInfo': {'name': 'browseros-neo', 'version': '1'}}}, 'session-123'
            if method == 'notifications/initialized': return None, session_id
            if method == 'tools/list':
                return {'jsonrpc': '2.0', 'id': request_id, 'result': {'tools': [{'name': 'snapshot'}, {'name': 'tabs'}, {'name': 'act'}]}}, session_id
        with patch('browseros_neo_setup.send_mcp_request', side_effect=fake_send):
            self.assertEqual(probe_mcp(ENDPOINT), ['snapshot','tabs','act'])
        self.assertEqual(calls[1:], [('notifications/initialized', 'session-123'), ('tools/list', 'session-123')])

    def test_mcp_probe_rejects_missing_tools(self):
        def fake_send(endpoint, method, params, request_id, session_id=None):
            if method == 'initialize': return {'result': {'protocolVersion':'2025-06-18', 'serverInfo': {'name':'x'}}}, None
            if method == 'notifications/initialized': return None, None
            return {'result': {'tools': []}}, None
        with patch('browseros_neo_setup.send_mcp_request', side_effect=fake_send):
            with self.assertRaises(ValidationError): probe_mcp(ENDPOINT)

    def test_real_local_http_json_mcp_handshake(self):
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        from threading import Thread
        from browseros_neo_setup import send_mcp_request
        calls = []
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                calls.append((body['method'], self.headers.get('Mcp-Session-Id')))
                if body['method'] == 'initialize':
                    payload = {'jsonrpc': '2.0', 'id': 1, 'result': {'protocolVersion': '2025-06-18'}}
                elif body['method'] == 'notifications/initialized':
                    self.send_response(202); self.end_headers(); return
                else:
                    payload = {'jsonrpc': '2.0', 'id': 2, 'result': {'tools': [{'name': 'snapshot'}, {'name': 'tabs'}]}}
                wire = json.dumps(payload).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Mcp-Session-Id', 'test-session')
                self.send_header('Content-Length', str(len(wire)))
                self.end_headers(); self.wfile.write(wire)
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            endpoint = f'http://127.0.0.1:{server.server_port}/mcp'
            self.assertEqual(probe_mcp(endpoint), ['snapshot', 'tabs'])
            self.assertEqual(calls, [('initialize', None), ('notifications/initialized', 'test-session'), ('tools/list', 'test-session')])
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=2)

    def test_real_local_sse_transport(self):
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        from threading import Thread
        from browseros_neo_setup import send_mcp_request
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def do_POST(self):
                self.rfile.read(int(self.headers['Content-Length']))
                wire = b'event: message\ndata: {"jsonrpc":"2.0","id":5,"result":{"tools":[]}}\n\n'
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.send_header('Content-Length', str(len(wire)))
                self.end_headers(); self.wfile.write(wire)
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            response, _ = send_mcp_request(f'http://127.0.0.1:{server.server_port}/mcp', 'tools/list', {}, 5)
            self.assertEqual(response['result']['tools'], [])
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=2)

    def test_sse_missing_blank_line_reports_validation_error_not_name_error(self):
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        from threading import Thread
        from browseros_neo_setup import send_mcp_request
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def do_POST(self):
                self.rfile.read(int(self.headers['Content-Length']))
                wire = b'data: {"jsonrpc":"2.0","id":5,"result":{"tools":[]}}\n'
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.send_header('Content-Length', str(len(wire)))
                self.end_headers(); self.wfile.write(wire)
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            with self.assertRaises(ValidationError):
                send_mcp_request(f'http://127.0.0.1:{server.server_port}/mcp', 'tools/list', {}, 5)
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=2)

    def test_dry_run_does_not_install_skill_or_create_config(self):
        from browseros_neo_setup import main
        with tempfile.TemporaryDirectory() as temp:
            cfg = Path(temp)/'mcp.json'
            with patch('sys.argv', ['setup', '--config', str(cfg)]), \
                 patch('browseros_neo_setup.assert_target_mac'), \
                 patch('browseros_neo_setup.probe_mcp', return_value=['tabs']), \
                 patch('browseros_neo_setup.subprocess.run') as run, \
                 patch('browseros_neo_setup.write_config_atomically') as write:
                self.assertEqual(main(), 0)
                run.assert_not_called(); write.assert_not_called()
            self.assertFalse(cfg.exists())

    def test_failed_skill_install_leaves_omp_config_untouched(self):
        import subprocess
        from browseros_neo_setup import main
        with tempfile.TemporaryDirectory() as temp:
            cfg = Path(temp)/'mcp.json'; cfg.write_text('{"mcpServers":{"existing":{"command":"foo"}}}')
            before = cfg.read_bytes()
            with patch('sys.argv', ['setup', '--apply', '--config', str(cfg)]), \
                 patch('browseros_neo_setup.assert_target_mac'), \
                 patch('browseros_neo_setup.probe_mcp', return_value=['tabs']), \
                 patch('browseros_neo_setup.shutil.which', return_value='/fake/npx'), \
                 patch('browseros_neo_setup.skill_installed', return_value=False), \
                 patch('browseros_neo_setup.subprocess.run', side_effect=subprocess.CalledProcessError(1, ['npx'])):
                self.assertEqual(main(), 2)
            self.assertEqual(cfg.read_bytes(), before)

if __name__ == '__main__': unittest.main()
