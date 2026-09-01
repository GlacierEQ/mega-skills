#!/usr/bin/env python3
"""Execute the repository's declared Mega-Skills verification sequence."""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

def run(cmd, cwd):
    p=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True,check=False)
    return {"command":cmd,"returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",type=Path,default=Path.cwd()); ap.add_argument("--report",type=Path); a=ap.parse_args()
    repo=a.repo.resolve()
    specs=[([sys.executable,"scripts/validate_hierarchy.py"],True),([sys.executable,"-m","unittest","discover","-s","tests","-v"],True),(["git","diff","--check"],True),(["git","status","--short","--branch"],False)]
    records=[]; ok=True
    for cmd,required in specs:
        r=run(cmd,repo); r["required"]=required; records.append(r)
        if required and r["returncode"]!=0: ok=False
    payload={"status":"PASS" if ok else "FAIL","repo":str(repo),"checks":records}
    if a.report:
        target=a.report if a.report.is_absolute() else repo/a.report; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    for r in records:
        print("$"," ".join(r["command"]))
        if r["stdout"]: print(r["stdout"],end="" if r["stdout"].endswith("\n") else "\n")
        if r["stderr"]: print(r["stderr"],file=sys.stderr,end="" if r["stderr"].endswith("\n") else "\n")
    print(json.dumps({"status":payload["status"]}))
    return 0 if ok else 1
if __name__=="__main__": raise SystemExit(main())
