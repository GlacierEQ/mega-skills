# SDK Master — independent execution and reproduction

**Canonical SDK:** `GlacierEQ/sdk-ts` commit `8594587e77a6d31f649ebd4b40fe4a6189770461`, `supermemory@3.0.0-alpha.26`.

**Owning skill:** `GlacierEQ/mega-skills/skills/sdk-master`. This is composition and verification of existing code—not a replacement orchestrator.

## Run on an existing Node/Python build host

Requires Git, Node.js 24, Yarn 1.22.22, Python 3.12, and network access to published dependencies and the SDK's OpenAPI specification. On Amazon Linux 2023, the already-operational runner was provisioned through AWS Systems Manager with `git`, `nodejs24`, `nodejs24-npm`, `python3.12`, and `lsof`.

```bash
git clone https://github.com/GlacierEQ/sdk-ts.git /path/sdk-ts
git -C /path/sdk-ts checkout --detach 8594587e77a6d31f649ebd4b40fe4a6189770461
# Run from a checked-out mega-skills tree with the SDK Master skill:
bash skills/sdk-master/scripts/reproduce.sh /path/sdk-ts verify
```

`verify` executes unit/regression tests, static manifest inspection, the SDK's frozen-lockfile install, build, lint and 216 active SDK tests, plus an independent real HTTP loopback conformance scenario covering positive response, 401, 429, 503, retries, timeout, and abort. The SDK's default tests use an OpenAPI Prism mock server; the conformance suite uses an actual local HTTP server, **not** a remote authenticated provider.

```bash
# Explicit fail-closed external mission acceptance; expected to fail while OPEN:
bash skills/sdk-master/scripts/reproduce.sh /path/sdk-ts accept
```

## Verified AWS execution context

An existing EC2 instance in `us-west-2` named `github-runner` was found RUNNING and SSM ONLINE; it was **not** a registered GitHub Actions runner. AWS SSM commands installed the needed build tools and executed the pinned SDK from `/opt/sdk-master-run/sdk-ts`. Relevant readback IDs:

| Activity | AWS SSM command ID | Observation |
| --- | --- | --- |
| Git, Node 24, npm | `e177fcf5-f90b-406d-9072-d4070c635681` | success |
| Pinned SDK Git checkout | `0faa64a2-ca89-421f-b1f2-3bfbc840b920` | exact SHA matched |
| Frozen Yarn install | `66adfe19-471a-41e4-9082-7019de6fff70` | success |
| SDK build/lint/test initial | `4b354db1-fb6f-4361-9827-cd3db9a6c9fd` | build/lint passed; test startup collided on Prism port 4010 |
| SDK suite, existing Prism | `c594daa5-7268-4a73-b585-a3a873699a54` | 216 passed; 33 skipped |
| Real HTTP conformance | `d5491b4e-2eda-47e6-a54f-aefb45590206` | pass, 9 HTTP requests |
| Python 3.12 gate + inspector | `b475b43c-7cb2-4997-95ba-d8b63077c719` | 33 tests passed |

A Python 3.9 probe yielded three expected TOML-dependent test failures because Python 3.9 lacks standard-library `tomllib`. The CI-matching Python 3.12 runtime passed all 33 tests. These are different execution environments, not contradictory conclusions.

## Provider and CI boundaries

- SDK exports, CommonJS/ESM imports, TypeScript compilation, local HTTP error mapping, and retry behavior have been exercised.
- Live Supermemory provider authentication, authorized mutations and state readback have **not** been established. The local HTTP server and Prism cannot prove provider state.
- GitHub Actions hosted-runner jobs failed before runner assignment (zero executed steps). Existing private full-validation workflow requires `[self-hosted, mega-skills, macos-x64]`; the available AWS instance is Linux x64.
- The AWS runner's SSM repository URL parameter was the literal placeholder `https://github.com/YOUR_ORG/YOUR_REPO`; its registration-token parameter was issued much earlier and needs a fresh token. Neither a placeholder nor a stored stale token establishes GitHub registration.
- GitHub PR #52 was closed **without merge**, and its head branch deleted by an external concurrent action on October 23, 2026. The verified head `5fc75af12bdda5886fdd3c54376579a3b26c1fb7` was recovered into continuation branch `feat/sdk-master-aws-verified-20261023`. No force push or merge occurred.

Recheck AWS SSM command invocations and GitHub source revision before promoting any evidence to completion. Unverified remains OPEN.
