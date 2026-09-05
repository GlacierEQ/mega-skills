#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import PipelineError, execute_pipeline, load_pipeline

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("pipeline",type=Path); p.add_argument("--workspace",type=Path,default=Path.cwd()); p.add_argument("--state-dir"); p.add_argument("--resume",action="store_true"); p.add_argument("--max-parallel",type=int); a=p.parse_args()
    try: result=execute_pipeline(load_pipeline(a.pipeline),a.workspace,state_dir=a.state_dir,resume=a.resume,max_parallel=a.max_parallel)
    except (PipelineError,OSError,ValueError) as exc: print(json.dumps({"status":"FAILED","error":str(exc)},indent=2)); return 2
    print(json.dumps(result,indent=2,sort_keys=True)); return 0 if result["status"]=="COMPLETE" else 1
if __name__=="__main__": raise SystemExit(main())
