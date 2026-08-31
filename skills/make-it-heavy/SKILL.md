---
name: make-it-heavy
description: "Operating inside the Make-It-Heavy multi-agent swarm project at /root/projects/make-it-heavy. Use when adding workers, modifying orchestrator logic, extending the persistent SwarmMemory, writing tools, or running the test suite. Covers role-bound workers, GeniusOrchestration, policy-bound tool allowlisting, and tiered memory."
---



# Make-It-Heavy Skill

Write-capable, policy-bound multi-agent swarm runner for heavy analysis,
repository improvement, and README star-map maintenance.

## Project Layout

| Path | Purpose |
|------|---------|
| `make_it_heavy.py` | Interactive CLI with live progress bars |
| `orchestrator.py` | `TaskOrchestrator` — mission decomposition + worker fan-out |
| `agent.py` | Single-agent loop (ReAct-style) |
| `local_agent.py` | Local-only agent variant |
| `memory.py` | `SwarmMemory` — SQLite missions/agent_runs/tool_calls/cache |
| `memory_tiered.py` | `TieredMemory` — STM/LTM/entity with FTS5 retrieval |
| `tools/` | Tool registry: calculator, file read/write, web search, Smithery MCP |
| `make_it_heavy/` | Package: `genius_orchestration.py`, `run_state.py`, `batch.py` |
| `config.yaml` | Worker roles, model assignments, policy allowlist |
| `tests/` | 220+ unit + integration tests |

## Key Commands

```bash
# CLI with live progress
cd /root/projects/make-it-heavy && python make_it_heavy.py

# Genius mode (deep, multi-pass)
cd /root/projects/make-it-heavy && python make_it_heavy.py --genius

# Full test suite
cd /root/projects/make-it-heavy && python -m unittest discover tests

# Targeted tests
cd /root/projects/make-it-heavy && python -m unittest tests.test_memory_tiered -v
```

## Memory Architecture

Two layers — pick deliberately:

1. **`SwarmMemory`** (`memory.py`) — flat store for missions, agent runs, tool
   calls, and LLM-response cache. Use for telemetry, audit trail, and mission
   replay.

2. **`TieredMemory`** (`memory_tiered.py`) — three tiers, all user-scoped:
   - **STM**: last 20 turns per user, 24h TTL, FTS5 indexed
   - **LTM**: consolidated summaries, 90d TTL, touch-on-read
   - **Entity**: typed facts, unlimited, conflict-tracked

   Use when building anything that needs user-aware recall. **Always pass
   `user_id`** — empty `user_id` is a hard error (privacy boundary).

## Tool Registry

Tools live in `tools/` and are allowlisted by `config.yaml`. Adding a tool:

1. Implement the function (sync or async).
2. Register it in `tools/__init__.py` with name, schema, and example.
3. Add an entry in `config.yaml` under the `tools:` section.
4. Write a test in `tests/test_<tool_name>.py`.
5. Verify with `python -m unittest tests.test_<tool_name> -v`.

## Worker Roles

Defined in `config.yaml` under `agents:`. Each role binds:

- `model` (gpt-4, claude-sonnet, etc.)
- `system_prompt`
- `tool_allowlist` (subset of the registered tools)
- `max_iterations` (default 10, never set to 0 or None)

## Sharp Edges

| Issue | Severity | Solution |
|-------|----------|----------|
| Worker role without `max_iterations` — infinite ReAct loop | critical | **Always set `max_iterations`** on every role. Default 10. |
| Tool not in `config.yaml` allowlist — silently fails at runtime | high | **Every tool must be allowlisted** in config before registration is enough. |
| `TieredMemory.retrieve()` called without `user_id` | critical | **Empty `user_id` raises `ValueError`** — never bypass this for "anonymous" users; require a session id. |
| `genius_orchestration` runs deep — can burn tokens fast | high | **Use `--genius` only for high-value missions.** Default mode is faster and cheaper. |
| Adding a tool without a test | medium | **No tool merges without a test** — `tests/test_<tool>.py` is mandatory. |
| Smithery MCP connector fail-open | high | **Connector is fail-closed by default** — never relax transport validation. |

## Related Skills

- `agent-memory-systems` — memory tier selection and retrieval strategy
- `conversation-memory` — user-isolated tiered memory patterns
- `ai-agents-architect` — ReAct, Plan-and-Execute, tool registries
- `clean-code` — pragmatic Python standards
- `apex-sovereign-runtime` — receipt-chain doctrine (when wiring mastermind interop)
