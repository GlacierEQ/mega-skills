# GlacierEQ Mem.ai — Portable Cross-Agent Connection and Runtime Certification

**Owner:** Existing `skills/unified-memory-connect/SKILL.md`. **Source:** current Mem notes and [Mem's official MCP setup](https://docs.mem.ai/mcp/setup). **State:** documentation + profile on a review branch; NOT host installation, gateway live verification, or automatic session-boot proof.

## 1. Connect a real client, without credential copying

Mem.ai is **not Mem0**. Mem.ai's first-party hosted Streamable HTTP MCP URL is `https://mcp.mem.ai/mcp`. Authenticate via that client's OAuth; credentials from ChatGPT cannot be inherited by OMP or another agent.

| Client | Provider-documented entry point | Sign-in |
| --- | --- | --- |
| Claude (web/desktop) | Customize → Connectors → Mem; or Settings → Connectors → Add custom connector → `https://mcp.mem.ai/mcp` | OAuth |
| Claude Code | `claude mcp add --transport http mem https://mcp.mem.ai/mcp` | `/mcp` |
| Codex CLI | `codex mcp add mem --url https://mcp.mem.ai/mcp` | Browser OAuth |
| Gemini CLI | `gemini mcp add -s user -t http mem https://mcp.mem.ai/mcp` | `/mcp auth mem` |
| ChatGPT | Connect existing Mem plugin | OAuth via host |
| OMP Glacier | Use existing native `.omp` MCP configuration/profile; discover *current host-version* syntax and transport before any edit | Authorized runtime credential handling |

The historical GlacierEQ gateway `https://glaciereq-memory-gateway.onrender.com/mcp` is **not** interchangeable with the first-party Mem.ai endpoint. Gateway identity, status, tool names, authentication and fan-out require fresh live discovery. It was recovered from Mem continuity, not successfully probed in this session.

Avoid placing credentials in Mem notes, prompts, committed files, sample configs, agent output or logs. OAuth sign-in or the current runtime's secret store is the credential boundary.

## 2. Exact-ID startup path for any agent

1. Interpret current user request, identify one actual mission and operator authorization; do not run a cached prior mission.
2. Verify client's Mem MCP initialization and `tools/list`. A config file is not connection proof. Find provider-exposed equivalent of exact-ID `get_note`.
3. Exact-read Mem living handoff `c3054a58-409e-5ee6-9c15-eec694b9a34a`. Use the current Mem version and current explicit supersessions.
4. For systems/skills/connectors tasks, exact-read boot manifest `6925915b-33d6-5fc9-b499-4fbe78790413`, federation charter `63f1d7cd-9202-577a-8d0d-211c40a07606`, and memory mesh map `e959992a-9df3-56fa-b811-f83a183d473b`; for other tasks read ONLY relevant domain owner notes selected by the handoff. Respect restricted-child, private legal, health, and employer scopes.
5. Recover source-bearing records by source-native IDs. A note summarizing Gmail, court, GitHub or Supabase state is not that provider's action/readback.
6. Continue real execution: **RECOVER → MATCH INTENT/AUTHORITY → APPLY → EXECUTE → VERIFY → PRESERVE → CONTINUE**.
7. Save a bounded, version-checked continuation in the **existing owner note**, then exact-ID readback. Do not mint new summary notes for every tool call or assert durable continuity from a generated paragraph.

## 3. Required continuation record

Use this envelope as fields/structure inside the owning Mem note; it is not a new global authority:

```yaml
work_unit_id: <stable outcome identity>
mission: <current user-requested goal>
actor: <agent/runtime identity>
origin: <provider + provider-native source ID>
source_version: <commit / note version / event ID / provider timestamp>
operator_intent: <attributed user instruction>
permission_scope: <exact approved action boundary>
classification: <source fact | user account | inference | disputed | unverified>
last_action: <what really occurred>
native_receipt: <provider native request, message, run, or commit ID; null if absent>
readback: <independent exact provider state + time; null if absent>
contradictions: <source-linked unresolved conflict list>
next_cursor: <single concrete next executable action>
```

Distinguish `PREPARED`, `ATTEMPTED`, `PROVIDER_ACCEPTED`, `READBACK_VERIFIED`, `EFFECTIVE` and `BLOCKED`. An agent may propose/calculate/document work, but none of those are a sent email, filed court motion, deployed worker, installed connector, or actual other-agent memory load.

## 4. Version and ambiguity discipline

Mem note updates submit the **complete replacement body** and exact current `version`; after update fetch by stable note ID and check content, version, and collection membership. If the version changes unexpectedly, recover and reconcile rather than clobber edits. A timeout after an attempted mutation is **ambiguous** until native readback. Never retry a side-effectful write or switch routes automatically solely because its response timed out.

No domain requires full federation availability if a qualified source path works. 401/403 means authentication or permission; 429 means obey rate-limit guidance; unsuccessful search is not nonexistence.

## 5. Proof stages, acceptance and negative tests

- `CONFIGURED`: host's effective config contains intended endpoint; may still be disconnected.
- `INITIALIZED`: actual MCP handshake succeeds with that host session.
- `DISCOVERED`: actual `tools/list` shows a usable Mem exact-read tool.
- `READ_VERIFIED`: actual authenticated exact-ID read returns expected Mem note ID and current version/content.
- `WRITE_VERIFIED`: approved owner-note write followed by exact-ID readback confirms current content/version.
- `CROSS_SESSION_APPLIED`: **independent clean session** resolves active task, reads correct current notes and source, executes appropriately, preserves proof, and does not repeat a previously completed external effect.

Certification is per host, identity, transport, permission scope and timestamp; passing one stage doesn't imply the next.

Negative tests to run: no auth; wrong workspace; missing tool; partial search hit; stale version; concurrent update; timeouts after attempted write; contradictory provider and Mem status; irrelevant legal material leaking into a JOB boot; user asks about a different mission than last session; frozen old note; external side effect lacking approval; new session that parrots doctrine without applying it.

## 6. OMP Glacier native projection

Reuse current OMP agent, `.omp/skills`, `RULES.md`/agent profile and native MCP registration. Do **not** replace them with a parallel supervisor, update the installed machine from a ChatGPT message, or assume the old Intel Mac is currently online. Add this existing skill to the active OMP profile's *supported* skill-loading/trigger mechanism only after the remote MCP handshake and effective profile are inspected. Capture `/mcp list` / client equivalent, tool schema, exact-ID Mem read, and fresh-session application receipt. No invented command syntax for OMP profile edits.

Cloud-first target: each AI talks to Mem's **hosted** MCP over HTTPS after user-approved OAuth. The GlacierEQ gateway is a separately certifiable, optional federation/fan-out route. It does not need a local Mac or Termux relay for Mem-native reads.

## 7. Execution next cursor

GitHub skill source and JSON manifest are only **packaged** until OMP/Claude/Gemini/Codex independently authenticates and reads these exact Mem notes. The package review must retain existing older skill behavior. Do not merge, deploy, auto-send or broaden permission scope without authorization. If an external client isn't accessible, leave that particular lane explicitly unverified while other independently available lanes continue.
