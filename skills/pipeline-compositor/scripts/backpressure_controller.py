#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import PipelineError, load_pipeline

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("pipeline",type=Path); p.add_argument("--ready",type=int,required=True); p.add_argument("--max-parallel",type=int); a=p.parse_args()
    try: spec=load_pipeline(a.pipeline); limit=a.max_parallel or int(spec.get("max_parallel",1)); width=max(0,min(a.ready,limit,32))
    except (PipelineError,OSError,ValueError) as exc: print(json.dumps({"status":"INVALID","error":str(exc)},indent=2)); return 2
    print(json.dumps({"status":"OK","pipeline_id":spec["id"],"ready":a.ready,"effective_parallelism":width},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
