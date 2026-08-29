---
name: mega-aspen-grove
description: Aspen Grove Connectors Skill — Multi-Service Integration
domains: [aspen-grove]
token_profile: Lean
---

# MEGA-ASPEN-GROVE

_Ingested from the opencode skill source. Bundled into the Monolith mega-skills catalog._


# Aspen Grove Connectors Skill — Multi-Service Integration

## Keywords
`aspen grove` `connectors` `mcp server` `multi-service` `connector registry` `health monitoring`
`connector discovery` `github connector` `notion connector` `supabase connector` `dropbox connector`
`clickup connector` `linear connector` `vercel connector` `onedrive connector` `taskade connector`
`memoryplugin connector` `pinecone connector` `duckdb connector` `connector registration`
`connector sync` `data synchronization` `cross-service` `api orchestration` `service mesh`
`connector health` `connector metrics` `connector authentication` `oauth` `api key management`
`token refresh` `rate limiting` `error handling` `retry logic` `circuit breaker` `connector lifecycle`
`connector configuration` `connector deployment` `connector testing` `connector documentation`
`connector versioning` `connector security` `connector monitoring` `connector logging`
`connector auditing` `connector backup` `connector recovery` `connector scaling`
`connector optimization` `connector profiling` `connector benchmarking` `connector analytics`
`connector reporting` `connector dashboard` `connector alerts` `connector notifications`
`connector webhooks` `connector events` `connector triggers` `connector workflows`
`connector pipelines` `connector chains` `connector composition` `connector federation`
`connector governance` `connector compliance` `connector standards` `connector patterns`

## Architecture

```
aspen-grove-connectors/
├── connectors/               # Individual connector implementations
│   ├── github-mcp/           # GitHub MCP connector
│   ├── notion-mcp/           # Notion MCP connector
│   ├── supabase/             # Supabase connector
│   ├── dropbox/              # Dropbox connector
│   ├── clickup/              # ClickUp connector
│   ├── linear/               # Linear connector
│   ├── vercel/               # Vercel connector
│   ├── onedrive/             # OneDrive connector
│   ├── taskade/              # Taskade connector
│   ├── memoryplugin/         # MemoryPlugin connector
│   ├── pinecone/             # Pinecone connector
│   └── motherduck/           # DuckDB connector
├── registry/                 # Connector registry and discovery
├── health/                   # Health monitoring and metrics
├── foundation/               # Foundation layer
├── workloads/                # Workload management
├── .github/workflows/        # CI/CD
├── .glaciereq/               # Configuration
├── GROVE_MANIFEST.json       # Manifest file
├── README.md                 # Documentation
└── health_check.py           # Health check script
```

## Connector List

| Connector | Purpose | Auth Method | Status |
|-----------|---------|-------------|--------|
| GitHub | Repos, PRs, issues, CI/CD | PAT/OAuth | ✅ |
| Notion | Databases, pages, blocks | API Key | ✅ |
| Supabase | Database, auth, storage | Service Key | ✅ |
| Dropbox | Files, folders, sharing | OAuth | ✅ |
| ClickUp | Tasks, lists, spaces | API Key | ✅ |
| Linear | Issues, projects, teams | API Key | ✅ |
| Vercel | Deployments, domains | Token | ✅ |
| OneDrive | Files, sharing | OAuth | ✅ |
| Taskade | Projects, tasks | API Key | ✅ |
| MemoryPlugin | Vector memory | API Key | ✅ |
| Pinecone | Vector database | API Key | ✅ |
| DuckDB | Analytics database | File-based | ✅ |

## Quick Commands

### Health Check
```bash
cd /root/aspen-grove-connectors
python -m aspen_grove health --all
python -m aspen_grove health --connector github
python -m aspen_grove health --connector notion
python -m aspen_grove health --connector supabase
```

### Register Connector
```bash
python -m aspen_grove register --name my-connector --type local
python -m aspen_grove register --name my-connector --type remote --endpoint https://api.example.com
```

### Sync Data
```bash
python -m aspen_grove sync --source notion --target supabase
python -m aspen_grove sync --source github --target notion
python -m aspen_grove sync --source dropbox --target supabase
python -m aspen_grove sync --source clickup --target linear
```

### List Connectors
```bash
python -m aspen_grove list
python -m aspen_grove list --status active
python -m aspen_grove list --type local
```

## Connector Operations

### GitHub Connector
```python
from aspen_grove import GitHubConnector

connector = GitHubConnector(token="...")
repos = connector.get_repos()
issues = connector.get_issues("owner/repo")
prs = connector.get_pull_requests("owner/repo")
commits = connector.get_commits("owner/repo")
```

### Notion Connector
```python
from aspen_grove import NotionConnector

connector = NotionConnector(api_key="...")
pages = connector.search("query")
database = connector.get_database("db_id")
page = connector.get_page("page_id")
connector.create_page("database_id", {"title": "New Page"})
```

### Supabase Connector
```python
from aspen_grove import SupabaseConnector

connector = SupabaseConnector(url="...", key="...")
data = connector.query("table_name", filters={"column": "value"})
connector.insert("table_name", {"column": "value"})
connector.update("table_name", {"column": "new_value"}, match={"id": 1})
connector.delete("table_name", match={"id": 1})
```

### Dropbox Connector
```python
from aspen_grove import DropboxConnector

connector = DropboxConnector(token="...")
files = connector.list_folder("/path")
connector.upload("/local/file", "/remote/path")
connector.download("/remote/path", "/local/file")
connector.share("/path", "email@example.com")
```

### ClickUp Connector
```python
from aspen_grove import ClickUpConnector

connector = ClickUpConnector(api_key="...")
tasks = connector.get_tasks()
connector.create_task({"name": "New Task", "list_id": "123"})
connector.update_task("task_id", {"status": "complete"})
```

### Linear Connector
```python
from aspen_grove import LinearConnector

connector = LinearConnector(api_key="...")
issues = connector.get_issues()
connector.create_issue({"title": "New Issue", "team_id": "123"})
connector.update_issue("issue_id", {"status": "in_progress"})
```

### Pinecone Connector
```python
from aspen_grove import PineconeConnector

connector = PineconeConnector(api_key="...")
index = connector.get_index("my-index")
index.upsert(vectors=[{"id": "1", "values": [...], "metadata": {...}}])
results = index.query(vector=[...], top_k=10)
```

## Integration Patterns

### Notion → Supabase Sync
```python
from aspen_grove import NotionConnector, SupabaseConnector

notion = NotionConnector(api_key="...")
supabase = SupabaseConnector(url="...", key="...")

# Sync database
pages = notion.get_database("db_id")
supabase.upsert("table_name", pages)
```

### GitHub → Linear Issue Sync
```python
from aspen_grove import GitHubConnector, LinearConnector

github = GitHubConnector(token="...")
linear = LinearConnector(api_key="...")

# Sync issues
issues = github.get_issues("owner/repo")
for issue in issues:
    linear.create_issue(title=issue.title, body=issue.body)
```

### Multi-Service Pipeline
```python
from aspen_grove import NotionConnector, GitHubConnector, SupabaseConnector

notion = NotionConnector(api_key="...")
github = GitHubConnector(token="...")
supabase = SupabaseConnector(url="...", key="...")

# Pipeline: Notion → GitHub → Supabase
pages = notion.get_database("db_id")
for page in pages:
    repo = github.create_repo(page.title)
    supabase.insert("projects", {"notion_id": page.id, "github_repo": repo.name})
```

## Health Monitoring

### Health Check Script
```bash
# Check all connectors
python health_check.py

# Check specific connector
python health_check.py --connector github

# Check with verbose output
python health_check.py --verbose

# Export health report
python health_check.py --export health_report.json
```

### Health Status
```json
{
  "connector": "github",
  "status": "healthy",
  "last_check": "2026-08-05T10:00:00Z",
  "response_time": "150ms",
  "uptime": "99.9%",
  "errors": []
}
```

## Foundation Layer

### Registry Seed
```sql
-- registry_seed.sql
INSERT INTO connectors (name, type, status, config)
VALUES ('github', 'remote', 'active', '{"token": "xxx"}');
```

### Route Policies
```json
{
  "policies": [
    {
      "name": "github-to-notion",
      "source": "github",
      "target": "notion",
      "trigger": "on_issue_created"
    }
  ]
}
```

## Integration Points

### With Quantum Nexus
- Vault stores connector credentials
- Memory persists sync history
- MCP server provides tool access

### With Mastermind
- Receipt-backed sync operations
- Identity verification for connectors
- Lane-based parallel sync

### With Brain
- Intelligence from connector data
- Threat detection across services
- Timeline integration

### With Tower of Babel
- Technology selection for connectors
- Evidence states for data quality
- Proof classes for verification
