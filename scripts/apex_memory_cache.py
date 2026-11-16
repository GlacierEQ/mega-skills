"""Local memory-search cache. Entries expire, and a write drops that account's hits."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

CACHE_TTL_SECONDS = 900


def query_hash(query: str) -> str:
    return hashlib.sha256(query.strip().lower().encode()).hexdigest()


def scope_fingerprint(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()[:12]


def mem0_prefix(account: str, user_id: str) -> str:
    return f"mem0:{account}:{user_id}:"


def mem0_cache_key(account: str, user_id: str, query: str) -> str:
    return mem0_prefix(account, user_id) + query_hash(query)


def pinecone_cache_key(host: str, api_key: str, query: str) -> str:
    return f"pc:{host}:{scope_fingerprint(api_key)}:{query_hash(query)}"


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _store(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    path.chmod(0o600)


def cache_get(path: Path, key: str, now: float | None = None) -> str | None:
    entry = _load(path).get(key)
    if not isinstance(entry, dict):
        return None
    stored = entry.get("t")
    value = entry.get("v")
    if not isinstance(stored, (int, float)) or not isinstance(value, str):
        return None
    current = time.time() if now is None else now
    if current - float(stored) > CACHE_TTL_SECONDS:
        return None
    return value


def cache_set(path: Path, key: str, value: str, now: float | None = None) -> None:
    data = _load(path)
    data[key] = {"v": value, "t": time.time() if now is None else now}
    _store(path, data)


def invalidate_prefix(path: Path, prefix: str) -> int:
    data = _load(path)
    stale = [key for key in data if str(key).startswith(prefix)]
    for key in stale:
        del data[key]
    if stale:
        _store(path, data)
    return len(stale)
