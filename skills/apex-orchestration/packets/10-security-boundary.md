# Packet 10 — SECURITY-BOUNDARY

**Owner:** apex-orchestration v1.0.0
**Maturity:** 9 / "Default-deny, blast-radius scoped, every action auditable"
**Layer:** Skill
**Scope:** What the operator and its lanes may read, write, send, and execute.

---

## Invariant (L5)

The orchestrator is **default-deny**. Every action is gated by:

1. An explicit allow-list (lane permission or skill permission).
2. A blast-radius check against `mission.blast_radius`.
3. A secrets check (no PII, no credentials, no tokens in any artifact).

A gate failure is a hard REFUSE, not a warning.

## Action Taxonomy (closed set)

| Action | Default | Gate |
|--------|---------|------|
| read local file | allow | within `mission.blast_radius.paths[]` |
| write local file | allow | within `mission.blast_radius.paths[]` AND lane has `edit` permission for the path glob |
| execute shell | allow | lane has `bash: allow` AND command is not in `forbidden_commands[]` |
| call MCP tool | allow | MCP server is enabled AND lane has `mcp: allow` |
| call external HTTP | deny | requires explicit `mission.blast_radius.external[]` allow-list |
| access network FS / cloud | deny | requires explicit `mission.blast_radius.cloud[]` allow-list |
| modify credentials / secrets | deny | always, no override |
| submit a form / file externally | deny | requires `human_approval` checkpoint |
| run deployment | deny | requires `human_approval` checkpoint |

## Forbidden Commands (closed set)

```
rm -rf /
dd if=
mkfs
curl | sh
wget | sh
:(){:|:&};:
chmod -R 777 /
kill -9 1
iptables -F
sudo *
```

Plus anything matching `**/.git/**` mutation, `**/secrets/**` read, `**/.env*` read.

## Forbidden Paths (closed set)

```
~/.ssh/**
~/.aws/**
~/.gcloud/**
~/.config/gh/**
**/secrets/**
**/.env
**/.env.*
**/credentials.json
**/service-account*.json
~/.local/share/kilo/auth.json
~/.local/share/kilo/mcp-auth.json
~/.local/share/kilo/session-export.db    # contains scrubbed PII
```

## Human Approval Checkpoints

The orchestrator must pause and ask before:

- Deploying to production
- Pushing to a remote git remote
- Submitting a court filing
- Spending more than `mission.budget.alert_threshold` (default 80%)
- Running a command that matches `dangerous_patterns[]` but is not in `forbidden_commands[]`

## Gates

- **G1 — Default-deny gate.** New action types are denied until added to allow-list.
- **G2 — Blast-radius gate.** Even allowed actions are checked against `mission.blast_radius` at execution time.
- **G3 — Secrets gate.** Receipts are scanned for credential-shaped strings before DELIVERY. Match = BLOCK.
- **G4 — Audit gate.** Every action is recorded in `audit.jsonl` with `actor`, `lane`, `action`, `target`, `ts`, `result`.

## Anti-Patterns

- "It's only a read" (reads can leak credentials).
- "It's only a write to /tmp" (write to outside blast radius).
- Running shell without checking forbidden_commands.
- Skipping approval checkpoints "to save time."

## L2 Evidence

- `audit.jsonl` is append-only, one line per action, sha256-chainable.
- Secret-scan test: feed known credential strings, expect BLOCK.
- Forbidden-command test: feed each entry, expect REFUSE.

## Versioning

- Major bump: relaxing a gate, removing a forbidden command.
- Minor bump: adding a new entry to `forbidden_commands` or `forbidden_paths`.

Current version: **1.0.0**
