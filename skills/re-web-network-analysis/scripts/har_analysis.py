#!/usr/bin/env python3
"""Web/network capture analysis: strict HAR validation and inventory.

Local companion to REA's inspect_web_network_capture (verified live on
6.7.0). REA validates HAR strictly - a capture exported without the
`cookies: []` field on entries is rejected as invalid input, which this
validator reproduces and names. The inventory counts endpoints, methods,
and status classes; credential material found in a capture is flagged,
never echoed.
"""
from __future__ import annotations

import json
from urllib.parse import urlparse

SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key", "proxy-authorization"}


def validate_har(document) -> list[str]:
    """Return structural problems with a HAR document (REA-strict)."""
    problems = []
    if not isinstance(document, dict) or "log" not in document:
        return ["missing top-level 'log' object"]
    log = document["log"]
    if "entries" not in log:
        return ["log.entries missing"]
    for index, entry in enumerate(log["entries"]):
        for field in ("request", "response", "startedDateTime", "time"):
            if field not in entry:
                problems.append(f"entry {index}: missing {field}")
        request = entry.get("request", {})
        for field in ("method", "url", "headers", "cookies"):
            if field not in request:
                problems.append(f"entry {index}: request missing {field} (strict HAR requires cookies: [])")
        response = entry.get("response", {})
        for field in ("status", "headers", "cookies", "content"):
            if field not in response:
                problems.append(f"entry {index}: response missing {field}")
    return problems


def inventory(document: dict) -> dict:
    """Endpoint/method/status inventory over a valid HAR document."""
    entries = document["log"]["entries"]
    endpoints = {}
    methods = {}
    statuses = {}
    sensitive = []
    for entry in entries:
        request, response = entry["request"], entry["response"]
        parsed = urlparse(request["url"])
        key = f"{request['method']} {parsed.netloc}{parsed.path}"
        endpoints[key] = endpoints.get(key, 0) + 1
        methods[request["method"]] = methods.get(request["method"], 0) + 1
        status_class = f"{int(response['status']) // 100}xx"
        statuses[status_class] = statuses.get(status_class, 0) + 1
        for header in request.get("headers", []):
            if header["name"].lower() in SENSITIVE_HEADERS:
                sensitive.append({"endpoint": key, "header": header["name"],
                                    "value": "<redacted: present>"})
    return {
        "format": "har",
        "entries": len(entries),
        "endpoints": endpoints,
        "methods": methods,
        "status_classes": statuses,
        "sensitive_headers": sensitive,
        "limitations": ["captured traffic proves what was recorded, not the full API surface"],
    }


def analyze(document) -> dict:
    problems = validate_har(document)
    if problems:
        return {"valid": False, "problems": problems}
    return {"valid": True, **inventory(document)}


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate and inventory a HAR capture.")
    parser.add_argument("path")
    args = parser.parse_args(argv)
    document = json.load(open(args.path, encoding="utf-8"))
    result = analyze(document)
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
