# SDK Master - independent cloud execution and reproduction

Mission: `sdk-master-operational-20261023`  
SDK: `GlacierEQ/sdk-ts` pinned to `8594587e77a6d31f649ebd4b40fe4a6189770461`  
Current acceptance: **OPEN** (the script passed, provider and CI admission remain unverified).

## Free-tier-first execution

Use the existing AWS Linux EC2 instance tagged `github-runner` (`us-west-2`, instance `i-09e62d6012bc289ed`). Its Systems Manager agent is online. Python 3.12, Node 24, Git and Yarn have been installed on the existing instance; no new compute was launched for this execution. **Cost Explorer has nonzero October EC2/VPC/Secrets Manager charges; a FreeTier tag does not prove zero cost.** Do not provision replacement machines, hosted browsers or paid runners without an explicit cost review. The Mac is offline until its operating system reinstall; no macOS job is required for SDK Master.

## Reproduce against the exact real SDK

On an authorized Linux host with Node 24, Python 3.12, git, Yarn 1.22.22 and dependencies:

```bash
git clone https://github.com/GlacierEQ/sdk-ts.git sdk-ts
cd sdk-ts
git checkout --detach 8594587e77a6d31f649ebd4b40fe4a6189770461
cd ..
bash mega-skills/skills/sdk-master/scripts/reproduce.sh "$PWD/sdk-ts" verify
```

The command runs the SDK Master's 33 Python regression tests, read-only manifest inspection, locked Yarn install, full TypeScript build, lint/typecheck, the SDK's Jest suites against Prism OpenAPI, and eight real loopback HTTP conformance requests covering success, 401, 429, 503, retry, timeout and cancellation. The script has **two distinct modes**: `verify` preserves an OPEN gate without conflating verified build with operational acceptance; `accept` returns nonzero until the signed evidence requirements, CI and provider readback succeed.

AWS SSM provider readback confirms the exact run: `69478d9d-a9e9-4702-8c1a-ca9c3d10436a`, start `2026-10-23T22:51:29.568Z`, finish `2026-10-23T22:52:09.568Z`, response code `0`. Script output contains `REPRODUCE_EXECUTION=PASS` and `SDK_REVISION=8594587e77a6d31f649ebd4b40fe4a6189770461`. The upstream test suite reported 216 passed and 33 skipped (7 passed, 4 skipped suites). The separate Python regressions reported 33 passed. The contract test executes SDK calls against **local HTTP**, not the external Supermemory API; no external provider mutation or provider-native state readback has been claimed.

## Source-bound receipts and truth gates

`receipts/MISSION_STATE.json` indexes SHA-256-bound criterion evidence under `receipts/evidence/`. The gate independently verifies expected criterion, tested SDK commit, executor run ID, exit code, kind, path containment, and SHA-256. This is **local evidence integrity** and does not magically verify provider facts. Required Supermemory provider readback and reliable CI runner allocation remain deliberately OPEN.

Previous PR #52 was closed without merge and its source branch deleted. This work resumes from its recovered exact commit on `feat/sdk-master-aws-verified-20261023`; do not silently reopen or assume merged.

## No new spending / no dependency on local Mac

Do not provision extra EC2/RDS, enable unpriced services, register a paid hosted runner, or wait for the Mac. Keep the current SSM run proof, check actual charges before prolonging AWS runtime, and make all external mutations reversible and authorized.
