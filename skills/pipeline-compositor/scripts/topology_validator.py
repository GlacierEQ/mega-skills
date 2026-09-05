#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import PipelineError, load_pipeline, topological_layers

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("pipeline", type=Path); a=p.parse_args()
    try: spec=load_pipeline(a.pipeline); layers=topological_layers(spec)
    except (PipelineError,OSError,ValueError) as exc: print(json.dumps({"status":"INVALID","error":str(exc)},indent=2)); return 2
    print(json.dumps({"status":"ACYCLIC","pipeline_id":spec["id"],"layers":layers},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
