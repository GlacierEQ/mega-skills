#!/usr/bin/env python3
"""Non-mutating Oh My Pi host-risk preflight, never a mission-completion attestation.

No model requests, credentials, network access, session transcript reads, or system changes.
Compatible with Python 3.9+ and lightweight Intel macOS hosts.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
from typing import Optional

SENSITIVE_GIT_PATHS = (
    "agent.db",
    "config.yml",
    "sessions/probe.jsonl",
    "secret-placeholder.key",
    "cred-candidates.json",
)
ACCEPTANCE_GATES = (
    "mission_identity_bound",
    "context_applied",
    "capability_resolved",
    "authorized_effect_executed",
    "provider_readback",
    "cross_process_recovery",
    "receipt_preserved",
    "second_run_reuse",
)
YAML_KEY_RE = re.compile(r"^(\\s*)([A-Za-z][A-Za-z0-9_-]*):(?:\\s*(.*))?$")


def extract_config_value(text: str, dotted_key: str) -> Optional[str]:
    """Read only a known simple scalar from OMP's nested config.yml.

    Deliberately not a general YAML parser. Unknown/complex syntax returns None;
    it never emits whole configuration or values of unrequested keys.
    """
    wanted = dotted_key.split(".")
    parents = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = YAML_KEY_RE.match(line)
        if not m:
            continue
        indent, key, raw_value = len(m.group(1).expandtabs(2)), m.group(2), (m.group(3) or "")
        while parents and parents[-1][0] >= indent:
            parents.pop()
        path = [value for _, value in parents] + [key]
        if path == wanted:
            value = raw_value.strip().split(" #", 1)[0].strip()
            if value.startswith(('"', "'")) and len(value) >= 2 and value[-1] == value[0]:
                value = value[1:-1]
            return value or None
        if not raw_value.strip() or raw_value.strip().startswith("#"):
            parents.append((indent, key))
    return None


def _git(base: Path, args: list[str]) -> Optional[subprocess.CompletedProcess]:
    try:
        return subprocess.run(
            ["git", "-C", str(base), *args],
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def _git_risks(base: Path) -> tuple[list[str], list[str], bool]:
    if not (base / ".git").exists():
        return [], [], False
    unignored, tracked = [], []
    for relative in SENSITIVE_GIT_PATHS:
        ignored_result = _git(base, ["check-ignore", "--no-index", "-q", "--", relative])
        if ignored_result is None or ignored_result.returncode != 0:
            unignored.append(relative)
        tracked_result = _git(base, ["ls-files", "--error-unmatch", "--", relative])
        if tracked_result is not None and tracked_result.returncode == 0:
            tracked.append(relative)
    return unignored, tracked, True


def audit_omp(
    *,
    home: Path,
    free_gib: Optional[float],
    load_1: Optional[float],
    cpu_count: Optional[int],
    executable: Path,
) -> dict:
    agent = home / ".omp" / "agent"
    findings = []

    def finding(id_: str, severity: str, observation: str, action: str) -> None:
        findings.append({"id": id_, "severity": severity, "observation": observation, "next_action": action})

    if not executable.is_file() or not os.access(executable, os.X_OK):
        finding("omp_missing", "HIGH", "OMP executable not verified", "Restore executable and verify its signed/versioned release")

    config_path = agent / "config.yml"
    config = None
    if config_path.is_file():
        try:
            config = config_path.read_text(encoding="utf-8")
        except OSError:
            pass
    if config is None:
        finding("config_unavailable", "HIGH", "OMP config unavailable", "Recover settings from the active profile before changes")
    else:
        approval = extract_config_value(config, "tools.approvalMode")
        memory = extract_config_value(config, "memory.backend")
        if approval == "yolo":
            finding("approval_mode_yolo", "HIGH", "Unrestricted tool approval is configured", "Review effect-specific authorization; avoid automated writes before scope is proven")
        elif approval is None:
            finding("approval_mode_unknown", "MEDIUM", "Approval mode not explicitly resolved", "Read back the active OMP profile's effective mode")
        if memory == "hindsight":
            finding("hindsight_unverified", "INFO", "Hindsight selected in config", "Prove cross-session recalled source, applied correction and cursor; config alone is not proof")

    unignored, tracked, has_git = _git_risks(agent)
    if has_git and unignored:
        finding("secrets_unignored", "HIGH", "Sensitive OMP runtime paths lack Git ignore protection", "Protect paths in .gitignore and verify before any git add; do not stage secrets")
    if tracked:
        finding("sensitive_files_tracked", "HIGH", "Sensitive runtime paths already present in Git index", "Stop publishing; inspect index/history and revoke exposed credentials if applicable")
    if not has_git:
        finding("git_not_present", "INFO", "No local Git metadata for OMP agent configuration", "Git protection check skipped; validate the actual owning repository")

    for file_name in ("agent.db", "config.yml"):
        file = agent / file_name
        if file.is_file():
            try:
                if stat.S_IMODE(file.stat().st_mode) & 0o077:
                    finding("sensitive_file_permissions", "MEDIUM", "Sensitive OMP state has group/other permission bits", "Review file and parent permissions before enabling remote users")
                    break
            except OSError:
                pass

    if free_gib is not None and free_gib < 12:
        finding("disk_pressure", "HIGH", "Under 12 GiB of free host storage", "Do not run large source builds; inspect APFS and caches without deleting system volumes")
    elif free_gib is None:
        finding("disk_unknown", "MEDIUM", "Disk free space not measurable", "Read back APFS shared-container free space")
    if load_1 is not None and cpu_count and cpu_count > 0 and load_1 > cpu_count * 8:
        finding("load_pressure", "HIGH", "One-minute load exceeds 8x logical CPU count", "Identify active compile/agent jobs and bound concurrency without killing mission state")

    high = any(x["severity"] == "HIGH" for x in findings)
    return {
        "schema": "glaciereq.omp.readonly_preflight.v1",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_execution": "READ_ONLY_AUDIT",
        "status": "NEEDS_ATTENTION" if high else "BASELINE_ONLY",
        "signals": {
            "omp_executable_present": executable.is_file() and os.access(executable, os.X_OK),
            "omp_config_present": config is not None,
            "local_config_git_present": has_git,
            "available_disk_gib": None if free_gib is None else round(free_gib, 2),
            "one_minute_load": None if load_1 is None else round(load_1, 2),
            "logical_cpus": cpu_count,
        },
        "findings": findings,
        "acceptance": {name: "UNVERIFIED" for name in ACCEPTANCE_GATES},
        "acceptance_note": "Host preflight does not execute, authorize, or verify a mission or provider effect.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home(), help="Target HOME for safe local metadata checks")
    parser.add_argument("--output", type=Path, help="Optional new JSON receipt path (never overwrite)")
    args = parser.parse_args()
    home = args.home.expanduser()
    executable = shutil.which("omp")
    binary = Path(executable) if executable else home / ".local" / "bin" / "omp"
    try:
        fs = os.statvfs(str(home))
        free_gib = fs.f_bavail * fs.f_frsize / (1024**3)
    except OSError:
        free_gib = None
    try:
        load_1 = os.getloadavg()[0]
    except (OSError, AttributeError):
        load_1 = None
    payload = audit_omp(home=home, free_gib=free_gib, load_1=load_1, cpu_count=os.cpu_count(), executable=binary)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as out:
            out.write(rendered)
    print(rendered, end="")
    return 0 if payload["status"] == "BASELINE_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
