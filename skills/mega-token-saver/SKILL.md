---
name: mega-token-saver
description: "Token Saver"
---



# MEGA-TOKEN-SAVER

_Ingested from the opencode skill source. Bundled into the Monolith mega-skills catalog._


# Token Saver

The Mermicorn Token Saver is the active token-management layer. When
context is filling, the token saver:
1. Compacts redundant turns
2. Applies pre-built prompt packs
3. Routes long context to handoff files
4. Tracks budget per-session in `/root/.token_saver/cache.json`

**See:**
- `@/root/.agents/skills/master/SKILL.md` — the skill router (load this skill for routing, not for token-saver specifics)
- `@/root/.agents/skills/research-study-act/SKILL.md` — for the Tri-Phase mandate

## Quick rules

- **Token-saver cache is at `/root/.token_saver/`** (not `/root/mermicorn-token-saver`; that path is a broken legacy reference).
- **Source of truth is `/root/projects/mermicorn/token-saver`** (the actual project).
- **Cache is append-only.** Compaction doesn't delete turns; it marks them
  as compacted and writes the compaction record.
- **When context > 70% capacity**, the token saver activates automatically
  per `opencode.jsonc` (`compaction.auto = true`).

## How to use

```python
from token_saver import save, load, compact
save(user_id="alice", turn_id="...", text="...")
# On long context:
compacted = compact(user_id="alice", session_id="...", strategy="summarize")
```

## Sharp edges

- The cache is **per-user**. Empty user_id is a hard error, like all
  memory stores. Per `conversation-memory` skill.
- **Compacted turns are still auditable.** The compaction record is the
  receipt; the original turn is preserved.
- **Token budget is not the same as context window.** The token saver
  works at the message-level, not the model-level. Don't bypass it to
  "fit more in."
- **The cache file (`/root/.token_saver/cache.json`) is 10 KB** at last
  check. If it grows without bound, the saver has failed — check
  `token_saver.log`.

## When this skill does NOT apply

- A new session with no prior context (nothing to compact).
- A short task that fits comfortably in context.
- Tasks where the user explicitly asked for verbatim recall.
