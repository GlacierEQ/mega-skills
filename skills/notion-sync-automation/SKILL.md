---
name: notion-sync-automation
description: Bidirectional sync between unified-memory-mcp and Notion databases. Real-time memory ↔ Notion replication with conflict resolution and audit trails.
---

# Notion Sync Automation Skill

## Overview
Maintains live bidirectional synchronization between agent memory systems (Mem0 cloud + SQLite local) and Notion databases. Enables Notion as command layer while preserving distributed memory.

## Architecture

```
Agent Memory System          Notion DB
├─ Mem0 (cloud chunks)   ←→  ├─ Pantheon
├─ SQLite (~/.unified_memory.db) ↔  ├─ SUPERLUMINAL_CASE_MATRIX
├─ .env (~/02_SYSTEM_TOOLS/.env)   ├─ WhisperX FedTrans DB
└─ Local cache          ←→  ├─ CONNECTORS HUB
                             └─ ELYSIUM Community
```

## Sync Modes

### 1. Pull (Notion → Memory)
- Notion DB changes trigger memory update
- Timestamp comparison (Notion > Local)
- Conflict resolution: Notion wins (source of truth)

### 2. Push (Memory → Notion)
- Agent work → Memory → Notion
- Batch every 5 minutes or on-demand
- Preserves audit trail

### 3. Bidirectional (Live)
- Polling interval: 30 seconds
- Conflict detection: timestamp + hash
- Resolution: Last-write-wins with logging

## Configuration

### Memory Side
```python
NOTION_SYNC_ENABLED = True
NOTION_API_TOKEN = "env:NOTION_API_KEY"
SYNC_INTERVAL_SECONDS = 30
CONFLICT_RESOLUTION = "last_write_wins"
AUDIT_LOG = "~/.notion_sync_audit.log"
```

### Notion Side
Create columns on each DB:
- `_sync_timestamp` (date) — Last sync
- `_sync_hash` (text) — Content hash
- `_source` (enum) — "agent" | "user" | "external"
- `_audit_trail` (text) — Change log

## Conflict Resolution

```
IF Notion.timestamp > Memory.timestamp:
  → Notion wins, Memory updates
ELSE IF Memory.timestamp > Notion.timestamp:
  → Memory wins, Notion updates
ELSE:
  → Hash comparison
    IF hashes differ: Manual review flag
    IF hashes same: Skip (no change)
```

## Notions DBs Synced

| DB | Purpose | Sync Direction |
|:---|:---|:---|
| ELYSIUM (325b1e...) | Pantheon + Community | ↔ Bidirectional |
| SUPERLUMINAL (5fedbd...) | Case Intelligence | → Push only |
| WhisperX (20024ac...) | Audio Transcripts | ← Pull + audit |
| CONNECTORS (4434b4...) | Tool Inventory | → Push only |

## Sync Process

### 1. Query Memory
```python
records = memory.query(
  table="aspen_grove_memory",
  filters={"modified_after": last_sync}
)
```

### 2. Fetch Notion
```python
notion_records = notion.query_database(db_id, filters={
  "_sync_timestamp": {"last_edited_time": {"after": last_sync}}
})
```

### 3. Merge Changes
```python
for notion_item in notion_records:
  if notion_item._sync_timestamp > memory_cache:
    memory.update(notion_item)
  if memory_item._sync_timestamp > notion_item:
    notion.update(memory_item)
```

### 4. Log Audit Trail
```json
{
  "timestamp": "2026-06-22T10:54:00Z",
  "direction": "pull",
  "records_synced": 47,
  "conflicts_detected": 2,
  "conflicts_resolved": "last_write_wins"
}
```

## Monitoring

### Sync Health
```bash
curl http://localhost:8000/notion-sync/status
# {
#   "last_sync": "2026-06-22T10:54:00Z",
#   "records_synced": 2847,
#   "conflicts": 0,
#   "lag_seconds": 3
# }
```

### Audit Trail
```bash
tail -f ~/.notion_sync_audit.log
```

## Use When
- Operating Notion as command layer
- Maintaining distributed memory
- Cross-team knowledge sharing
- Requiring immutable audit trails
- Syncing case intelligence across tools
