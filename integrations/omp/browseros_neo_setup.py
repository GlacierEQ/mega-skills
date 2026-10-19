#!/usr/bin/env python3
"""Guarded additive BrowserOS Neo integration for an existing OMP agent.

Defaults to read-only diagnostics. --apply requires the exact Mac identity and
live loopback endpoint, then installs the official skill and updates OMP JSON
atomically, preserving all unrelated MCP servers and generating a backup.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

NAME = "browseros-neo"
DEFAULT_ENDPOINT = "http://127.0.0.1:9012/mcp"
DEFAULT_CONFIG = Path.home() / ".omp" / "agent" / "mcp.json"


class ValidationError(Exception):
    pass


def validate_endpoint(endpoint: str) -> tuple[str, int]:
    value = urlparse(endpoint)
    if value.scheme != "http" or value.hostname != "127.0.0.1" or value.path != "/mcp" or value.query or value.fragment or value.username or value.password:
        raise ValidationError("Only the explicit localhost HTTP /mcp endpoint is allowed")
    try:
        port = value.port
    except ValueError as error:
        raise ValidationError("Invalid endpoint port") from error
    if port is None:
        raise ValidationError("Endpoint must contain an explicit port")
    return value.hostname, port


def merge_config(original: object, endpoint: str) -> dict:
    validate_endpoint(endpoint)
    if not isinstance(original, dict):
        raise ValidationError("OMP configuration must be an object")
    result = copy.deepcopy(original)
    servers = result.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        raise ValidationError("Existing mcpServers is not a map")
    disabled = result.get("disabledServers", [])
    if not isinstance(disabled, list) or any(not isinstance(x, str) for x in disabled):
        raise ValidationError("Existing disabledServers is invalid")
    intended = {"type": "http", "url": endpoint}
    existing = servers.get(NAME)
    if existing is not None and existing != intended:
        raise ValidationError("An existing browseros-neo entry differs; refusing to overwrite it")
    servers[NAME] = intended
    if NAME in disabled:
        result["disabledServers"] = [x for x in disabled if x != NAME]
    return result


def install_skill_command() -> list[str]:
    return ["npx", "skills", "add", "browseros-ai/browseros", "--skill", NAME, "-g", "-y"]


def write_config_atomically(path: Path, result: dict) -> Path | None:
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    mode = 0o600
    if path.exists():
        if not path.is_file() or path.is_symlink():
            raise ValidationError("Refusing to alter a non-regular or symlinked config")
        mode = path.stat().st_mode & 0o777
        backup = path.with_name(path.name + ".bak." + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
        shutil.copy2(path, backup)
    serialized = (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode()
    fd, tmp = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(serialized)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return backup


def assert_expected_mac(expected_host: str) -> None:
    if sys.platform != "darwin":
        raise ValidationError("This installer must run on the target macOS machine")
    local = platform.node().split(".")[0]
    if local != expected_host:
        raise ValidationError(f"Wrong Mac: expected {expected_host}; got {local}")


def probe_port(endpoint: str) -> None:
    host, port = validate_endpoint(endpoint)
    try:
        with socket.create_connection((host, port), timeout=3):
            pass
    except OSError as error:
        raise ValidationError(f"BrowserOS loopback endpoint is not accepting connections on port {port}") from error


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--apply", action="store_true", help="Actually install skill and update local OMP configuration")
    cli.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    cli.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    cli.add_argument("--expected-host", default="KcBs-MacBook-Air")
    args = cli.parse_args()
    try:
        assert_expected_mac(args.expected_host)
        probe_port(args.endpoint)
        config_path = args.config.expanduser()
        if config_path.exists():
            if config_path.is_symlink() or not config_path.is_file():
                raise ValidationError("Config must be a regular file")
            config = json.loads(config_path.read_text(encoding="utf-8"))
        else:
            config = {}
        new_config = merge_config(config, args.endpoint)
        changed = new_config != config
        print(f"HOST_OK=1 ENDPOINT_TCP_OK=1 MCP_ENTRY_CHANGE_NEEDED={int(changed)}")
        if not args.apply:
            print("DRY_RUN=1 NO_FILES_MODIFIED=1")
            return 0
        if shutil.which("npx") is None:
            raise ValidationError("npx is not available in the target user's PATH")
        subprocess.run(install_skill_command(), check=True, timeout=180)
        skill_paths = [Path.home() / ".agents" / "skills" / NAME / "SKILL.md", Path.home() / ".omp" / "agent" / "skills" / NAME / "SKILL.md"]
        if not any(p.exists() for p in skill_paths):
            raise ValidationError("The skills CLI did not create a verifiable BrowserOS Neo skill at a discovered global path")
        backup = write_config_atomically(config_path, new_config) if changed else None
        if json.loads(config_path.read_text(encoding="utf-8")) != new_config:
            raise ValidationError("Local OMP readback failed")
        print(f"INSTALL_VERIFIED=1 CONFIG_CHANGED={int(changed)} BACKUP_CREATED={int(backup is not None)}")
        return 0
    except (ValidationError, json.JSONDecodeError, subprocess.SubprocessError, OSError) as error:
        print(f"NOT_INSTALLED_OR_UNVERIFIED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
