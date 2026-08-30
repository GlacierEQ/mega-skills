---
name: mega-quantum-nexus
description: Quantum Nexus Skill — Sovereign Intelligence System
domains: [quantum-nexus]
token_profile: Lean
---

# MEGA-QUANTUM-NEXUS

_Ingested from the opencode skill source. Bundled into the Monolith mega-skills catalog._


# Quantum Nexus Skill — Sovereign Intelligence System

## Keywords
`quantum nexus` `vault` `memory` `courtlistener` `mcp server` `sovereign` `intelligence`
`case management` `api keys` `llm providers` `mem0` `pinecone` `supermemory`
`vector database` `1FDV-23-0001009` `due process` `habeas corpus` `fraud evidence`
`judicial misconduct` `hawaii family court` `kekkoa` `glaciereq` `evidence processing`
`court filings` `legal research` `motion drafting` `case law` `statutes` `intelligence fusion`
`api credential management` `secret management` `environment variables` `vault env`
`legal analytics` `court api` `docket search` `opinion search` `judge search`
`citation search` `financial disclosure` `legal basis research` `memory orchestration`
`knowledge persistence` `context retrieval` `multi-source context` `mcp tools`
`tool execution` `service integration` `dropbox` `linear` `vercel` `onedrive`

## Architecture

```
quantum_nexus/
├── core/
│   ├── __init__.py
│   └── vault.py              # QuantumVault — 229+ API keys (ImmutableVault)
├── memory/
│   ├── __init__.py
│   └── orchestrator.py       # Memory orchestrator (Mem0, Pinecone, MemoryPlugin)
├── legal/
│   ├── __init__.py
│   └── courtlistener.py      # CourtListener API integration
├── mcp/
│   ├── __init__.py
│   └── server.py             # 30+ MCP tools unified interface
├── brain/                    # Decision engine, threats, timeline, orchestrator
│   ├── decisions/
│   ├── orchestrator/
│   ├── threats/
│   └── timeline/
├── buckets/                  # Memory buckets (identity, legal, technical, etc.)
├── services/                 # External service integrations
├── run.py                    # CLI interface
├── health-check.sh           # Health check script
└── optimize.sh               # Optimization script
```

## Quick Commands

### System Status
```bash
PYTHONPATH=/root python3 /root/quantum_nexus/run.py status
```

### Memory Operations
```bash
# Store memory with category
PYTHONPATH=/root python3 /root/quantum_nexus/run.py store "memory content" --category legal

# Search memories
PYTHONPATH=/root python3 /root/quantum_nexus/run.py search "query"

# Export all memories
PYTHONPATH=/root python3 /root/quantum_nexus/run.py export
```

### Legal Research
```bash
# Search CourtListener docket entries
PYTHONPATH=/root python3 /root/quantum_nexus/run.py court "motion to dismiss"

# Due process violations
PYTHONPATH=/root python3 /root/quantum_nexus/run.py due-process

# Habeas corpus cases
PYTHONPATH=/root python3 /root/quantum_nexus/run.py habeas

# Research any legal topic
PYTHONPATH=/root python3 /root/quantum_nexus/run.py research "fraud"
PYTHONPATH=/root python3 /root/quantum_nexus/run.py research "due process"
PYTHONPATH=/root python3 /root/quantum_nexus/run.py research "habeas corpus"
PYTHONPATH=/root python3 /root/quantum_nexus/run.py research "RICO"
PYTHONPATH=/root python3 /root/quantum_nexus/run.py research "void ab initio"
```

### Vault Info
```bash
PYTHONPATH=/root python3 /root/quantum_nexus/run.py vault
```

## MCP Server Tools (30+)

### Memory Tools
| Tool | Description | Use Case |
|------|-------------|----------|
| `memory_store` | Store content with category | Persist case knowledge |
| `memory_search` | Search by query/category | Retrieve case facts |
| `memory_export` | Export all memories | Backup knowledge |
| `memory_legal_store` | Store legal-specific memory | Legal research persistence |
| `memory_context` | Get context for query | Multi-source context |

### Legal Tools
| Tool | Description | Use Case |
|------|-------------|----------|
| `courtlistener_search` | Search docket entries | Find case filings |
| `courtlistener_docket` | Get docket details | Case information |
| `courtlistener_entries` | Get docket entries | Filing timeline |
| `courtlistener_opinions` | Search opinions | Case law research |
| `courtlistener_judges` | Get judge info | Judge profiles |
| `courtlistener_citations` | Get citations | Citation network |
| `courtlistener_alerts` | Get alerts | Monitoring |
| `courtlistener_financials` | Financial disclosures | Judicial transparency |
| `legal_research` | Research legal basis | Legal argument support |
| `due_process_cases` | Due process violations | Constitutional claims |
| `habeas_corpus` | Habeas corpus cases | Freedom claims |

### GitHub Tools
| Tool | Description | Use Case |
|------|-------------|----------|
| `github_repos` | List repositories | Code inventory |
| `github_search` | Search GitHub | Find code/issues |
| `github_issues` | Get issues | Issue tracking |
| `github_commits` | Get commits | Change history |

### Notion Tools
| Tool | Description | Use Case |
|------|-------------|----------|
| `notion_search` | Search Notion | Find pages |
| `notion_page` | Get page | Read content |
| `notion_chats` | Get chats database | Communication log |
| `notion_create_page` | Create page | Documentation |

### Supabase Tools
| Tool | Description | Use Case |
|------|-------------|----------|
| `supabase_query` | Query table | Data retrieval |
| `supabase_insert` | Insert row | Data storage |
| `supabase_update` | Update rows | Data modification |

### Service Tools
| Tool | Description | Use Case |
|------|-------------|----------|
| `clickup_tasks` | Get ClickUp tasks | Project management |
| `taskade_workspaces` | Get Taskade workspaces | Task management |
| `elevenlabs_tts` | Text to speech | Audio generation |
| `assemblyai_transcribe` | Transcribe audio | Speech-to-text |

### System Tools
| Tool | Description | Use Case |
|------|-------------|----------|
| `vault_status` | Get vault status | System health |
| `get_context` | Get multi-source context | Intelligence fusion |
| `swarm_status` | Get swarm status | Agent status |

## Vault Categories

### LLM Providers (11)
| Provider | Key Field | Purpose |
|----------|-----------|---------|
| OpenAI | `OPENAI_API_KEY` | GPT models, DALL-E |
| Anthropic | `ANTHROPIC_API_KEY` | Claude models |
| Gemini | `GEMINI_API_KEY` | Google AI |
| DeepSeek | `DEEPSEEK_API_KEY` | DeepSeek models |
| Groq | `GROQ_API_KEY` | Fast inference |
| Cohere | `COHERE_API_KEY` | Embeddings, generation |
| HuggingFace | `HUGGINGFACE_API_KEY` | Open models |
| Nebius | `NEBIUS_API_KEY` | AI infrastructure |
| Together | `TOGETHER_AI_API_KEY` | Open source inference |
| OpenRouter | `OPENROUTER_API_KEY` | Model routing |
| Perplexity | `PERPLEXITY_API_KEY` | Search-augmented AI |

### Memory Providers (4)
| Provider | Key Field | Purpose |
|----------|-----------|---------|
| Mem0 | `MEM0_API_KEY` | Primary memory |
| MemoryPlugin | `MEMORY_PLUGIN_PRIMARY` | Specialized memory |
| Pinecone | `PINECONE_API_KEY` | Vector database |
| SuperMemory | `SUPERMEMORY_KEY` | Long-term memory |

### Working Services
| Service | Status | Purpose |
|---------|--------|---------|
| CourtListener | ✅ | Legal research |
| GitHub | ✅ | Code/evidence |
| Supabase | ✅ | Database |
| Mem0 | ✅ | Memory |
| Pinecone | ✅ | Vectors |
| Notion | ✅ | Documentation |

## Python Usage

### Direct Vault Access
```python
import sys
sys.path.insert(0, '/root')
from quantum_nexus.core.vault import vault

# Get API keys
openai_key = vault.OPENAI_API_KEY
anthropic_key = vault.ANTHROPIC_API_KEY
courtlistener_key = vault.COURTLISTENER_API_KEY

# Get working providers
providers = vault.get_working_providers()

# Get service map
services = vault.get_service_map()

# Get LLM providers
llm_providers = vault.get_llm_providers()

# Get memory providers
memory_providers = vault.get_memory_providers()
```

### MCP Server Integration
```python
import sys
sys.path.insert(0, '/root')
from quantum_nexus.mcp.server import quantum_server

# Execute any tool
result = await quantum_server.memory_store("content", "category")
result = await quantum_server.courtlistener_search("query")
result = await quantum_server.vault_status()
result = await quantum_server.get_context("query")
result = await quantum_server.swarm_status()
```

### CourtListener Direct
```python
import sys
sys.path.insert(0, '/root')
from quantum_nexus.legal.courtlistener import courtlistener

# Search docket entries
results = await courtlistener.search_dockets("due process violation")

# Get docket details
docket = await courtlistener.get_docket(docket_id)

# Get docket entries
entries = await courtlistener.get_docket_entries(docket_id)

# Search opinions
opinions = await courtlistener.search_opinions("habeas corpus")

# Get judges
judges = await courtlistener.get_judges()

# Get citations
citations = await courtlistener.get_citations(cluster_id)

# Financial disclosures
financials = await courtlistener.search_financials("Judge Shaw")

# Legal research
research = await courtlistener.research_legal_basis("void ab initio")

# Due process cases
due_process = await courtlistener.get_due_process_cases()

# Habeas corpus
habeas = await courtlistener.get_habeas_corpus_cases()
```

### Memory Orchestration
```python
import sys
sys.path.insert(0, '/root')
from quantum_nexus.memory.orchestrator import memory

# Store memory
await memory.store(entry)

# Search memories
results = await memory.search("query", category="legal")

# Export all
all_memories = await memory.export_all()

# Get context
context = await memory.get_context("current case status")
```

## Integration Points

### With Legal Powerhouse
- Vault stores legal documents securely
- Memory persists case knowledge
- CourtListener provides case law research
- Evidence chain of custody

### With Aspen Grove
- GitHub connector for repo management
- Notion connector for documentation
- Supabase connector for data storage
- Dropbox for file storage

### With Mastermind
- Receipt-backed operations
- Identity verification for vault access
- Lane-based execution for parallel tasks

### With Brain
- Decision engine integration
- Threat intelligence feeds
- Timeline tracking
- Memory tagging system

### With Tower of Babel
- Technology selection for AI sessions
- Evidence states for data quality
- Proof classes for verification

## Environment

- **Location**: `/root/quantum_nexus/`
- **PYTHONPATH**: Must set `PYTHONPATH=/root` for imports
- **Vault Env**: `/root/.vault_env` (229 API keys)
- **Async**: All operations use `asyncio.run()`
- **Case ID**: `1FDV-23-0001009`
- **Operator**: `GlacierEQ`
- **Mission**: `BRING KEKOA HOME`
