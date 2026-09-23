#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
STAGES=("intake","hydrate","power-fit","compose","execute","adversarial-verify","readback","preserve","handoff")
FILES={"intake":["MISSION.md","INTAKE.json"],"hydrate":["CONTEXT.md","HYDRATION.json"],"power-fit":["POWER_FIT_ROUTE.json"],"compose":["COMPOSITION.json","ARCHITECTURE.md"],"execute":["EXECUTION.json","STAGE_RECEIPTS.json"],"adversarial-verify":["VERIFY.json","EVIDENCE.md"],"readback":["READBACK.json"],"preserve":["PRESERVATION.json"],"handoff":["HANDOFF.md","STRONG_SMART_MISSION_RESULT.md"]}
def main(argv=None):
 p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,default=Path.cwd()); p.add_argument('--pipeline-id',default='strong-smart-mission'); p.add_argument('--stage',choices=STAGES,required=True); a=p.parse_args(argv); out=a.root.resolve()/'missions'/a.pipeline_id; out.mkdir(parents=True,exist_ok=True); now=datetime.now(timezone.utc).isoformat(); prior=STAGES[STAGES.index(a.stage)-1] if a.stage!='intake' else None
 payload={'schema_version':1,'pipeline_id':a.pipeline_id,'stage':a.stage,'status':'EXECUTED_LOCAL','timestamp':now,'operator_invariant':'STRONG AND SMART, NOT SMALL AND MINIMAL','previous_stage':prior,'claim_boundary':'Local artifact generation only; external effects require approval and provider-native readback.'}; payload['receipt_sha256']=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest(); written=[]
 for name in FILES[a.stage]:
  path=out/name
  if name.endswith('.json'): path.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
  else: path.write_text(f"# {name.rsplit('.',1)[0].replace('_',' ').title()}\n\n- Stage: `{a.stage}`\n- Status: `EXECUTED_LOCAL`\n- Receipt: `{payload['receipt_sha256']}`\n- Boundary: {payload['claim_boundary']}\n")
  written.append(path.relative_to(a.root.resolve()).as_posix())
 print(json.dumps({'status':'COMPLETED','stage':a.stage,'artifacts':written,'receipt_sha256':payload['receipt_sha256']},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
