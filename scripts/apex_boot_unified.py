#!/usr/bin/env python3
"""Load a local env file and write a boot receipt that lists missing key names only."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

try:
    import httpx
except ImportError:
    httpx = None

HOME = Path.home()
ENV_PATH = Path(os.environ.get("APEX_ENV_PATH", str(HOME / ".env")))
LOG_DIR = Path(os.environ.get("APEX_LOG_DIR", str(HOME / "FORENSIC_AUDIT")))

REQUIRED_KEYS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "SUPERMEMORY_API_KEY",
    "MEM0_API_KEY",
    "MEMORY_PLUGIN_TOKEN",
    "GH_TOKEN",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
]


def _logger() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("APEX_BOOT")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler = logging.FileHandler(LOG_DIR / f"apex_boot_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


_ASSIGNMENT = re.compile(
    r"""([A-Za-z_][A-Za-z0-9_]*)\s*=\s*("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[^\s#]+)"""
)


def load_env(path: Path = ENV_PATH) -> Dict[str, str]:
    loaded: Dict[str, str] = {}
    if not path.exists():
        return loaded
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = re.sub(r"^(export\s+|declare\s+-x\s+)", "", raw.strip())
        if not line or line.startswith("#"):
            continue
        for match in _ASSIGNMENT.finditer(line):
            key = match.group(1)
            value = match.group(2).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
                value = value[1:-1]
            if key and value:
                os.environ.setdefault(key, value)
                loaded[key] = value
    return loaded


def verify_keys() -> Dict[str, object]:
    missing = [key for key in REQUIRED_KEYS if not os.environ.get(key)]
    return {"present": len(REQUIRED_KEYS) - len(missing), "total": len(REQUIRED_KEYS), "missing": missing}


def check_runtime() -> Dict[str, str]:
    git_version = "missing"
    try:
        git_version = subprocess.check_output(["git", "--version"], stderr=subprocess.DEVNULL).decode().strip()
    except (OSError, subprocess.CalledProcessError):
        git_version = "missing"
    return {"os": platform.platform(), "python": sys.version.split()[0], "git": git_version}


async def check_local_locus(endpoint: str) -> str:
    if httpx is None:
        return "OFFLINE (BYPASS)"
    headers = {"Content-Type": "application/json"}
    sigil = os.environ.get("MICROWAVE_AUTH_SIGIL", "")
    if sigil:
        headers["Authorization"] = f"Bearer {sigil}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                headers=headers,
                json={"directive": "PING", "timestamp": datetime.now(timezone.utc).isoformat()},
                timeout=3.0,
            )
            return f"ONLINE ({response.status_code})"
    except (httpx.HTTPError, OSError):
        return "OFFLINE (BYPASS)"


def receipt_digest(report: dict) -> str:
    payload = {key: value for key, value in report.items() if key != "sha256"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def write_boot_receipt(report: dict, directory: Path = LOG_DIR) -> Path:
    payload = {key: value for key, value in report.items() if key != "sha256"}
    document = {"sha256": receipt_digest(payload), "report": payload}
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / "latest_boot_receipt.json"
    destination.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    destination.chmod(0o600)
    return destination


async def main() -> int:
    log = _logger()
    env = load_env()
    runtime = check_runtime()
    keys = verify_keys()
    endpoint = os.environ.get("SYNTHESIZER_LOCUS_ENDPOINT", "http://127.0.0.1:8000/invoke")
    locus = await check_local_locus(endpoint)
    report = {
        "booted_at": datetime.now(timezone.utc).isoformat(),
        "env_loaded": len(env),
        "runtime": runtime,
        "core_keys": keys,
        "locus": locus,
    }
    receipt = write_boot_receipt(report)
    log.info(
        "APEX Boot Complete | env=%d | keys=%d/%d | locus=%s | receipt=%s",
        len(env),
        keys["present"],
        keys["total"],
        locus,
        receipt,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
