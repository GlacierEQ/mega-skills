"""Shared GitHub auth + rate-limit-aware request core for the github skill.

Auth order: gh CLI secure store first, Postman 'Muse Keys' GitHub vars fallback.
Retries 429/5xx/rate-limit 403s with backoff (honors Retry-After and
X-RateLimit-Reset, capped). Never retries 401/404/422.
"""
import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import urllib.error

REST_BASE = "https://api.github.com"
GRAPHQL_URL = "https://api.github.com/graphql"
GET_ENV_KEY = "/home/hatch/workspace/skills/postman/bin/get-env-key"
KEY_VARS = ["GITHUB_VAULT_TAIL", "Github", "GITHUB_TOKEN", "GITHUB_PAT", "GITHUB_PAT2",
            "GITHUB_PAT3", "Github_Master", "GITHUB_AWESOME_FORENSICS_TOKEN",
            "github"]
MAX_ATTEMPTS = 4
MAX_WAIT_SECS = 600


def get_key() -> str:
    try:
        key = subprocess.run(["gh", "auth", "token"], capture_output=True,
                             text=True, timeout=15).stdout.strip()
        if key:
            return key
    except Exception:  # noqa: BLE001
        pass
    for var in KEY_VARS:
        try:
            key = subprocess.run([GET_ENV_KEY, var], capture_output=True,
                                 text=True, timeout=30).stdout.strip()
        except Exception:  # noqa: BLE001
            continue
        if key:
            return key
    return ""


def _headers(token):
    return {"Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": "Bearer " + token}


def _parse(resp):
    raw = resp.read().decode("utf-8") or "{}"
    try:
        parsed = json.loads(raw)
    except Exception:  # noqa: BLE001
        parsed = {"raw": raw[:2000]}
    return parsed, dict(resp.headers or {})


def _send(req, timeout):
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            parsed, headers = _parse(resp)
            return {"status": resp.status, "body": parsed, "headers": headers}
    except urllib.error.HTTPError as exc:
        try:
            err_body = json.loads(exc.read().decode("utf-8") or "{}")
        except Exception:  # noqa: BLE001
            err_body = {}
        return {"status": exc.code, "body": err_body,
                "headers": dict(exc.headers or {})}


def _retryable(status, body):
    if status == 429 or status in (500, 502, 503, 504):
        return True
    if status == 403:
        blob = json.dumps(body).lower()
        if "rate limit" in blob or "abuse" in blob:
            return True
    return False


def _wait_secs(headers, attempt):
    ra = headers.get("Retry-After") or headers.get("retry-after")
    if ra:
        try:
            return min(int(ra) + 2, MAX_WAIT_SECS)
        except ValueError:
            pass
    reset = headers.get("X-RateLimit-Reset") or headers.get("x-ratelimit-reset")
    if reset:
        try:
            wait = int(reset) - int(time.time()) + 5
            if wait > 0:
                return min(wait, MAX_WAIT_SECS)
        except ValueError:
            pass
    return min(5 * (3 ** (attempt - 1)), MAX_WAIT_SECS)


def _with_retries(label, no_retry, timeout, send_fn):
    token = get_key()
    if not token:
        return {"status": 0, "body": {
            "error": "no GitHub auth: gh not logged in and no key in Postman Muse Keys env"}}
    attempts = 1 if no_retry else MAX_ATTEMPTS
    last = None
    for attempt in range(1, attempts + 1):
        try:
            r = send_fn(token)
        except Exception as e:  # network-level failure
            if attempt < attempts:
                wait = min(5 * (3 ** (attempt - 1)), MAX_WAIT_SECS)
                print(f"[{label}] network error, retry {attempt}/{attempts} in {wait}s",
                      file=sys.stderr)
                time.sleep(wait)
                continue
            return {"status": 0, "body": {"error": f"network failure: {e}"}}
        last = r
        if r["status"] == 401:
            r["body"]["hint"] = ("GitHub rejected the token. Re-authenticate: "
                                 "gh auth login --with-token <PAT>, then retry. "
                                 "A 401 will not clear on its own — never retry it.")
            return r
        if _retryable(r["status"], r["body"]) and attempt < attempts:
            wait = _wait_secs(r.get("headers", {}), attempt)
            print(f"[{label}] HTTP {r['status']} (rate limit/server), "
                  f"retry {attempt}/{attempts} in {wait}s", file=sys.stderr)
            time.sleep(wait)
            continue
        return r
    if last and _retryable(last["status"], last["body"]):
        last["body"]["hint"] = ("Rate limit still exhausted after retries. "
                                "Stop hammering — wait for the reset window.")
    return last


def rest_request(method, path, params=None, data=None, no_retry=False,
                 timeout=30, label="github-api"):
    if not path.startswith("/"):
        path = "/" + path
    url = REST_BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    body = json.dumps(data).encode("utf-8") if data is not None else None

    def send(token):
        req = urllib.request.Request(url, data=body, headers=_headers(token),
                                     method=method.upper())
        if body is not None:
            req.add_header("Content-Type", "application/json")
        return _send(req, timeout)

    return _with_retries(label, no_retry, timeout, send)


def graphql_request(query, variables=None, no_retry=False, timeout=60,
                    label="github-graphql"):
    payload = json.dumps({"query": query,
                          "variables": variables or {}}).encode("utf-8")

    def send(token):
        req = urllib.request.Request(GRAPHQL_URL, data=payload,
                                     headers=_headers(token), method="POST")
        req.add_header("Content-Type", "application/json")
        return _send(req, timeout)

    return _with_retries(label, no_retry, timeout, send)


def paginate_graphql(query, variables, connection_path, no_retry=False,
                     timeout=60, page_size=100, label="github-graphql"):
    """Auto-walk a GraphQL connection's pages, merging nodes/edges.

    query must accept $after and select the connection with
    pageInfo { hasNextPage endCursor } plus nodes { ... } or edges { node { ... } }.
    connection_path: dotted path, e.g. 'viewer.repositories'.
    Returns {"status": 200, "pages": N, "nodes": [...]} (or "edges", or an error).
    """
    variables = dict(variables or {})
    variables["page_size"] = page_size
    merged_nodes, merged_edges = [], []
    use_edges = None
    after = None
    pages = 0
    while True:
        variables["after"] = after
        r = graphql_request(query, variables, no_retry=no_retry,
                            timeout=timeout, label=label)
        if r["status"] != 200:
            return r
        body = r["body"]
        if body.get("errors"):
            return {"status": 200, "body": body,
                    "error": "graphql errors: " + json.dumps(body["errors"])[:300]}
        node = body.get("data", {})
        for part in connection_path.split("."):
            node = (node or {}).get(part, {})
        if not isinstance(node, dict) or "pageInfo" not in node:
            return {"status": 0, "body": {
                "error": f"connection '{connection_path}' not found or missing pageInfo"}}
        if use_edges is None:
            use_edges = "edges" in node and "nodes" not in node
        if use_edges:
            merged_edges.extend(node.get("edges", []))
        else:
            merged_nodes.extend(node.get("nodes", []))
        pages += 1
        pi = node["pageInfo"]
        if not pi.get("hasNextPage"):
            break
        after = pi.get("endCursor")
        if pages > 1000:  # sanity cap
            break
    key = "edges" if use_edges else "nodes"
    return {"status": 200, "pages": pages,
            key: merged_edges if use_edges else merged_nodes}
