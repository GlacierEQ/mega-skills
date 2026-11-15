#!/usr/bin/env python3
"""Deduplicate a local env file by key family and probe public whoami endpoints.

Values are read from the env file and sent only as request credentials.
Reports contain key names, short fingerprints, and HTTP status. They do not
contain secret values. A cleaned env file is written only outside git or to
a gitignored path, mode 0600.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import key_hierarchy

ASSIGNMENT = re.compile(
    r"""([A-Za-z_][A-Za-z0-9_]*)\s*=\s*("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[^\s#]+)"""
)


def mask(value: str) -> str:
    if len(value) <= 10:
        return "***"
    return f"{value[:4]}...{value[-2:]}"


def _unquote(raw: str) -> str:
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {'"', "'"}:
        return raw[1:-1]
    return raw


def parse_env(path: Path) -> Dict[str, str]:
    env: Dict[str, str] = {}
    text = path.read_text(encoding="utf-8", errors="ignore")
    for raw in text.splitlines():
        line = re.sub(r"^(export\s+|declare\s+-x\s+)", "", raw.strip())
        if not line or line.startswith("#"):
            continue
        for match in ASSIGNMENT.finditer(line):
            key = match.group(1)
            value = _unquote(match.group(2)).strip()
            if key and value:
                env[key] = value
    return env


def _family_of(name: str) -> str | None:
    for family, spec in key_hierarchy.FAMILIES.items():
        if name == spec["env"] or name in spec["aliases"]:
            return family
    return None


def dedupe(env: Dict[str, str]) -> Tuple[Dict[str, str], List[dict]]:
    grouped: Dict[str, Dict[str, str]] = {}
    loose: Dict[str, str] = {}
    for key, value in env.items():
        family = _family_of(key)
        if family is None:
            loose.setdefault(key, value)
            continue
        grouped.setdefault(family, {})[key] = value

    canonical: Dict[str, str] = {}
    for family, present in grouped.items():
        spec = key_hierarchy.FAMILIES[family]
        names = set(present)
        chosen = spec["env"] if spec["env"] in names else key_hierarchy.pick_winner(family, names)
        if chosen is None:
            continue
        canonical[spec["env"]] = present[chosen]

    for key, value in loose.items():
        if key not in canonical:
            canonical[key] = value

    by_hash: Dict[str, List[str]] = {}
    for key, value in env.items():
        fingerprint = hashlib.sha256(value.encode()).hexdigest()[:12]
        by_hash.setdefault(fingerprint, []).append(key)
    duplicates = [
        {"fingerprint": fingerprint, "keys": names}
        for fingerprint, names in by_hash.items()
        if len(names) > 1
    ]
    return canonical, duplicates


def probe(name: str, url: str, headers: Dict[str, str]) -> dict:
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            return {"provider": name, "status": "PASS", "http_code": response.status}
    except urllib.error.HTTPError as exc:
        status = "AUTH_FAIL" if exc.code in (401, 403) else f"HTTP_{exc.code}"
        return {"provider": name, "status": status, "http_code": exc.code}
    except Exception as exc:
        detail = exc.__class__.__name__
        return {"provider": name, "status": "ERROR", "detail": detail}


def _checks(canon: Dict[str, str]) -> List[Tuple[str, str, Dict[str, str]]]:
    checks: List[Tuple[str, str, Dict[str, str]]] = []
    github = canon.get("GH_TOKEN") or canon.get("GITHUB_TOKEN")
    if github:
        checks.append(("github", "https://api.github.com/user", {"Authorization": f"Bearer {github}", "User-Agent": "apex-audit"}))
    if canon.get("OPENAI_API_KEY"):
        checks.append(("openai", "https://api.openai.com/v1/models", {"Authorization": f"Bearer {canon['OPENAI_API_KEY']}"}))
    if canon.get("ANTHROPIC_API_KEY"):
        checks.append(("anthropic", "https://api.anthropic.com/v1/models", {"x-api-key": canon["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"}))
    if canon.get("GROQ_API_KEY"):
        checks.append(("groq", "https://api.groq.com/openai/v1/models", {"Authorization": f"Bearer {canon['GROQ_API_KEY']}"}))
    if canon.get("DEEPSEEK_API_KEY"):
        checks.append(("deepseek", "https://api.deepseek.com/models", {"Authorization": f"Bearer {canon['DEEPSEEK_API_KEY']}"}))
    notion = canon.get("NOTION_TOKEN") or canon.get("NOTION_API_KEY")
    if notion:
        checks.append(("notion", "https://api.notion.com/v1/users/me", {"Authorization": f"Bearer {notion}", "Notion-Version": "2022-06-28"}))
    if canon.get("CLOUDFLARE_API_TOKEN"):
        checks.append(("cloudflare", "https://api.cloudflare.com/client/v4/user/tokens/verify", {"Authorization": f"Bearer {canon['CLOUDFLARE_API_TOKEN']}"}))
    if canon.get("BUILDKITE_API_TOKEN"):
        checks.append(("buildkite", "https://api.buildkite.com/v2/user", {"Authorization": f"Bearer {canon['BUILDKITE_API_TOKEN']}"}))
    if canon.get("VERCEL_TOKEN"):
        checks.append(("vercel", "https://api.vercel.com/v2/user", {"Authorization": f"Bearer {canon['VERCEL_TOKEN']}"}))
    if canon.get("SUPABASE_URL") and canon.get("SUPABASE_ANON_KEY"):
        base = canon["SUPABASE_URL"].rstrip("/")
        checks.append(("supabase", f"{base}/rest/v1/", {"apikey": canon["SUPABASE_ANON_KEY"]}))
    if canon.get("GEMINI_API_KEY"):
        checks.append(("gemini", "https://generativelanguage.googleapis.com/v1beta/models", {"x-goog-api-key": canon["GEMINI_API_KEY"]}))
    return checks


def _git_toplevel(start: Path) -> Path | None:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=start if start.is_dir() else start.parent,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip())


def _existing_ancestor(path: Path) -> Path:
    current = path if path.is_dir() else path.parent
    while not current.exists():
        parent = current.parent
        if parent == current:
            return current
        current = parent
    return current


def destination_is_safe(path: Path) -> bool:
    start = _existing_ancestor(path)
    top = _git_toplevel(start)
    if top is None:
        return True
    try:
        path.resolve().relative_to(top.resolve())
    except ValueError:
        return True
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", "--", str(path)],
        cwd=top,
        check=False,
    )
    return ignored.returncode == 0


def write_clean_env(source: Path, canonical: Dict[str, str]) -> Path:
    destination = source.with_suffix(".deduped.env")
    if not destination_is_safe(destination):
        raise SystemExit(f"refusing to write secrets inside the git repo: {destination}")
    lines = [f"{key}={value}" for key, value in sorted(canonical.items())]
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    destination.chmod(0o600)
    return destination


def report_contains_secret(report: dict, values: Dict[str, str]) -> bool:
    printable = json.dumps(report)
    return any(value and value in printable for value in values.values())


def build_report(raw: Dict[str, str], canonical: Dict[str, str], duplicates: List[dict], probes: List[dict]) -> dict:
    return {
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "raw_count": len(raw),
        "canonical_count": len(canonical),
        "canonical_names": sorted(canonical),
        "duplicates": duplicates,
        "live_probes": sorted(probes, key=lambda item: item["provider"]),
    }


def audit(env_path: Path, run_probes: bool = True) -> dict:
    raw = parse_env(env_path)
    canonical, duplicates = dedupe(raw)
    probes: List[dict] = []
    if run_probes:
        jobs = _checks(canonical)
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(probe, name, url, headers) for name, url, headers in jobs]
            for future in as_completed(futures):
                probes.append(future.result())
    return build_report(raw, canonical, duplicates, probes)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", default=str(Path.home() / ".env"))
    parser.add_argument("--out", default="key_audit_report.json")
    parser.add_argument("--write-clean-env", action="store_true")
    parser.add_argument("--skip-probes", action="store_true")
    args = parser.parse_args(argv)
    env_path = Path(args.env).expanduser()
    if not env_path.is_file():
        print(json.dumps({"status": "MISSING_ENV", "path": str(env_path)}))
        return 2
    raw = parse_env(env_path)
    canonical, duplicates = dedupe(raw)
    probes: List[dict] = []
    if not args.skip_probes:
        jobs = _checks(canonical)
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(probe, name, url, headers) for name, url, headers in jobs]
            for future in as_completed(futures):
                probes.append(future.result())
    report = build_report(raw, canonical, duplicates, probes)
    if report_contains_secret(report, raw):
        raise SystemExit("report included a secret value; refusing to write")
    out_path = Path(args.out)
    if not destination_is_safe(out_path):
        raise SystemExit(f"refusing to write the report inside the git repo: {out_path}")
    printable = json.dumps(report, indent=2)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(printable + "\n", encoding="utf-8")
    out_path.chmod(0o600)
    if args.write_clean_env:
        write_clean_env(env_path, canonical)
    print(printable)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
