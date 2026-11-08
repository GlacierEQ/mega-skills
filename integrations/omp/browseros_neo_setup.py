#!/usr/bin/env python3
"""Safely provision BrowserOS Neo for the EXISTING Oh My Pi user/profile.

Default mode is read-only. --apply installs the upstream single-skill package
and adds one MCP entry. The local loopback MCP handshake and tools/list are
required. Runtime tool availability within a running OMP session still needs
an OMP-native /mcp test; the script does not claim that final verification.
"""
from __future__ import annotations

import argparse
import copy
import http.client
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

NAME = 'browseros-neo'
DEFAULT_ENDPOINT = 'http://127.0.0.1:9012/mcp'  # example copied from the USER'S BrowserOS tab; override when changed
PROTOCOL = '2025-06-18'


class ValidationError(Exception):
    """A failed admission gate, not a successful installation."""


def validate_endpoint(endpoint: str) -> tuple[str, int]:
    try:
        p = urlparse(endpoint)
        port = p.port
    except ValueError as exc:
        raise ValidationError('Invalid endpoint URL/port') from exc
    if (p.scheme != 'http' or p.netloc != f'127.0.0.1:{port}'
            or p.hostname != '127.0.0.1' or p.path != '/mcp'
            or p.query or p.fragment or p.params or not port or not (1 <= port <= 65535)):
        raise ValidationError('Endpoint must be exactly http://127.0.0.1:<port>/mcp')
    return '127.0.0.1', port


def resolve_config_path(home: Path, env: dict[str, str]) -> Path:
    """Use OMP's profile-specific root; never silently configure a different profile."""
    root_name = env.get('PI_CONFIG_DIR') or '.omp'
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', root_name) or root_name in ('.', '..'):
        raise ValidationError('Unsafe PI_CONFIG_DIR name')
    profile = env.get('OMP_PROFILE', env.get('PI_PROFILE', ''))
    if profile and (not re.fullmatch(r'[A-Za-z0-9_.-]+', profile) or profile in ('.', '..')):
        raise ValidationError('Unsafe OMP profile name')
    root = home / root_name
    if profile:
        return root / 'profiles' / profile / 'agent' / 'mcp.json'
    custom = env.get('PI_CODING_AGENT_DIR')
    if custom:
        path = Path(custom).expanduser()
        if not path.is_absolute():
            raise ValidationError('PI_CODING_AGENT_DIR must be an absolute path')
        return path / 'mcp.json'
    return root / 'agent' / 'mcp.json'


def merge_config(original: object, endpoint: str) -> dict:
    validate_endpoint(endpoint)
    if not isinstance(original, dict):
        raise ValidationError('OMP configuration is not an object')
    out = copy.deepcopy(original)
    servers = out.setdefault('mcpServers', {})
    if not isinstance(servers, dict):
        raise ValidationError('mcpServers is not a map')
    for field in ('disabledServers', 'enabledServers'):
        if field in out and (not isinstance(out[field], list) or
                              any(not isinstance(v, str) for v in out[field])):
            raise ValidationError(f'{field} is invalid')
    intended = {'type': 'http', 'url': endpoint}
    current = servers.get(NAME)
    if current is not None and current != intended:
        raise ValidationError('Conflicting browseros-neo entry; refusing to overwrite')
    servers[NAME] = intended
    if NAME in out.get('disabledServers', []):
        out['disabledServers'] = [v for v in out['disabledServers'] if v != NAME]
    return out


def _load_config(path: Path) -> dict:
    if path.is_symlink():
        raise ValidationError('Refusing symlinked OMP config')
    if not path.exists():
        return {}
    if not path.is_file():
        raise ValidationError('OMP config is not a regular file')
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError('Existing OMP config cannot be read as valid JSON') from exc
    if not isinstance(data, dict):
        raise ValidationError('Existing OMP config must be an object')
    return data


def _atomic_bytes(path: Path, data: bytes, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temp, mode)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def write_config_atomically(path: Path, result: dict) -> Path | None:
    path = path.expanduser()
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValidationError('Refusing non-regular or symlinked OMP config')
    previous = path.read_bytes() if path.exists() else None
    mode = (path.stat().st_mode & 0o777) if previous is not None else 0o600
    backup = None
    if previous is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        backup = path.with_name(path.name + '.bak.' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
        with backup.open('xb') as stream:
            stream.write(previous)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(backup, mode)
    _atomic_bytes(path, (json.dumps(result, indent=2, ensure_ascii=False) + '\n').encode('utf-8'), mode)
    return backup


def restore_backup(path: Path, backup: Path, expected_current: dict) -> None:
    """Only roll back the exact version we wrote; don't destroy intervening edits."""
    if path.is_symlink() or backup.is_symlink() or not backup.is_file():
        raise ValidationError('Unsafe rollback path')
    if _load_config(path) != expected_current:
        raise ValidationError('Configuration changed since install; refusing rollback overwrite')
    _atomic_bytes(path, backup.read_bytes(), backup.stat().st_mode & 0o777)


def assert_target_mac(expected_host: str) -> None:
    if sys.platform != 'darwin':
        raise ValidationError('Target host is not macOS')
    host = platform.node().split('.')[0]
    if host != expected_host:
        raise ValidationError(f'Wrong target host: {host}; expected {expected_host}')
    if hasattr(os, 'geteuid') and os.geteuid() == 0:
        raise ValidationError('Refusing to install as root; use the OMP account')


def send_mcp_request(endpoint: str, method: str, params: object, request_id: int | None,
                     session_id: str | None = None) -> tuple[dict | None, str | None]:
    host, port = validate_endpoint(endpoint)
    request = {'jsonrpc': '2.0', 'method': method}
    if request_id is not None:
        request['id'] = request_id
    if params is not None:
        request['params'] = params
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream',
               'MCP-Protocol-Version': PROTOCOL}
    if session_id:
        headers['Mcp-Session-Id'] = session_id
    conn = http.client.HTTPConnection(host, port, timeout=4)
    try:
        conn.request('POST', '/mcp', body=json.dumps(request), headers=headers)
        res = conn.getresponse()
        new_session = res.getheader('Mcp-Session-Id') or session_id
        if method == 'notifications/initialized' and res.status == 202:
            res.read(2048)
            return None, new_session
        if res.status != 200:
            raise ValidationError(f'BrowserOS MCP HTTP response {res.status} for {method}')
        ctype = res.getheader('Content-Type', '').lower()
        if 'text/event-stream' in ctype:
            messages = []
            payload = None
            for _ in range(300):
                line = res.readline(8193)
                if not line:
                    break
                if len(line) > 8192:
                    raise ValidationError('MCP SSE line exceeds safety limit')
                if line.startswith(b'data:'):
                    messages.append(line[5:].strip())
                if not line.strip() and messages:
                    payload = b'\n'.join(messages)
                    break
            else:
                raise ValidationError('MCP SSE response too long')
            if payload is None:
                raise ValidationError('Incomplete MCP SSE event (missing delimiter or data)')
        elif 'application/json' in ctype:
            payload = res.read(1024 * 1024 + 1)
            if len(payload) > 1024 * 1024:
                raise ValidationError('MCP JSON response too large')
        else:
            raise ValidationError('BrowserOS did not return MCP JSON or SSE')
        try:
            obj = json.loads(payload)
        except (ValueError, UnicodeError) as exc:
            raise ValidationError('MCP response JSON is invalid') from exc
        if not isinstance(obj, dict) or obj.get('error'):
            raise ValidationError('MCP response returned a protocol error')
        if request_id is not None and obj.get('id') != request_id:
            raise ValidationError('MCP response ID mismatch')
        return obj, new_session
    except (OSError, TimeoutError, http.client.HTTPException) as exc:
        raise ValidationError(f'MCP transport failed: {type(exc).__name__}') from exc
    finally:
        conn.close()


def probe_mcp(endpoint: str) -> list[str]:
    validate_endpoint(endpoint)
    init, session = send_mcp_request(endpoint, 'initialize', {
        'protocolVersion': PROTOCOL, 'capabilities': {},
        'clientInfo': {'name': 'glaciereq-omp-preflight', 'version': '1.0'}}, 1)
    if not isinstance(init, dict) or not isinstance(init.get('result'), dict) or not init['result'].get('protocolVersion'):
        raise ValidationError('BrowserOS MCP initialize was not acknowledged')
    send_mcp_request(endpoint, 'notifications/initialized', None, None, session)
    listed, session = send_mcp_request(endpoint, 'tools/list', {}, 2, session)
    tools = listed.get('result', {}).get('tools') if isinstance(listed, dict) else None
    if not isinstance(tools, list) or not tools:
        raise ValidationError('BrowserOS MCP did not expose any tools')
    names = [t.get('name') for t in tools if isinstance(t, dict) and isinstance(t.get('name'), str)]
    if not names:
        raise ValidationError('MCP tools/list contains no named tools')
    return names


def skill_installed(home: Path) -> bool:
    for path in (home / '.agents/skills' / NAME / 'SKILL.md',
                 home / '.omp/agent/skills' / NAME / 'SKILL.md'):
        if path.is_file():
            try:
                content = path.read_text(encoding='utf-8')
            except OSError:
                continue
            if 'name: browseros-neo' in content and content.lstrip().startswith('---'):
                return True
    return False


def install_skill_command() -> list[str]:
    return ['npx', 'skills', 'add', 'browseros-ai/browseros', '--skill', NAME, '-g', '-y']


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Install exactly one skill and MCP config entry')
    parser.add_argument('--refresh-skill', action='store_true', help='Reinstall skill even if present, with --apply')
    parser.add_argument('--endpoint', default=DEFAULT_ENDPOINT, help='Copy from BrowserOS MCP page (dynamic across builds)')
    parser.add_argument('--config', type=Path, help='Explicit OMP file, otherwise active profile is selected')
    parser.add_argument('--expected-host', default='KcBs-MacBook-Air')
    args = parser.parse_args()
    try:
        assert_target_mac(args.expected_host)
        home = Path.home()
        path = args.config if args.config else resolve_config_path(home, os.environ)
        path = path.expanduser()
        existing = _load_config(path)
        candidate = merge_config(existing, args.endpoint)
        names = probe_mcp(args.endpoint)
        changed = candidate != existing
        print('HOST_VERIFIED=1 MCP_INITIALIZE=1 MCP_TOOLS_LIST=1 CONFIG_CHANGE_NEEDED=' + str(int(changed)))
        print(f'TOOLS_COUNT={len(names)} CONFIG_PATH={path}')
        if not args.apply:
            print('DRY_RUN=1 NO_FILES_MODIFIED=1')
            return 0
        if not shutil.which('omp'):
            raise ValidationError('OMP command not in this account PATH; refusing unverified install')
        if not skill_installed(home) or args.refresh_skill:
            if not shutil.which('npx'):
                raise ValidationError('npx unavailable; cannot install BrowserOS skill')
            subprocess.run(install_skill_command(), check=True, timeout=180)
        if not skill_installed(home):
            raise ValidationError('BrowserOS skill absent from recognized global skill roots')
        backup = write_config_atomically(path, candidate) if changed else None
        if _load_config(path) != candidate:
            raise ValidationError('OMP config changed during readback; preserved backup, not overwriting intervening changes')
        print('LOCAL_CONFIG_VERIFIED=1 SKILL_FILE_VERIFIED=1')
        print(f'CONFIG_CHANGED={int(changed)} BACKUP={backup or "none"}')
        print('OMP_RUNTIME_MCP_TEST_PENDING=1')
        return 0
    except (ValidationError, OSError, subprocess.SubprocessError) as exc:
        print(f'NOT_INSTALLED_OR_UNVERIFIED: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
