# BrowserOS Neo ↔ existing OMP agent

Owner: GlacierEQ's existing OMP agent and Context First/APEX/Spiral governance. This is an **additive adapter**, not a second autonomous browser system. The BrowserOS Neo MCP and the vendor's single skill are both required.

## Authority and architecture

- BrowserOS Neo's **MCP sidebar page** is authoritative for the current loopback URL. Port `9012` was supplied by the user for one build; it can change. Never silently fall back to a guessed port.
- Oh My Pi uses `mcpServers.browseros-neo = {"type":"http","url":"http://127.0.0.1:<port>/mcp"}` in its **active user profile**. This script resolves `OMP_PROFILE`, `PI_PROFILE`, `PI_CONFIG_DIR`, and `PI_CODING_AGENT_DIR`, or can take an explicit `--config`.
- The upstream skill is installed **only** with `--skill browseros-neo`, preserving all unrelated skills/MCP entries.
- This adapter does not grant ChatGPT cloud direct access to `127.0.0.1`. The Mac-based agent uses the Mac-based browser. Session effects still require user authorization and owner-native receipts.

## Safe deployment, when the correct Mac's device connector is online

The workflow's hosted job runs portable tests. A self-hosted Mac preflight is deliberately **manual-only**; **never use GitHub Actions to run `--apply`**. Run from the Mac account that actually launches OMP, not root or a different CI service account.

```bash
python3 integrations/omp/browseros_neo_setup.py \
  --endpoint 'http://127.0.0.1:9012/mcp'
```

This is a **no-write preflight**, requiring exact host identity, valid existing JSON, protocol-level MCP `initialize` followed by `tools/list` (including real named tools), and an explicit loopback endpoint. If any gate fails, no configuration changes occur. It doesn't read browser pages.

Only after reviewing those preflight results and confirming the URL on the BrowserOS MCP page:

```bash
python3 integrations/omp/browseros_neo_setup.py --apply \
  --endpoint 'http://127.0.0.1:9012/mcp'
```

The installer refuses conflicting `browseros-neo` entries, checks OMP and npm tooling, verifies a valid upstream skill file, backs up any existing config as a timestamped `mcp.json.bak.*`, atomically updates JSON, and reads back the new config. Existing skills and other MCP servers are not replaced. Subsequent identical runs are configuration-idempotent; use `--refresh-skill` only when intentionally updating the upstream skill.

**Important:** A successful local installer does *not* mean OMP has reloaded its tools. In the **actual active OMP session**, run:

```text
/mcp reload
/mcp list
/mcp test browseros-neo
```

Then confirm the skill is discoverable in OMP, and use a BrowserOS `tabs` or `snapshot` read as a non-destructive end-to-end test before any website write. BrowserOS instructs agents to create/nickname their own sessions and tabs rather than hijack user tabs. Preserve session and provider receipts through existing GlacierEQ continuity infrastructure.

## Failure, rollback, and proof boundaries

- A TCP listener alone is insufficient. The installer requires MCP protocol negotiation and tools disclosure. A browser tab or website remains unverified until a provider tool actually reads it.
- If the skill install fails, the OMP JSON is untouched.
- After a config update, the printed `BACKUP=` path preserves the old bytes; the tested `restore_backup(path, backup, expected_current)` refuses rollback over a newer intervening edit.
- A malformed or symlinked existing config is never overwritten.
- Mac offline, test job unavailable, or wrong macOS account = **UNVERIFIED / NO INSTALL**. No success claims based only on repository commits, workflow YAML, or tests.
- The draft PR should not be merged merely because portable tests passed. Require macOS device connectivity, actual OMP session tool proof, and independent readback.

## Official references

- [BrowserOS Neo manual MCP setup](https://docs.browseros.com/neo/mcp/manual)
- [BrowserOS Neo skill](https://www.skills.sh/browseros-ai/browseros/browseros-neo)
- [OMP MCP configuration and profiles](https://github.com/can1357/oh-my-pi/blob/main/docs/mcp-config.md)
