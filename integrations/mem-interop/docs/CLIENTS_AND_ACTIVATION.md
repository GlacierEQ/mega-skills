# Mem native MCP clients + GlacierEQ archive fallback

Official docs: https://docs.mem.ai/mcp/setup
Live hosted Mem MCP: https://mcp.mem.ai/mcp (OAuth). The URL is verified in current vendor documentation; this package cannot authenticate another user's AI client remotely.

## Claude / Claude Code
Claude web/desktop: Customize → Connectors → Mem → connect with OAuth; optionally add custom connector at `https://mcp.mem.ai/mcp`.
Claude Code: `claude mcp add --transport http mem https://mcp.mem.ai/mcp` then `/mcp` and complete OAuth.

## Codex and Gemini CLI
`codex mcp add mem --url https://mcp.mem.ai/mcp` then authenticate on first tool call.
`gemini mcp add -s user -t http mem https://mcp.mem.ai/mcp` then `gemini` and `/mcp auth mem`.

## OMP
OMP project config: `.omp/mcp.json`; `mem-live` as `type: http`, URL as above. `glaciereq-archive` as stdio with `python3` and absolute paths to `mem_archive_mcp.py` and the private SQLite database. The `scripts/install_omp.py` command **dry-runs by default** and preserves existing server entries, rejects collisions, backs up file and readbacks after `--apply`. Don't overwrite the owner's current config.

Run:
`python scripts/install_omp.py --config /PATH/TO/.omp/mcp.json --db /PRIVATE/PATH/archive.sqlite --server /PATH/TO/bridge/mem_archive_mcp.py`
After review, explicitly append `--apply`. In OMP run `/mcp reload`, `/mcp list`, `/mcp test mem-live`, `/mcp test glaciereq-archive`, follow the OAuth flow, then query a **known current** Mem UUID via live native Mem tools. Compare UUID/title/readback, and query the same UUID offline to confirm shared identity. OMP extension startup checks are still unverified without an installed host; never claim them passed from local code tests.

## Connected AI handoff examples
- "Use `mem-live` to search GlacierEQ JOB; return the original UUID, note version, and exact source links. Do not send messages."
- "Recover `1FDV-23-0001009` from Mem then independently verify the docket; list draft vs filed separately."
- "If live Mem is unavailable, query `glaciereq-archive.memory_mission`; label the result historical and state which source needs live validation."

## Deployment gates
1. Project package tests pass.
2. Owner-side OMP config applied with backup and parse readback.
3. OMP `tools/list` confirms both servers; live OAuth authorized.
4. Cross-client source read of 2 real UUIDs returns correct version and metadata without full sensitive text disclosure.
5. Process-stop/restore works with the archive; provider execution still governed externally.
6. No claims of autonomous cross-session boot until independently tested in the actual host.