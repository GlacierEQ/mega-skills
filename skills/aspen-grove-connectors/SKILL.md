---
name: aspen-grove-connectors
description: "Universal multi-service MCP & API connector mesh. Bridges GitHub, Notion, Supabase, Dropbox, ClickUp, Linear, Vercel, DuckDB, Taskade, Pinecone, and E2B with rate-limiting, exponential backoff, credential sandboxing, and health telemetry."
---

# Aspen Grove Connectors Mesh

Operate as the **centralized external service connector fabric** for the APEX Estate. Provides resilient, typed adapters to third-party APIs and MCP servers with automatic secret resolution, backoff retry policies, and sandboxed mock modes for safe local execution.

## Supported Connector Services

| Service | Protocol | Key Endpoints / Tools | Sandboxed Mode |
|---|---|---|---|
| **GitHub** | REST / GraphQL / MCP | Repo, PRs, Commits, Issues, Actions | Mock Git Fixtures |
| **Notion** | REST / MCP | Pages, Databases, Blocks, Comments | Mock Workspace JSON |
| **Supabase** | PostgREST / Realtime | Table queries, RPC functions, Auth | SQLite / Local Mock |
| **Dropbox** | REST / Rclone | Files, Revisions, Shared Links | Local Virtual FS |
| **Linear** | GraphQL | Issues, Cycles, Teams, Projects | Mock Issue Graph |
| **ClickUp** | REST | Tasks, Lists, Spaces, Time Tracking | Mock Task DB |
| **Vercel** | REST / MCP | Deployments, Domains, Projects, Logs | Mock Deployment State |
| **DuckDB** | In-Process SQL | Parquet queries, OLAP analytics, Lakehouse | Embedded DuckDB |
| **Pinecone** | REST / gRPC | Vector Upsert, Query, Namespace Index | In-Memory Cosine Index |
| **Taskade** | REST | Workspaces, Agents, Task Outlines | Mock Outline DB |

## Core Operational Rules

1. **Credential Sandboxing**: Never hardcode secrets in source code. Credentials resolve from `os.environ` or `~/.secrets/<service>`. If missing in testing/CI, gracefully degrade to Sandboxed Mock Mode (`mock_mode=True`).
2. **Backoff & Rate Limiting**: All outbound HTTP requests enforce exponential backoff with randomized jitter (100ms base, 5 retries max).
3. **Fail-Closed Isolation**: Network errors or auth rejections emit structured error telemetry and never corrupt local mission state.
4. **Health Telemetry**: All connectors expose a `.health_check()` probe reporting latency, quota, and authentication status.
