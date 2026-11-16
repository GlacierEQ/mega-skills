#!/usr/bin/env python3
"""Forward MCP stdio JSON-RPC to an n8n streamable HTTP endpoint.

N8N_API_KEY is read from the environment and sent as an Authorization header.
It is never placed on a process command line.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Dict, List, Tuple


def endpoint(base_url: str) -> str:
    return base_url.rstrip("/") + "/mcp-server/http"


def sse_payloads(text: str) -> List[str]:
    payloads: List[str] = []
    for block in text.split("\n\n"):
        data_lines = [line[5:].lstrip() for line in block.splitlines() if line.startswith("data:")]
        if data_lines:
            payloads.append("\n".join(data_lines))
    return payloads


def jsonrpc_error(raw: str, message: str) -> str:
    message_id = None
    try:
        message_id = json.loads(raw).get("id")
    except json.JSONDecodeError:
        message_id = None
    return json.dumps({"jsonrpc": "2.0", "id": message_id, "error": {"code": -32000, "message": message}})


def forward(url: str, api_key: str, raw: str, session_id: str | None) -> Tuple[str | None, List[str]]:
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {api_key}",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    request = urllib.request.Request(url, data=raw.encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            new_session = response.headers.get("Mcp-Session-Id") or session_id
            body = response.read()
            if response.status == 202 or not body:
                return new_session, []
            content_type = response.headers.get("Content-Type", "")
            text = body.decode()
            if "text/event-stream" in content_type:
                return new_session, sse_payloads(text)
            return new_session, [text.strip()]
    except urllib.error.HTTPError as exc:
        return session_id, [jsonrpc_error(raw, f"HTTP {exc.code}")]
    except Exception as exc:
        return session_id, [jsonrpc_error(raw, exc.__class__.__name__)]


def main() -> int:
    base_url = os.environ.get("N8N_BASE_URL", "")
    api_key = os.environ.get("N8N_API_KEY", "")
    if not base_url or not api_key:
        print("N8N_BASE_URL and N8N_API_KEY are required", file=sys.stderr)
        return 2
    url = endpoint(base_url)
    session_id = None
    for line in sys.stdin:
        raw = line.strip()
        if not raw:
            continue
        session_id, messages = forward(url, api_key, raw, session_id)
        for message in messages:
            sys.stdout.write(message + "\n")
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
