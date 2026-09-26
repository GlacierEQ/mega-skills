#!/usr/bin/env python3
"""Read-only source access for the APEX Max Research Engine.

Implements the three source-access actions declared in the
``apex-max-research-engine`` firewall policy:

* ``search_workspace``        -- local corpus search
* ``read_connected_sources``  -- configured connector reads
* ``load_public_sources``    -- guarded public HTTP GET

Standard library only. Nothing here writes to the workspace, mutates a
remote system, or transmits workspace data outward.
"""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
SKILL_NAME = "research-source-access"

# Bounds for the one networked action.
MAX_BYTES = 2_000_000
TIMEOUT_SECONDS = 10
DEFAULT_USER_AGENT = f"{SKILL_NAME}/1.0 (+read-only research source access)"

# Corpus files we are willing to read for search_workspace.
SEARCHABLE_SUFFIXES = {".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".csv"}
MAX_CORPUS_FILES = 5000
MAX_CORPUS_BYTES = 5_000_000
TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _receipt(action: str, detail: dict[str, Any], *, ok: bool, reason: str = "") -> dict[str, Any]:
    return {
        "schema": f"glaciereq.{SKILL_NAME}.receipt.v{SCHEMA_VERSION}",
        "skill": SKILL_NAME,
        "action": action,
        "read_only": True,
        "mutated": False,
        "transmitted": False,
        "ok": ok,
        "reason": reason,
        **detail,
    }


# ── search_workspace ─────────────────────────────────────────────────────


def _iter_corpus(root: Path, roots: list[Path]) -> list[Path]:
    found: list[Path] = []
    for base in roots:
        if not base.exists():
            continue
        candidates = [base] if base.is_file() else base.rglob("*")
        for path in candidates:
            if len(found) >= MAX_CORPUS_FILES:
                return found
            try:
                if not path.is_file() or path.suffix.lower() not in SEARCHABLE_SUFFIXES:
                    continue
                if any(p in {".git", "node_modules", "__pycache__", ".venv"} for p in path.parts):
                    continue
                if path.stat().st_size > MAX_CORPUS_BYTES:
                    continue
            except OSError:
                continue
            found.append(path)
    return found


def search_workspace(payload: dict[str, Any]) -> dict[str, Any]:
    """Rank local corpus files against a query. Never writes anything."""
    root = Path(payload.get("root", ".")).expanduser().resolve()
    roots = [root]
    for extra in payload.get("roots", []) or []:
        roots.append(Path(extra).expanduser().resolve())
    query = str(payload.get("query", "")).strip()
    limit = max(1, min(int(payload.get("limit", 20) or 20), 200))

    if not query:
        return _receipt("search_workspace", {"results": [], "file_count": 0},
                        ok=False, reason="empty_query")

    files = _iter_corpus(root, roots)
    terms = [t.lower() for t in TOKEN_RE.findall(query)]
    if not terms:
        return _receipt("search_workspace", {"results": [], "file_count": len(files)},
                        ok=False, reason="no_indexable_terms")

    scored: list[dict[str, Any]] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        hits = sum(text.count(term) for term in terms)
        if hits:
            scored.append({
                "path": str(path),
                "score": hits,
                "digest": _sha256(str(path).encode("utf-8"))[:16],
            })
    scored.sort(key=lambda item: (-item["score"], item["path"]))

    return _receipt(
        "search_workspace",
        {"results": scored[:limit], "file_count": len(files), "root": str(root)},
        ok=True,
    )


# ── read_connected_sources ──────────────────────────────────────────────


def read_connected_sources(payload: dict[str, Any]) -> dict[str, Any]:
    """Read through declared read-only connectors.

    A connector that declares a write capability is refused. Connectors are
    described in a local ``connectors.json``; nothing is contacted implicitly.
    """
    name = str(payload.get("connector", "")).strip()
    request = payload.get("request", {}) or {}
    config_path = Path(payload.get("connectors_path", "connectors.json")).expanduser()
    method = str(request.get("method", "GET")).upper()

    if method != "GET":
        return _receipt("read_connected_sources", {"connector": name},
                        ok=False, reason=f"method_not_allowed:{method}")

    connectors: dict[str, Any] = {}
    if config_path.is_file():
        try:
            connectors = json.loads(config_path.read_text(encoding="utf-8")).get("connectors", {})
        except (json.JSONDecodeError, OSError):
            connectors = {}

    spec = connectors.get(name)
    if not isinstance(spec, dict):
        return _receipt("read_connected_sources", {"connector": name},
                        ok=False, reason="connector_not_configured")
    if spec.get("read_only") is not True:
        return _receipt("read_connected_sources", {"connector": name},
                        ok=False, reason="connector_not_read_only")
    if spec.get("capabilities") and any(
        c not in {"read", "search"} for c in spec["capabilities"]
    ):
        return _receipt("read_connected_sources", {"connector": name},
                        ok=False, reason="connector_declares_write_capability")

    url = urllib.parse.urljoin(str(spec.get("base_url", "")), str(request.get("path", "")))
    if not url:
        return _receipt("read_connected_sources", {"connector": name},
                        ok=False, reason="connector_has_no_endpoint")
    # Reuse the public-source guard so connectors inherit the same protections.
    return _fetch(url, action="read_connected_sources", connector=name,
                  allow_insecure_http=bool(spec.get("allow_insecure_http", False)))


# ── load_public_sources ─────────────────────────────────────────────────


def _host_is_public(host: str) -> tuple[bool, str]:
    """Refuse anything resolving into private or reserved address space."""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        return False, f"dns_resolution_failed:{exc}"
    for info in infos:
        try:
            addr = ipaddress.ip_address(info[4][0])
        except ValueError:
            return False, "unparseable_address"
        if (addr.is_private or addr.is_loopback or addr.is_link_local
                or addr.is_reserved or addr.is_multicast or addr.is_unspecified):
            return False, f"non_public_address:{addr}"
    return True, ""


def _safe_url(raw: str, allow_insecure_http: bool) -> tuple[str, str]:
    """Validate a URL for a read-only fetch. Returns (url, refusal_reason)."""
    parsed = urllib.parse.urlsplit(raw)
    if parsed.scheme not in ({"https", "http"} if allow_insecure_http else {"https"}):
        return "", f"scheme_not_allowed:{parsed.scheme or 'none'}"
    if not parsed.hostname:
        return "", "missing_host"
    if parsed.username or parsed.password:
        return "", "embedded_credentials_rejected"
    public, reason = _host_is_public(parsed.hostname)
    if not public:
        return "", reason
    return urllib.parse.urlunsplit(parsed), ""


def _fetch(url: str, *, action: str, connector: str = "",
           allow_insecure_http: bool = False) -> dict[str, Any]:
    """Perform the one permitted network operation: a read-only GET."""
    safe, reason = _safe_url(url, allow_insecure_http)
    detail: dict[str, Any] = {"url": url, "connector": connector or None}
    if not safe:
        return _receipt(action, detail, ok=False, reason=reason)

    request = urllib.request.Request(safe, method="GET")  # GET only, always
    request.add_header("User-Agent", DEFAULT_USER_AGENT)
    # Deliberately no Authorization header, no cookies, no API keys.

    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            final = response.geturl()
            if final != safe:
                redirected, redirect_reason = _safe_url(final, allow_insecure_http)
                if not redirected:
                    return _receipt(action, {**detail, "url": final}, ok=False,
                                    reason=f"unsafe_redirect:{redirect_reason}")
            body = response.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as exc:
        return _receipt(action, detail, ok=False, reason=f"http_error:{exc.code}")
    except (urllib.error.URLError, ValueError, OSError) as exc:
        return _receipt(action, detail, ok=False,
                        reason=f"fetch_failed:{type(exc).__name__}")

    truncated = len(body) > MAX_BYTES
    body = body[:MAX_BYTES]
    return _receipt(
        action,
        {**detail,
         "status": "truncated" if truncated else "complete",
         "bytes": len(body),
         "content_sha256": _sha256(body),
         "text": body.decode("utf-8", errors="ignore")},
        ok=True,
    )


def load_public_sources(payload: dict[str, Any]) -> dict[str, Any]:
    """Guarded read-only HTTP GET of public URLs. Pull-only; sends nothing."""
    urls = payload.get("urls", []) or []
    if isinstance(urls, str):
        urls = [urls]
    if not urls:
        return _receipt("load_public_sources", {"sources": []}, ok=False, reason="no_urls")
    allow_insecure = bool(payload.get("allow_insecure_http", False))
    sources = [_fetch(str(u), action="load_public_sources",
                      allow_insecure_http=allow_insecure) for u in urls]
    return _receipt(
        "load_public_sources",
        {"sources": sources, "requested": len(urls),
         "refused": sum(1 for s in sources if not s["ok"])},
        ok=True,
    )


OPERATIONS = {
    "search-workspace": search_workspace,
    "read-connected-sources": read_connected_sources,
    "load-public-sources": load_public_sources,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog=SKILL_NAME, description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    for name in OPERATIONS:
        op = sub.add_parser(name)
        op.add_argument("--input", type=Path, required=True)
        op.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = OPERATIONS[args.operation](payload)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())


