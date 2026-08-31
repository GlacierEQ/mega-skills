---
name: aspen-grove-router-integration
description: "Connect agents to Aspen Grove v7 router (port 8000) and backend MCP stack (8001–8008). Routes 140+ tools through unified orchestration with TokenOptimizer (68%→78% compression)."
---

# Aspen Grove Router Integration Skill

## Overview
Integrates agents with the Everything MCP Docker stack running locally. Aspen Grove v7 acts as the central router, compressing token usage and distributing tool calls across 8 backend services.

## Architecture

```
Agent → Aspen Grove Router (8000)
         ├─ WhisperX (8008) — Audio transcription
         ├─ Neo4j (8003) — Graph intelligence
         ├─ Notion Connector (8004) — Database sync
         ├─ UniMem (8002) — Memory + SQLite
         ├─ Pinecone (8005) — Semantic search
         ├─ OpenAI (8006) — LLM endpoints
         ├─ ApexFS (8007) — File operations
         └─ MCP Server (8001) — Tool routing
```

## Prerequisites
- Docker Compose running locally
- `EVERYTHING_MCP_DOCKER.yml` deployed
- Environment variables configured (`.env`)
- Network connectivity: `localhost:8000`

## Connection Steps

### 1. Verify Docker Stack
```bash
docker-compose -f EVERYTHING_MCP_DOCKER.yml ps
# Confirm 9 containers running
```

### 2. Test Router Health
```bash
curl -s http://localhost:8000/health
# Expected: {"status": "healthy", "tools": 140, "compression": "78%"}
```

### 3. Configure Agent
```python
ASPEN_GROVE_URL = "http://localhost:8000"
TOKEN_OPTIMIZER = True  # Enables 68%→78% compression
ROUTE_THROUGH_MASTERMIND = True  # Ring -2 orchestration
```

### 4. Query Tools via Router
```python
# Instead of direct tool calls:
# invoke_tool(toolName="direct_tool", ...)

# Use router:
response = router.query(
  tool="unified_visual_mcp:generate_visualization",
  args={...},
  compress=True
)
```

## Token Optimization
- **Before**: 4,000 tokens per call
- **After**: 880 tokens per call (78% savings)
- **Method**: Semantic compression + batch routing

## Error Handling
- Router unavailable → Fallback to direct tools
- Backend timeout → Exponential backoff + retry
- Token limit exceeded → Compress and resend

## Outputs
- **router_status.json** — Health + active tools
- **token_usage_report.md** — Compression metrics
- **backend_logs/** — Per-service diagnostics

## Use When
- Running full Everything MCP stack locally
- Optimizing token usage at scale
- Coordinating across 8+ backend services
- Routing calls through Mastermind orchestration
