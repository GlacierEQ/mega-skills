# GlacierEQ Mem Interop for OMP and Other AI

**Existing architecture, additive interoperability.** Live Mem stays in Mem and is shared with other AI clients through its **official OAuth MCP**; the private v2 snapshot remains accessible through a local read-only MCP stdio server. APEX/Aspen remain mission authority; Computer User/sigma-glue remain action/receipt owners. No new provider registry, public memory dump, or agent-runtime fork.

## What is real now
- Real Mem connected-app reading was used in the originating ChatGPT session, not in a separately provisioned OMP or Claude runtime.
- `bridge/mem_archive_mcp.py`: independent MCP stdio `initialize`, `tools/list`, `tools/call`; five read-only tools; locally tested against actual 835-note/219-body archive.
- `scripts/install_omp.py`: dry-run/backup/atomic additive config helper.
- `.omp/RULES.md`, `.omp/AGENTS.md`, three proper skills, OMP advisory current-turn hook, and docs.
- Existing private database lives in separate Library/Box backup. **Not in this source repository.**

## Start
1. Download existing private archive from `/GlacierEQ/Memory_Fabric_Portable_2026-10-21` in ChatGPT Library.
2. Review `docs/CLIENTS_AND_ACTIVATION.md`. Connect live `https://mcp.mem.ai/mcp` to each AI through its native OAuth.
3. For a host-controlled offline fallback, point `glaciereq-archive` at the private SQLite file and this bridge.
4. `python -m unittest discover -s tests -v` after setting `MEM_TEST_DB=/private/path/archive.sqlite`. The package has no embedded private dataset; tests that need it fail closed when missing.
5. Confirm actual host tools/list and native UUID readback before calling live integration complete.

## Guardrails
The archive is a snapshot; `MEM_SECONDARY` never establishes an external provider outcome. Search returns original UUID/title and classification hints, not note bodies. Body access requires `GLACIEREQ_MEM_ALLOW_BODIES=1` and, separately, `GLACIEREQ_MEM_ALLOW_RESTRICTED=1`; these are process-owner disclosure flags, **not access controls**. Never expose the bridge or snapshot over an unauthenticated network.