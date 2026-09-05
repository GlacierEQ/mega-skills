#!/usr/bin/env python3
"""Generic durable pipeline runner for mega-skills pipeline contracts.

Executes a pipelines/*.json contract in dependency order:
  - the {python} command placeholder resolves to the current interpreter
  - stages run sequentially; a non-zero stage exit aborts the run (fail-closed)
  - completion state is recorded in the pipeline's durable manifest after each
    stage, so an interrupted run resumes after the last verified stage
  - --resume skips stages already recorded complete when they are resume_safe
  - --dry-run prints the resolved execution plan without running anything
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_pipeline(path):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if doc.get("schema_version") != 1:
        raise SystemExit(f"unsupported pipeline schema_version: {doc.get('schema_version')}")
    if not doc.get("stages"):
        raise SystemExit("pipeline has no stages")
    return doc


def ordered_stages(doc):
    order, done = [], set()
    pending = list(doc["stages"])
    while pending:
        progressed = False
        for stage in list(pending):
            if all(need in done for need in stage.get("needs", [])):
                order.append(stage)
                done.add(stage["id"])
                pending.remove(stage)
                progressed = True
        if not progressed:
            unresolved = {s["id"]: [n for n in s.get("needs", []) if n not in done] for s in pending}
            raise SystemExit(f"unresolvable stage dependencies: {unresolved}")
    return order


def write_manifest(manifest_path, doc, state, done, failed=None):
    manifest = {
        "schema_version": 1,
        "pipeline_id": doc["id"],
        "state": state,
        "stages_completed": sorted(done),
        "last_run_utc": datetime.now(timezone.utc).isoformat(),
    }
    if failed:
        manifest["failed_stage"] = failed
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run(pipeline_path, resume=False, dry_run=False):
    doc = load_pipeline(pipeline_path)
    manifest_rel = doc.get("manifest")
    manifest_path = (ROOT / manifest_rel) if manifest_rel else None
    completed = []
    if resume and manifest_path and manifest_path.is_file():
        completed = json.loads(manifest_path.read_text(encoding="utf-8")).get("stages_completed", [])
    done = set(completed)
    executed, skipped, failed = [], [], None
    for stage in ordered_stages(doc):
        if stage["id"] in done and stage.get("resume_safe"):
            skipped.append(stage["id"])
            continue
        cmd = [sys.executable if token == "{python}" else token for token in stage["command"]]
        if dry_run:
            executed.append(stage["id"])
            done.add(stage["id"])
            continue
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        if proc.returncode != 0:
            failed = {
                "id": stage["id"],
                "returncode": proc.returncode,
                "tail": (proc.stdout + proc.stderr).strip().splitlines()[-10:],
            }
            break
        done.add(stage["id"])
        executed.append(stage["id"])
        if manifest_path:
            write_manifest(manifest_path, doc, "running", done)
    state = "failed" if failed else "completed"
    if manifest_path and not dry_run:
        write_manifest(manifest_path, doc, state, done, failed)
    report = {
        "pipeline": doc["id"],
        "state": state,
        "stages_executed": len(executed),
        "stages_skipped_resumed": len(skipped),
        "failed": failed,
    }
    print(json.dumps(report, indent=2))
    return 1 if failed else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Durable pipeline runner for pipeline contracts.")
    parser.add_argument("pipeline", help="Path to pipelines/<id>.json")
    parser.add_argument("--resume", action="store_true",
                        help="Skip stages already recorded complete in the durable manifest.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Resolve and report the execution plan without running stages.")
    args = parser.parse_args(argv)
    return run(args.pipeline, args.resume, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
