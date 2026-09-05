#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import PipelineError, load_checkpoint, load_pipeline

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("pipeline",type=Path); p.add_argument("--workspace",type=Path,default=Path.cwd()); p.add_argument("--state-dir"); a=p.parse_args()
    try: spec=load_pipeline(a.pipeline); state=load_checkpoint(spec,a.workspace.resolve(),a.state_dir)
    except (PipelineError,OSError,ValueError) as exc: print(json.dumps({"status":"INVALID","error":str(exc)},indent=2)); return 2
    print(json.dumps({"status":"OK","pipeline_id":spec["id"],"checkpoint":state},indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
