#!/usr/bin/env python3
"""Fail closed when the Deep Progress Forge continuation pointer drifts."""
from __future__ import annotations

import json
import re
import subprocess
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
POINTER = ROOT / "evidence" / "deep-progress-forge" / "LATEST.json"
RENEWAL = ROOT / "evidence" / "deep-progress-forge" / "proof-renewal-latest.json"
ABANDONED = ROOT / "evidence" / "deep-progress-forge" / "proof-renewal-abandoned.json"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
CURRENT_REPO = "GlacierEQ/mega-skills"
PROVIDER_STATE_SCHEMA_VERSION = 4
LEGACY_PROVIDER_STATE_SCHEMA_VERSION = 3
PROVIDER_TYPES = {"repo_commit", "cross_repo_commit", "blob"}
PROVIDER_MANIFEST_SCHEMA_VERSION = 2
LEGACY_PROVIDER_MANIFEST_SCHEMA_VERSION = 1
REQUIRED_LEDGER = {
    "stream", "run_sequence", "verbatim_sources", "failure_pattern_attacked",
    "durable_sources_changed", "concrete_outputs", "verification",
    "objective_state_delta", "unresolved", "next_executable_frontier",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_repository_history(root: Path = ROOT) -> dict:
    """Hydrate shallow Git history before making historical continuity claims."""
    shallow = subprocess.run(
        ["git", "rev-parse", "--is-shallow-repository"],
        cwd=root, capture_output=True, text=True,
    )
    if shallow.returncode != 0:
        raise ValueError("unable to determine repository history depth")
    was_shallow = shallow.stdout.strip() == "true"
    if was_shallow:
        hydrated = subprocess.run(
            ["git", "fetch", "--quiet", "--unshallow", "origin", "main"],
            cwd=root, capture_output=True, text=True,
        )
        if hydrated.returncode != 0:
            raise ValueError(
                "source-bearing Git history is shallow and hydration failed: "
                + hydrated.stderr.strip()
            )
    return {"was_shallow": was_shallow, "hydrated": was_shallow}


def git_last_change(path: Path) -> str:
    rel = path.relative_to(ROOT)
    return subprocess.check_output(
        ["git", "log", "-1", "--format=%H", "--", str(rel)],
        cwd=ROOT, text=True,
    ).strip()


def git_commit_reachable(sha: str, root: Path = ROOT) -> bool:
    exists = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=root, capture_output=True, text=True,
    )
    if exists.returncode != 0:
        return False
    reachable = subprocess.run(
        ["git", "merge-base", "--is-ancestor", sha, "HEAD"],
        cwd=root, capture_output=True, text=True,
    )
    return reachable.returncode == 0



def git_object_type(sha: str, root: Path = ROOT) -> str | None:
    result = subprocess.run(
        ["git", "cat-file", "-t", sha], cwd=root, capture_output=True, text=True
    )
    return result.stdout.strip() if result.returncode == 0 else None

def git_commit_parent(sha: str, root: Path = ROOT) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", f"{sha}^"], cwd=root, capture_output=True, text=True
    )
    return result.stdout.strip() if result.returncode == 0 else None


def git_commit_tree(sha: str, root: Path = ROOT) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", f"{sha}^{{tree}}"], cwd=root, capture_output=True, text=True
    )
    return result.stdout.strip() if result.returncode == 0 else None


def git_blob_at(sha: str, rel: str, root: Path = ROOT) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", f"{sha}:{rel}"], cwd=root, capture_output=True, text=True
    )
    return result.stdout.strip() if result.returncode == 0 else None


def git_json_at(sha: str, rel: str, root: Path = ROOT) -> dict | None:
    result = subprocess.run(
        ["git", "show", f"{sha}:{rel}"], cwd=root, capture_output=True, text=True
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def canonical_digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()




def parse_utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("freshness timestamps must be UTC RFC3339 values ending in Z")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(f"invalid UTC timestamp: {value}") from exc


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def manifest_digest_payload(manifest: dict) -> dict:
    return {
        "schema_version": manifest.get("schema_version"),
        "source": manifest.get("source"),
        "observed_at": manifest.get("observed_at"),
        "revalidate_after": manifest.get("revalidate_after"),
        "proofs": manifest.get("proofs"),
    }


def receipt_digest(receipt: dict) -> str:
    body = dict(receipt)
    body.pop("receipt_digest_sha256", None)
    return canonical_digest(body)

def load_provider_manifest(pointer: dict, root: Path = ROOT, *, require_freshness: bool = False, now: datetime | None = None) -> dict:
    binding = pointer.get("provider_readback_manifest")
    if not isinstance(binding, dict):
        raise ValueError("provider_readback_manifest is required for provider-state")
    rel = binding.get("path")
    digest = binding.get("proof_digest_sha256")
    if not isinstance(rel, str) or not rel.startswith("evidence/deep-progress-forge/"):
        raise ValueError("provider readback manifest must stay inside forge evidence directory")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("provider readback manifest binding requires proof_digest_sha256")
    path = root / rel
    if not path.is_file():
        raise ValueError(f"provider readback manifest does not exist: {rel}")
    manifest = load_json(path)
    schema_version = manifest.get("schema_version")
    allowed = {PROVIDER_MANIFEST_SCHEMA_VERSION} if require_freshness else {LEGACY_PROVIDER_MANIFEST_SCHEMA_VERSION, PROVIDER_MANIFEST_SCHEMA_VERSION}
    if schema_version not in allowed:
        raise ValueError("unsupported provider readback manifest schema")
    proofs = manifest.get("proofs")
    if not isinstance(proofs, list) or not proofs:
        raise ValueError("provider readback manifest proofs must be a non-empty list")
    if schema_version == LEGACY_PROVIDER_MANIFEST_SCHEMA_VERSION:
        actual = canonical_digest(proofs)
    else:
        observed = parse_utc(manifest.get("observed_at"))
        due = parse_utc(manifest.get("revalidate_after"))
        if due <= observed:
            raise ValueError("provider proof revalidate_after must be later than observed_at")
        if require_freshness and (now or utc_now()) > due:
            raise ValueError("provider readback proof is stale and requires revalidation")
        actual = canonical_digest(manifest_digest_payload(manifest))
    if manifest.get("proof_digest_sha256") != actual or digest != actual:
        raise ValueError("provider readback manifest digest mismatch")
    return manifest


def validate_host_runtime_proof(pointer: dict, root: Path = ROOT, *, now: datetime | None = None) -> dict:
    binding = pointer.get("host_runtime_proof")
    if not isinstance(binding, dict):
        raise ValueError("host_runtime_proof is required for provider-state v4")
    rel = binding.get("path")
    if not isinstance(rel, str) or not rel.startswith("evidence/deep-progress-forge/"):
        raise ValueError("host runtime proof must stay inside forge evidence directory")
    path = root / rel
    if not path.is_file():
        raise ValueError(f"host runtime proof does not exist: {rel}")
    receipt = load_json(path)
    expected_digest = binding.get("receipt_digest_sha256")
    if receipt_digest(receipt) != expected_digest or receipt.get("receipt_digest_sha256") != expected_digest:
        raise ValueError("host runtime receipt digest mismatch")
    observed = parse_utc(binding.get("observed_at"))
    due = parse_utc(binding.get("revalidate_after"))
    if due <= observed:
        raise ValueError("host runtime revalidate_after must be later than observed_at")
    if (now or utc_now()) > due:
        raise ValueError("host runtime proof is stale and requires revalidation")
    executable_sha = binding.get("executable_sha256")
    if not isinstance(executable_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", executable_sha):
        raise ValueError("host runtime proof requires executable_sha256")
    if receipt.get("skills_bin_sha256") != executable_sha:
        raise ValueError("host runtime executable fingerprint disagrees with receipt")
    return {"status": "PASS", "observed_at": binding["observed_at"], "revalidate_after": binding["revalidate_after"], "executable_sha256": executable_sha}

def validate_provider_state(
    pointer: dict,
    root: Path = ROOT,
    commit_reachable: Callable[[str, Path], bool] | None = None,
    object_type_lookup: Callable[[str, Path], str | None] | None = None,
    now: datetime | None = None,
) -> dict:
    version = pointer.get("provider_state_schema_version")
    if version is None:
        return {"status": "LEGACY", "checked": 0}
    if version not in {LEGACY_PROVIDER_STATE_SCHEMA_VERSION, PROVIDER_STATE_SCHEMA_VERSION}:
        raise ValueError(f"provider_state_schema_version must be {LEGACY_PROVIDER_STATE_SCHEMA_VERSION} or {PROVIDER_STATE_SCHEMA_VERSION}")
    state = pointer.get("verified_provider_state")
    if not isinstance(state, dict) or not state:
        raise ValueError("verified_provider_state must be a non-empty object")
    lookup = commit_reachable or git_commit_reachable
    object_lookup = object_type_lookup or git_object_type
    require_freshness = version == PROVIDER_STATE_SCHEMA_VERSION
    manifest = load_provider_manifest(pointer, root, require_freshness=require_freshness, now=now)
    proof_index = {}
    for proof in manifest["proofs"]:
        if not isinstance(proof, dict):
            raise ValueError("provider readback manifest proof must be an object")
        key = (proof.get("type"), proof.get("repo"), proof.get("sha"))
        proof_index[key] = proof
    checked = 0
    same_repo_commits = 0
    same_repo_blobs = 0
    cross_repo_proofs = 0
    for name, entry in state.items():
        if not isinstance(entry, dict):
            raise ValueError(f"provider state {name} must be a typed object")
        kind = entry.get("type")
        repo = entry.get("repo")
        sha = entry.get("sha")
        if kind not in PROVIDER_TYPES:
            raise ValueError(f"provider state {name} has unsupported type={kind!r}")
        if not isinstance(repo, str) or "/" not in repo:
            raise ValueError(f"provider state {name} requires owner/repo")
        if not isinstance(sha, str) or not HEX40.fullmatch(sha):
            raise ValueError(f"provider state {name} requires a full 40-hex SHA")
        if kind == "repo_commit":
            if repo != CURRENT_REPO:
                raise ValueError(
                    f"provider state {name} repo_commit must target {CURRENT_REPO}; "
                    "use cross_repo_commit for external repositories"
                )
            if not lookup(sha, root):
                raise ValueError(
                    f"provider state {name} commit is not reachable from repository HEAD: {sha}"
                )
            same_repo_commits += 1
        elif kind == "cross_repo_commit":
            if repo == CURRENT_REPO:
                raise ValueError(
                    f"provider state {name} cannot classify a same-repository commit as cross_repo_commit"
                )
            proof = proof_index.get((kind, repo, sha))
            if not proof or not proof.get("provider_url"):
                raise ValueError(
                    f"provider state {name} cross-repository commit lacks matching provider readback proof"
                )
            if require_freshness:
                provider_object = proof.get("provider_object")
                if not isinstance(provider_object, dict) or provider_object.get("kind") != "commit":
                    raise ValueError(f"provider state {name} lacks immutable commit metadata")
                tree_sha = provider_object.get("tree_sha")
                parents = provider_object.get("parent_shas")
                if not isinstance(tree_sha, str) or not HEX40.fullmatch(tree_sha):
                    raise ValueError(f"provider state {name} requires provider tree_sha")
                if not isinstance(parents, list) or not all(isinstance(x, str) and HEX40.fullmatch(x) for x in parents):
                    raise ValueError(f"provider state {name} requires provider parent_shas")
            cross_repo_proofs += 1
        elif kind == "blob":
            if repo == CURRENT_REPO:
                if object_lookup(sha, root) != "blob":
                    raise ValueError(
                        f"provider state {name} is not a same-repository blob object: {sha}"
                    )
                same_repo_blobs += 1
            else:
                proof = proof_index.get((kind, repo, sha))
                if not proof or not proof.get("provider_url"):
                    raise ValueError(
                        f"provider state {name} external blob lacks matching provider readback proof"
                    )
        checked += 1
    if same_repo_commits == 0:
        raise ValueError("provider state v3 must contain at least one reachable same-repository commit")
    return {
        "status": "PASS",
        "checked": checked,
        "same_repo_commits": same_repo_commits,
        "same_repo_blobs": same_repo_blobs,
        "cross_repo_proofs": cross_repo_proofs,
        "manifest_digest": manifest["proof_digest_sha256"],
    }


def validate_no_abandoned_renewal(root: Path = ROOT) -> dict:
    """Fail closed while a rejected leased publish still has unresolved local state."""
    path = root / "evidence/deep-progress-forge/proof-renewal-abandoned.json"
    if not path.is_file():
        return {"status": "NONE"}
    record = load_json(path)
    if record.get("status") != "ABANDONED_LOCAL_TRANSACTION":
        raise ValueError("malformed abandoned proof-renewal marker")
    origin = record.get("origin_parent")
    final_commit = record.get("final_commit")
    if not isinstance(origin, str) or not HEX40.fullmatch(origin):
        raise ValueError("abandoned proof-renewal marker lacks valid origin_parent")
    if not isinstance(final_commit, str) or not HEX40.fullmatch(final_commit):
        raise ValueError("abandoned proof-renewal marker lacks valid final_commit")
    raise ValueError(
        "unresolved abandoned proof-renewal transaction; "
        "recover explicitly with `python3 scripts/renew_proof_leases.py --recover-abandoned` "
        f"before continuity can PASS (origin_parent={origin}, final_commit={final_commit})"
    )


def validate_latest_renewal_chain(pointer: dict, root: Path = ROOT) -> dict:
    """Traverse the latest proof-renewal receipt through immutable Git objects."""
    state = pointer.get("verification_state", {})
    payload = state.get("latest_proof_renewal_payload_commit")
    if not payload:
        return {"status": "LEGACY"}
    required = {
        "latest_proof_renewal_payload_commit": payload,
        "latest_proof_renewal_payload_tree": state.get("latest_proof_renewal_payload_tree"),
        "latest_proof_renewal_origin_parent": state.get("latest_proof_renewal_origin_parent"),
        "latest_proof_renewal_receipt_digest": state.get("latest_proof_renewal_receipt_digest"),
        "latest_proof_renewal_finalization_commit": state.get("latest_proof_renewal_finalization_commit"),
        "latest_proof_renewal_finalization_tree": state.get("latest_proof_renewal_finalization_tree"),
    }
    for name, value in required.items():
        if not isinstance(value, str) or (name.endswith(("commit", "tree", "parent")) and not HEX40.fullmatch(value)):
            raise ValueError(f"renewal chain requires {name}")
    receipt_path = root / "evidence/deep-progress-forge/proof-renewal-latest.json"
    if not receipt_path.is_file():
        raise ValueError("latest proof-renewal receipt is missing")
    receipt = load_json(receipt_path)
    expected_digest = required["latest_proof_renewal_receipt_digest"]
    if receipt_digest(receipt) != expected_digest or receipt.get("receipt_digest_sha256") != expected_digest:
        raise ValueError("latest proof-renewal receipt digest mismatch")
    gf = receipt.get("git_finalization")
    if not isinstance(gf, dict):
        raise ValueError("latest proof-renewal receipt lacks git_finalization")
    origin = required["latest_proof_renewal_origin_parent"]
    if gf.get("origin_parent") != origin or gf.get("payload_commit") != payload:
        raise ValueError("latest proof-renewal receipt disagrees on origin/payload commit")
    payload_tree = required["latest_proof_renewal_payload_tree"]
    if gf.get("payload_tree") != payload_tree or git_commit_tree(payload, root) != payload_tree:
        raise ValueError("proof-renewal payload tree mismatch")
    if git_commit_parent(payload, root) != origin:
        raise ValueError("proof-renewal payload parent does not equal recorded origin parent")
    blobs = gf.get("payload_blob_shas")
    if not isinstance(blobs, dict):
        raise ValueError("proof-renewal receipt lacks payload blob identities")
    expected_paths = {
        "provider": "evidence/deep-progress-forge/provider-readback-manifest-v2.json",
        "host": "evidence/deep-progress-forge/host-skills-lifecycle-latest.json",
    }
    for lane, rel in expected_paths.items():
        recorded = blobs.get(lane)
        if not isinstance(recorded, str) or not HEX40.fullmatch(recorded):
            raise ValueError(f"proof-renewal receipt lacks {lane} blob identity")
        if git_blob_at(payload, rel, root) != recorded:
            raise ValueError(f"proof-renewal {lane} blob identity mismatch")
    final_commit = required["latest_proof_renewal_finalization_commit"]
    final_tree = required["latest_proof_renewal_finalization_tree"]
    if git_commit_parent(final_commit, root) != payload:
        raise ValueError("proof-renewal finalization parent does not equal payload commit")
    if git_commit_tree(final_commit, root) != final_tree:
        raise ValueError("proof-renewal finalization tree mismatch")
    if not git_commit_reachable(final_commit, root):
        raise ValueError("proof-renewal finalization commit is not reachable from repository HEAD")
    committed_receipt = git_json_at(final_commit, "evidence/deep-progress-forge/proof-renewal-latest.json", root)
    if not isinstance(committed_receipt, dict) or committed_receipt.get("receipt_digest_sha256") != expected_digest:
        raise ValueError("finalization commit does not contain the bound renewal receipt")
    committed_pointer = git_json_at(final_commit, "evidence/deep-progress-forge/LATEST.json", root)
    if not isinstance(committed_pointer, dict):
        raise ValueError("finalization commit does not contain LATEST.json")
    committed_state = committed_pointer.get("verification_state", {})
    for key in ("latest_proof_renewal_payload_commit", "latest_proof_renewal_payload_tree", "latest_proof_renewal_origin_parent", "latest_proof_renewal_receipt_digest"):
        if committed_state.get(key) != state.get(key):
            raise ValueError(f"finalization commit disagrees with current binding for {key}")
    return {
        "status": "PASS",
        "origin_parent": origin,
        "payload_commit": payload,
        "payload_tree": payload_tree,
        "finalization_commit": final_commit,
        "finalization_tree": final_tree,
        "receipt_digest_sha256": expected_digest,
        "payload_blob_shas": blobs,
    }


def validate_pointer(
    pointer: dict,
    root: Path = ROOT,
    commit_lookup: Callable[[Path], str] | None = None,
    provider_commit_reachable: Callable[[str, Path], bool] | None = None,
    provider_object_type: Callable[[str, Path], str | None] | None = None,
    now: datetime | None = None,
) -> dict:
    if pointer.get("stream") != "deep-progress-forge":
        raise ValueError("unexpected continuation stream")
    sequence = pointer.get("run_sequence")
    if not isinstance(sequence, int) or sequence < 1:
        raise ValueError("run_sequence must be a positive integer")
    run_rel = pointer.get("current_run")
    if not isinstance(run_rel, str) or not run_rel.startswith("evidence/deep-progress-forge/"):
        raise ValueError("current_run must stay inside the forge evidence directory")
    if run_rel.endswith("LATEST.json"):
        raise ValueError("LATEST.json cannot point to itself")
    run_path = root / run_rel
    if not run_path.is_file():
        raise ValueError(f"current_run does not exist: {run_rel}")
    expected_commit = pointer.get("current_run_commit", "")
    if not HEX40.fullmatch(expected_commit):
        raise ValueError("current_run_commit must be a full Git SHA")
    lookup = commit_lookup or git_last_change
    actual_commit = lookup(run_path)
    if actual_commit != expected_commit:
        raise ValueError(
            f"current_run_commit drifted: pointer={expected_commit}, file={actual_commit}"
        )

    receipt = load_json(run_path)
    missing = REQUIRED_LEDGER - set(receipt)
    if missing:
        raise ValueError(f"current run ledger incomplete: missing={sorted(missing)}")
    if receipt["stream"] != pointer["stream"]:
        raise ValueError("current run stream disagrees with pointer")
    if receipt["run_sequence"] != sequence:
        raise ValueError("current run sequence disagrees with pointer")
    delta = receipt.get("objective_state_delta")
    if not isinstance(delta, dict) or delta.get("changed") is not True:
        raise ValueError("current run must prove objective_state_delta.changed=true")
    if not delta.get("before") or not delta.get("after"):
        raise ValueError("objective-state delta requires explicit before/after state")
    if receipt["next_executable_frontier"] != pointer.get("next_executable_frontier"):
        raise ValueError("pointer frontier disagrees with current run receipt")
    if not receipt["verbatim_sources"]:
        raise ValueError("current run must preserve verbatim source excerpts")
    if not receipt["durable_sources_changed"] or not receipt["concrete_outputs"]:
        raise ValueError("current run must contain durable mutation and concrete outputs")
    provider_result = validate_provider_state(
        pointer, root, provider_commit_reachable, provider_object_type, now
    )
    host_result = validate_host_runtime_proof(pointer, root, now=now) if pointer.get("provider_state_schema_version") == PROVIDER_STATE_SCHEMA_VERSION else {"status": "LEGACY"}
    abandoned_result = validate_no_abandoned_renewal(root)
    renewal_result = validate_latest_renewal_chain(pointer, root)
    return {
        "status": "PASS",
        "run_sequence": sequence,
        "current_run": run_rel,
        "current_run_commit": actual_commit,
        "provider_state": provider_result,
        "host_runtime_proof": host_result,
        "abandoned_renewal": abandoned_result,
        "proof_renewal_chain": renewal_result,
        "next_executable_frontier": receipt["next_executable_frontier"],
    }


def main() -> int:
    history = ensure_repository_history(ROOT)
    result = validate_pointer(load_json(POINTER))
    result["repository_history"] = history
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
