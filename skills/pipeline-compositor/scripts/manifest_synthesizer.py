#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("manifest",type=Path); a=p.parse_args()
    try: m=json.loads(a.manifest.read_text(encoding="utf-8"))
    except Exception as exc: print(json.dumps({"status":"INVALID","error":str(exc)},indent=2)); return 2
    required={"schema_version","pipeline_id","status","stage_results","summary"}; missing=sorted(required-set(m))
    if missing: print(json.dumps({"status":"INVALID","missing":missing},indent=2)); return 2
    print(json.dumps({"status":"VALID","pipeline_id":m["pipeline_id"],"execution_status":m["status"],"summary":m["summary"]},indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
