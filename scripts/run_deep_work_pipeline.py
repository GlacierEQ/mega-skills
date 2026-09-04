#!/usr/bin/env python3
"""Compose and execute a checked-in deep-work pipeline with the compositor engine.

External mutation remains forbidden. This runner only executes
`scripts/deep_work_stage.py` stages declared in pipelines/*.json.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def load_engine(root: Path):
    path = root / "skills" / "pipeline-compositor" / "scripts" / "engine.py"
    if not path.is_file():
        raise FileNotFoundError(f"pipeline compositor engine missing: {path}")
    spec = importlib.util.spec_from_file_location("pipeline_compositor_engine", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def pipeline_path(root: Path, pipeline_id: str) -> Path:
    direct = root / "pipelines" / f"{pipeline_id}.json"
    if direct.is_file():
        return direct
    raise FileNotFoundError(f"pipeline not found: {direct}")


def assert_firewall(spec: dict) -> None:
    if spec.get("deploy_mode") not in {None, "approval_packet_only", "forbidden"}:
        raise ValueError(f"unsupported deploy_mode: {spec.get('deploy_mode')}")
    banned = ("git push", "git merge", "vercel deploy", "gh release", "supabase db push")
    for stage in spec["stages"]:
        command = " ".join(stage.get("command", [])).lower()
        for token in banned:
            if token in command:
                raise ValueError(f"stage {stage['id']} contains forbidden command token: {token}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--pipeline", default="inception-to-deployment")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    engine = load_engine(root)
    spec = engine.load_pipeline(pipeline_path(root, args.pipeline))
    assert_firewall(spec)
    if args.validate_only:
        print(json.dumps({"status": "VALID", "pipeline_id": spec["id"], "stages": len(spec["stages"])}, indent=2))
        return 0
    manifest = engine.execute_pipeline(spec, workspace=root, resume=args.resume)
    print(json.dumps({"status": manifest["status"], "pipeline_id": spec["id"], "manifest": manifest.get("manifest")}, indent=2))
    return 0 if manifest["status"] == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
