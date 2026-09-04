#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class PipelineError(ValueError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(payload).hexdigest()


def load_pipeline(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        raise PipelineError(f"pipeline not found: {p}")
    if p.suffix.lower() != ".json":
        raise PipelineError("pipeline definition must be JSON")
    spec = json.loads(p.read_text(encoding="utf-8"))
    validate_pipeline(spec)
    return spec


def validate_pipeline(spec: dict[str, Any]) -> None:
    if spec.get("schema_version") != 1:
        raise PipelineError("schema_version must be 1")
    if not isinstance(spec.get("id"), str) or not spec["id"].strip():
        raise PipelineError("pipeline id required")
    stages = spec.get("stages")
    if not isinstance(stages, list) or not stages:
        raise PipelineError("stages must be a non-empty array")
    ids: list[str] = []
    for stage in stages:
        if not isinstance(stage, dict) or not isinstance(stage.get("id"), str):
            raise PipelineError("each stage requires string id")
        sid = stage["id"]
        if sid in ids:
            raise PipelineError(f"duplicate stage id: {sid}")
        ids.append(sid)
        command = stage.get("command")
        if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
            raise PipelineError(f"stage {sid} command must be a non-empty string array")
        needs = stage.get("needs", [])
        if not isinstance(needs, list) or not all(isinstance(x, str) for x in needs):
            raise PipelineError(f"stage {sid} needs must be a string array")
    known = set(ids)
    for stage in stages:
        for dep in stage.get("needs", []):
            if dep not in known:
                raise PipelineError(f"stage {stage['id']} depends on unknown stage {dep}")
    topological_layers(spec)


def topological_layers(spec: dict[str, Any]) -> list[list[str]]:
    stages = {s["id"]: s for s in spec["stages"]}
    indegree = {sid: 0 for sid in stages}
    children = {sid: [] for sid in stages}
    for sid, stage in stages.items():
        for dep in stage.get("needs", []):
            indegree[sid] += 1
            children[dep].append(sid)
    ready = sorted([sid for sid, degree in indegree.items() if degree == 0])
    layers: list[list[str]] = []
    visited = 0
    while ready:
        layer = ready
        layers.append(layer)
        visited += len(layer)
        nxt: list[str] = []
        for sid in layer:
            for child in sorted(children[sid]):
                indegree[child] -= 1
                if indegree[child] == 0:
                    nxt.append(child)
        ready = sorted(nxt)
    if visited != len(stages):
        cyclic = sorted([sid for sid, degree in indegree.items() if degree > 0])
        raise PipelineError(f"pipeline contains a cycle involving: {', '.join(cyclic)}")
    return layers


def _contained(root: Path, rel: str | Path) -> Path:
    root = root.resolve()
    candidate = (root / rel).resolve() if not Path(rel).is_absolute() else Path(rel).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise PipelineError(f"path escapes workspace: {rel}") from exc
    return candidate


def hash_artifact(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise PipelineError(f"artifact missing: {path}")
    digest = hashlib.sha256()
    size = 0
    if path.is_dir():
        for f in sorted(p for p in path.rglob("*") if p.is_file()):
            rel = f.relative_to(path).as_posix().encode()
            data = f.read_bytes()
            digest.update(len(rel).to_bytes(8, "big")); digest.update(rel)
            digest.update(len(data).to_bytes(8, "big")); digest.update(data)
            size += len(data)
        kind = "directory"
    else:
        data = path.read_bytes(); digest.update(data); size = len(data); kind = "file"
    return {"path": str(path), "kind": kind, "bytes": size, "sha256": digest.hexdigest()}


def _checkpoint_path(spec: dict[str, Any], workspace: Path, state_dir: str | Path | None) -> Path:
    base = _contained(workspace, state_dir or ".pipeline-state")
    return base / spec["id"] / "checkpoint.json"


def load_checkpoint(spec: dict[str, Any], workspace: Path, state_dir: str | Path | None) -> dict[str, Any]:
    path = _checkpoint_path(spec, workspace, state_dir)
    expected = canonical_sha256(spec)
    if not path.is_file():
        return {"pipeline_id": spec["id"], "spec_sha256": expected, "completed": {}}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"pipeline_id": spec["id"], "spec_sha256": expected, "completed": {}}
    if state.get("spec_sha256") != expected:
        return {"pipeline_id": spec["id"], "spec_sha256": expected, "completed": {}}
    state.setdefault("completed", {})
    return state


def write_checkpoint(spec: dict[str, Any], workspace: Path, state_dir: str | Path | None, state: dict[str, Any]) -> None:
    path = _checkpoint_path(spec, workspace, state_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _artifact_snapshots(stage: dict[str, Any], workspace: Path, field: str) -> dict[str, Any]:
    return {rel: hash_artifact(_contained(workspace, rel)) for rel in stage.get(field, [])}


def _resume_valid(stage: dict[str, Any], record: dict[str, Any], workspace: Path) -> bool:
    if not stage.get("resume_safe", False) or record.get("status") != "succeeded":
        return False
    try:
        return record.get("inputs", {}) == _artifact_snapshots(stage, workspace, "consumes") and record.get("outputs", {}) == _artifact_snapshots(stage, workspace, "produces")
    except PipelineError:
        return False


def _render(token: str, workspace: Path) -> str:
    return token.replace("{python}", sys.executable).replace("{workspace}", str(workspace))


def run_stage(stage: dict[str, Any], workspace: Path) -> dict[str, Any]:
    started = utc_now(); t0 = time.monotonic()
    command = [_render(x, workspace) for x in stage["command"]]
    cwd = _contained(workspace, stage.get("cwd", "."))
    env = os.environ.copy(); env.update({str(k): _render(str(v), workspace) for k, v in stage.get("env", {}).items()})
    inputs = _artifact_snapshots(stage, workspace, "consumes")
    attempts = []; rc = 1; stdout = ""; stderr = ""
    retries = int(stage.get("retries", 0)); timeout = float(stage.get("timeout_seconds", 300))
    for n in range(1, retries + 2):
        try:
            p = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout, check=False)
            rc, stdout, stderr = p.returncode, p.stdout[-20000:], p.stderr[-20000:]
            attempts.append({"attempt": n, "returncode": rc})
            if rc == 0: break
        except subprocess.TimeoutExpired as exc:
            rc = 124; stdout = (exc.stdout or "")[-20000:]; stderr = ((exc.stderr or "") + f"\ntimeout after {timeout}s")[-20000:]
            attempts.append({"attempt": n, "returncode": rc, "timeout": True})
        if n <= retries: time.sleep(float(stage.get("retry_delay_seconds", 0.25)) * n)
    outputs = {}; status = "succeeded" if rc == 0 else "failed"
    if status == "succeeded":
        try: outputs = _artifact_snapshots(stage, workspace, "produces")
        except PipelineError as exc:
            status = "failed"; rc = 65; stderr = (stderr + "\n" + str(exc)).strip()
    return {"id": stage["id"], "status": status, "started_at": started, "finished_at": utc_now(), "duration_ms": round((time.monotonic()-t0)*1000,3), "command": command, "returncode": rc, "attempts": attempts, "stdout": stdout, "stderr": stderr, "inputs": inputs, "outputs": outputs}


def execute_pipeline(spec: dict[str, Any], workspace: str | Path = ".", *, state_dir: str | Path | None = None, resume: bool = False, max_parallel: int | None = None) -> dict[str, Any]:
    validate_pipeline(spec)
    workspace = Path(workspace).resolve()
    if not workspace.is_dir(): raise PipelineError(f"workspace does not exist: {workspace}")
    layers = topological_layers(spec); by_id = {s["id"]: s for s in spec["stages"]}
    state = load_checkpoint(spec, workspace, state_dir) if resume else {"pipeline_id": spec["id"], "spec_sha256": canonical_sha256(spec), "completed": {}}
    results = []; started = utc_now(); failed = False
    for layer in layers:
        runnable = []
        for sid in layer:
            stage = by_id[sid]; prior = state["completed"].get(sid)
            if resume and prior and _resume_valid(stage, prior, workspace):
                results.append({**deepcopy(prior), "status": "resumed"}); continue
            runnable.append(stage)
        if not runnable: continue
        workers = min(max_parallel or int(spec.get("max_parallel", 1)), len(runnable), 32)
        with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
            layer_results = [f.result() for f in as_completed([pool.submit(run_stage, s, workspace) for s in runnable])]
        layer_results.sort(key=lambda x: x["id"]); results.extend(layer_results)
        for r in layer_results:
            if r["status"] == "succeeded" and by_id[r["id"]].get("resume_safe", False):
                state["completed"][r["id"]] = deepcopy(r)
        write_checkpoint(spec, workspace, state_dir, state)
        if any(r["status"] == "failed" for r in layer_results): failed = True; break
    status = "FAILED" if failed else "COMPLETE"
    manifest = {"schema_version": 1, "pipeline_id": spec["id"], "spec_sha256": canonical_sha256(spec), "status": status, "started_at": started, "finished_at": utc_now(), "layers": layers, "stage_results": results, "summary": {"stages": len(spec["stages"]), "succeeded": sum(r["status"] in {"succeeded","resumed"} for r in results), "failed": sum(r["status"] == "failed" for r in results), "resumed": sum(r["status"] == "resumed" for r in results)}}
    manifest_path = _contained(workspace, spec.get("manifest", f"missions/{spec['id']}/pipeline-execution-manifest.json"))
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest["manifest"] = str(manifest_path)
    return manifest
