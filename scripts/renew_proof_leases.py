#!/usr/bin/env python3
"""Atomically renew Deep Progress Forge provider + host proof leases."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import tempfile
import fcntl
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence/deep-progress-forge"
LATEST = EVIDENCE / "LATEST.json"
PROVIDER = EVIDENCE / "provider-readback-manifest-v2.json"
HOST = EVIDENCE / "host-skills-lifecycle-latest.json"
RENEWAL = EVIDENCE / "proof-renewal-latest.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


provider_mod = load_module("refresh_provider", ROOT / "scripts/refresh_provider_readback_manifest.py")
host_mod = load_module("refresh_host", ROOT / "scripts/refresh_host_runtime_proof.py")
validator = load_module("validate_latest", ROOT / "scripts/validate_deep_progress_latest.py")


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))



def git(*args: str, check: bool = True) -> str:
    cp = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
    if check and cp.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {cp.stderr.strip()}")
    return cp.stdout.rstrip("\n")


def mission_tuple(pointer: dict) -> dict:
    return {
        "run_sequence": pointer["run_sequence"],
        "current_run": pointer.get("current_run"),
        "current_run_commit": pointer.get("current_run_commit"),
        "provider_state_schema_version": pointer.get("provider_state_schema_version"),
        "frontier": pointer["next_executable_frontier"],
    }


def recovery_tuple(pointer: dict) -> dict:
    return {
        **mission_tuple(pointer),
        "provider_digest": pointer["provider_readback_manifest"]["proof_digest_sha256"],
        "host_digest": pointer["host_runtime_proof"]["receipt_digest_sha256"],
    }


def capture_repository_snapshot(pointer: dict, *, fetch: bool = True) -> dict:
    if fetch:
        git("fetch", "--quiet", "origin", "main")
    return {
        "local_head": git("rev-parse", "HEAD"),
        "origin_main": git("rev-parse", "origin/main"),
        "mission_tuple": mission_tuple(pointer),
        "mission_tuple_sha256": digest(mission_tuple(pointer)),
        "recovery_tuple": recovery_tuple(pointer),
        "recovery_tuple_sha256": digest(recovery_tuple(pointer)),
    }


def assert_snapshot_unchanged(snapshot: dict) -> None:
    git("fetch", "--quiet", "origin", "main")
    failures = []
    if git("rev-parse", "HEAD") != snapshot["local_head"]:
        failures.append("local HEAD moved")
    if git("rev-parse", "origin/main") != snapshot["origin_main"]:
        failures.append("origin/main moved")
    current = read_json(LATEST)
    if digest(recovery_tuple(current)) != snapshot["recovery_tuple_sha256"]:
        failures.append("bound recovery tuple moved")
    if failures:
        raise RuntimeError("optimistic concurrency conflict: " + "; ".join(failures))


def assert_precommit_snapshot_unchanged(snapshot: dict, candidate: dict) -> None:
    git("fetch", "--quiet", "origin", "main")
    failures = []
    if git("rev-parse", "HEAD") != snapshot["local_head"]:
        failures.append("local HEAD moved")
    if git("rev-parse", "origin/main") != snapshot["origin_main"]:
        failures.append("origin/main moved")
    if digest(mission_tuple(candidate)) != snapshot["mission_tuple_sha256"]:
        failures.append("mission tuple moved")
    if failures:
        raise RuntimeError("optimistic concurrency conflict: " + "; ".join(failures))


@contextmanager
def renewal_lock():
    lock_path = ROOT / ".git" / "deep-progress-proof-renewal.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w") as fh:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("another proof renewal holds the repository lock") from exc
        fh.write(str(os.getpid())); fh.flush()
        try:
            yield
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def _require_clean_except(paths: set[Path] | None = None) -> None:
    paths = {p.resolve() for p in (paths or set())}
    unexpected = []
    for line in git("status", "--porcelain").splitlines():
        rel = line[3:]
        path = (ROOT / rel).resolve()
        if path not in paths:
            unexpected.append(rel)
    if unexpected:
        raise RuntimeError(f"refusing renewal with unrelated worktree changes: {unexpected}")


def _blob_sha(path: Path) -> str:
    return git("hash-object", str(path.relative_to(ROOT)))


def commit_and_publish(candidate: dict, receipt: dict, snapshot: dict, *, push: bool = True) -> dict:
    """Create payload + finalization commits and CAS-publish them as one ref update."""
    assert_precommit_snapshot_unchanged(snapshot, candidate)
    allowed = {LATEST, PROVIDER, HOST, RENEWAL}
    _require_clean_except(allowed)

    # Payload commit: immutable renewed proof bytes, still based on the expected provider head.
    git("add", str(PROVIDER.relative_to(ROOT)), str(HOST.relative_to(ROOT)))
    git("commit", "-m", "chore: renew provider and host proof payload")
    payload_commit = git("rev-parse", "HEAD")
    payload_tree = git("rev-parse", "HEAD^{tree}")
    payload_blobs = {
        "provider": _blob_sha(PROVIDER),
        "host": _blob_sha(HOST),
    }

    candidate = json.loads(json.dumps(candidate))
    candidate.setdefault("verification_state", {})["latest_proof_renewal_payload_commit"] = payload_commit
    candidate["verification_state"]["latest_proof_renewal_payload_tree"] = payload_tree
    candidate["verification_state"]["latest_proof_renewal_origin_parent"] = snapshot["origin_main"]
    receipt = json.loads(json.dumps(receipt))
    receipt["git_finalization"] = {
        "origin_parent": snapshot["origin_main"],
        "payload_commit": payload_commit,
        "payload_tree": payload_tree,
        "payload_blob_shas": payload_blobs,
        "recovery_tuple_before_sha256": snapshot["recovery_tuple_sha256"],
    }
    receipt.pop("receipt_digest_sha256", None)
    receipt["receipt_digest_sha256"] = digest(receipt)
    candidate["verification_state"]["latest_proof_renewal_receipt_digest"] = receipt["receipt_digest_sha256"]
    _atomic_json(RENEWAL, receipt)
    _atomic_json(LATEST, candidate)

    git("add", str(RENEWAL.relative_to(ROOT)), str(LATEST.relative_to(ROOT)))
    git("commit", "-m", "chore: finalize proof renewal transaction")
    final_commit = git("rev-parse", "HEAD")
    final_tree = git("rev-parse", "HEAD^{tree}")

    # Re-read the remote immediately before the single ref update.
    git("fetch", "--quiet", "origin", "main")
    if git("rev-parse", "origin/main") != snapshot["origin_main"]:
        raise RuntimeError("optimistic concurrency conflict: origin/main moved before publish")
    if push:
        git("push", "--quiet", f"--force-with-lease=refs/heads/main:{snapshot['origin_main']}", "origin", f"{final_commit}:refs/heads/main")
    return {
        "origin_parent": snapshot["origin_main"],
        "payload_commit": payload_commit,
        "payload_tree": payload_tree,
        "final_commit": final_commit,
        "final_tree": final_tree,
        "receipt_digest_sha256": receipt["receipt_digest_sha256"],
        "payload_blob_shas": payload_blobs,
        "published": push,
    }

def lease_status(pointer: dict, now: datetime | None = None, renew_within_hours: float = 2.0) -> dict:
    now = now or datetime.now(timezone.utc)
    rows = {}
    for lane, binding_key in (("provider", "provider_readback_manifest"), ("host", "host_runtime_proof")):
        binding = pointer[binding_key]
        if lane == "provider":
            due = parse_utc(read_json(ROOT / binding["path"])["revalidate_after"])
        else:
            due = parse_utc(binding["revalidate_after"])
        remaining = (due - now).total_seconds() / 3600
        rows[lane] = {
            "revalidate_after": due.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
            "hours_remaining": round(remaining, 3),
            "expired": remaining < 0,
            "renew_recommended": remaining <= renew_within_hours,
        }
    rows["renewal_required"] = any(v["renew_recommended"] for v in rows.values() if isinstance(v, dict))
    return rows


def _atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(value, fh, indent=2)
            fh.write("\n")
            fh.flush(); os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def renew(pointer: dict, skills_bin: Path, provider_ttl: int = 24, host_ttl: int = 8,
          now: datetime | None = None, provider_builder=None, host_builder=None,
          validate=None) -> tuple[dict, dict, dict, dict]:
    now = now or datetime.now(timezone.utc)
    provider_builder = provider_builder or (lambda p: provider_mod.build(p, now, provider_ttl))
    host_builder = host_builder or (lambda: host_mod.build(skills_bin, host_ttl))
    validate = validate or (lambda candidate: validator.validate_pointer(candidate, ROOT, now=now))

    before = {
        "provider_digest": pointer["provider_readback_manifest"]["proof_digest_sha256"],
        "host_digest": pointer["host_runtime_proof"]["receipt_digest_sha256"],
        "run_sequence": pointer["run_sequence"],
        "frontier": pointer["next_executable_frontier"],
    }
    new_provider = provider_builder(pointer)
    new_host = host_builder()
    candidate = json.loads(json.dumps(pointer))
    candidate["provider_readback_manifest"] = {
        "path": str(PROVIDER.relative_to(ROOT)),
        "proof_digest_sha256": new_provider["proof_digest_sha256"],
    }
    candidate["host_runtime_proof"] = {
        "path": str(HOST.relative_to(ROOT)),
        "receipt_digest_sha256": new_host["receipt_digest_sha256"],
        "observed_at": new_host["observed_at"],
        "revalidate_after": new_host["revalidate_after"],
        "executable_sha256": new_host["skills_bin_sha256"],
    }
    candidate["verification_state"].update({
        "provider_readback_manifest_digest": new_provider["proof_digest_sha256"],
        "provider_proof_observed_at": new_provider["observed_at"],
        "provider_proof_revalidate_after": new_provider["revalidate_after"],
        "operator_host_runtime_receipt_digest": new_host["receipt_digest_sha256"],
        "host_proof_observed_at": new_host["observed_at"],
        "host_proof_revalidate_after": new_host["revalidate_after"],
        "host_executable_sha256": new_host["skills_bin_sha256"],
    })
    after = {
        "provider_digest": new_provider["proof_digest_sha256"],
        "host_digest": new_host["receipt_digest_sha256"],
        "run_sequence": candidate["run_sequence"],
        "frontier": candidate["next_executable_frontier"],
    }
    if before["run_sequence"] != after["run_sequence"] or before["frontier"] != after["frontier"]:
        raise RuntimeError("renewal attempted to mutate mission sequence/frontier")
    return candidate, new_provider, new_host, {"before": before, "after": after}


def commit_transaction(candidate: dict, new_provider: dict, new_host: dict, delta: dict, *, validate=None) -> dict:
    original = {p: p.read_bytes() if p.exists() else None for p in (LATEST, PROVIDER, HOST, RENEWAL)}
    try:
        _atomic_json(PROVIDER, new_provider)
        _atomic_json(HOST, new_host)
        validate_fn = validate or (lambda c: validator.validate_pointer(c, ROOT))
        validation = validate_fn(candidate)
        receipt = {
            "schema_version": 1,
            "transaction": "atomic_proof_renewal",
            "renewed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            **delta,
            "validation": validation,
            "invariants": {
                "run_sequence_unchanged": delta["before"]["run_sequence"] == delta["after"]["run_sequence"],
                "frontier_unchanged": delta["before"]["frontier"] == delta["after"]["frontier"],
                "both_lanes_changed": delta["before"]["provider_digest"] != delta["after"]["provider_digest"] and delta["before"]["host_digest"] != delta["after"]["host_digest"],
            },
        }
        receipt["receipt_digest_sha256"] = digest(receipt)
        if not all(receipt["invariants"].values()):
            raise RuntimeError(f"renewal invariants failed: {receipt['invariants']}")
        _atomic_json(RENEWAL, receipt)
        _atomic_json(LATEST, candidate)
        return receipt
    except Exception:
        for path, data in original.items():
            if data is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(data)
        raise


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--check", action="store_true", help="exit nonzero when either lease is within the renewal window")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--renew-within-hours", type=float, default=2.0)
    ap.add_argument("--skills-bin", type=Path, default=Path.home()/"bin/skills")
    ap.add_argument("--no-push", action="store_true", help="finalize locally without publishing origin/main")
    args = ap.parse_args()
    pointer = read_json(LATEST)
    status = lease_status(pointer, renew_within_hours=args.renew_within_hours)
    if args.status:
        print(json.dumps(status, indent=2)); return 0
    if args.check:
        print(json.dumps(status, indent=2)); return 3 if status["renewal_required"] else 0
    if not args.force and not status["renewal_required"]:
        print(json.dumps({"status":"SKIPPED_FRESH","leases":status}, indent=2)); return 0
    with renewal_lock():
        _require_clean_except()
        snapshot = capture_repository_snapshot(pointer)
        if snapshot["local_head"] != snapshot["origin_main"]:
            raise RuntimeError("renewal requires local HEAD to equal origin/main")
        candidate, p, h, delta = renew(pointer, args.skills_bin)
        assert_snapshot_unchanged(snapshot)
        receipt = commit_transaction(candidate, p, h, delta)
        finalization = commit_and_publish(candidate, receipt, snapshot, push=not args.no_push)
    print(json.dumps({"status":"RENEWED","receipt":receipt,"git_finalization":finalization,"leases":lease_status(candidate)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
