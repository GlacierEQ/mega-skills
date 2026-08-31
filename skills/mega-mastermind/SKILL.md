---
name: mega-mastermind
description: "Mastermind Skill — Mission-Control Runtime"
---



# MEGA-MASTERMIND

_Ingested from the opencode skill source. Bundled into the Monolith mega-skills catalog._


# Mastermind Skill — Mission-Control Runtime

## Keywords
`mastermind` `receipt chain` `identity` `agent card` `lane` `execution` `tamper evident`
`audit trail` `hash linked` `sha-256` `mission record` `action record` `authority`
`capability` `pattern matching` `yaml agent card` `strict identity` `permissive mode`
`component authorization` `action restriction` `workflow orchestration` `mission execution`
`receipt export` `ndjson` `chain integrity` `genesis hash` `hash chaining` `immutable audit`
`audit logging` `compliance trails` `provenance` `mission control` `runtime` `spine`
`config` `adapter` `shadow` `test suite` `pytest` `receipt` `mission` `action`
`component` `capability` `restriction` `authority level` `evidence level` `tower floors`
`pattern wildcard` `glob pattern` `action class` `read` `plan` `write_internal`
`succeeded` `failed` `blocked` `canonical hash` `json ready` `utc now`

## Architecture

```
mastermind/
├── runtime/
│   ├── __init__.py
│   ├── spine.py          # MastermindRuntime (core executor)
│   ├── receipt.py        # ReceiptChain (hash-linked audit)
│   ├── identity.py       # IdentityLayer (AgentCard, Authority)
│   ├── lane.py           # Lane management
│   └── config.py         # MastermindConfig
├── adapters/             # Adapter implementations
├── identity/             # Agent card definitions (YAML)
├── lanes/                # Lane configurations
├── shadow/               # Shadow execution
├── tower/                # Tower integration
├── tests/
│   ├── __init__.py
│   └── test_runtime.py   # Test suite
├── __init__.py
└── __main__.py           # CLI entry point
```

## Quick Commands

### Health Check
```bash
cd /root/mastermind && python -m mastermind health
```

### Execute Mission
```bash
cd /root/mastermind && python -m mastermind execute "intent description" \
  --component comp \
  --capability cap \
  --action plan \
  --requested-by cli \
  --metadata '{"key": "value"}'
```

### Verify Receipt Chain
```bash
cd /root/mastermind && python -m mastermind chain
```

### List Receipts
```bash
cd /root/mastermind && python -m mastermind receipts
cd /root/mastermind && python -m mastermind receipts --export receipts.ndjson
```

### List Lanes
```bash
cd /root/mastermind && python -m mastermind lanes
```

### Identity Operations
```bash
# List all identity cards
cd /root/mastermind && python -m mastermind identity list

# Check authority
cd /root/mastermind && python -m mastermind identity check <component> <action>
```

## Receipt Chain

### Tamper-Evident Audit Trail
Each receipt is hash-linked to its predecessor, creating an immutable chain:
```
Genesis (0000...0000) → Receipt 1 → Receipt 2 → Receipt 3
                          ↓            ↓            ↓
                       hash-1       hash-2       hash-3
```

### Receipt Fields
| Field | Type | Description |
|-------|------|-------------|
| `receipt_id` | UUID | Unique identifier |
| `mission_id` | str | Mission reference |
| `action_id` | str | Action reference |
| `component_id` | str | Executing component |
| `lane` | str | Execution lane |
| `action_class` | str | read, plan, write_internal |
| `status` | str | succeeded, failed, blocked |
| `started_at` | str | Start timestamp (ISO) |
| `completed_at` | str | Completion timestamp (ISO) |
| `input_hash` | str | SHA-256 of input |
| `output_hash` | str | SHA-256 of output |
| `evidence_refs` | tuple | Evidence references |
| `error` | str | Error message if failed |
| `previous_hash` | str | Hash of previous receipt |
| `receipt_hash` | str | Hash of this receipt |
| `metadata` | dict | Additional metadata |

### Verify Integrity
```python
import sys
sys.path.insert(0, '/root')
from mastermind.runtime.spine import MastermindRuntime
from mastermind.runtime.config import MastermindConfig

config = MastermindConfig.from_env()
runtime = MastermindRuntime(config)

# Verify chain integrity
valid = runtime.verify_chain()
print(f"Chain valid: {valid}")

# Get receipt count
count = runtime.receipts.count()
print(f"Total receipts: {count}")

# Get last receipt
last = runtime.receipts.last()
print(f"Last receipt: {last.to_dict() if last else 'None'}")
```

### Export Receipts
```python
# Export all receipts to NDJSON
path = runtime.export_receipts("/path/to/receipts.ndjson")
print(f"Exported to: {path}")
```

### Hash Functions
```python
from mastermind.runtime.receipt import _canonical_hash, GENESIS_HASH

# Compute canonical hash
data = {"key": "value"}
hash_value = _canonical_hash(data)
print(f"Hash: {hash_value}")

# Genesis hash (start of chain)
print(f"Genesis: {GENESIS_HASH}")  # 0000...0000 (64 zeros)
```

## Identity Layer

### Agent Cards
Each component has an identity card defining its capabilities and authority:
```python
from mastermind.runtime.identity import AgentCard

card = AgentCard(
    name="component-name",
    version="1.0.0",
    lane="execution",
    capabilities=("read", "write", "execute"),
    authority=("read:*", "write:specific", "execute:approved"),
    restrictions=("write:forbidden", "execute:unauthorized"),
    tower_floors=("PY", "GO", "TS"),
    evidence_level="tested",
    description="Component description"
)
```

### AgentCard Fields
| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Component name |
| `version` | str | Semantic version |
| `lane` | str | Execution lane |
| `capabilities` | tuple | What it can do |
| `authority` | tuple | Allowed actions (patterns) |
| `restrictions` | tuple | Blocked actions (patterns) |
| `tower_floors` | tuple | Associated Tower floors |
| `evidence_level` | str | Evidence quality level |
| `description` | str | Human-readable description |

### Authority Verification
```python
from mastermind.runtime.identity import IdentityLayer

layer = IdentityLayer(strict=True)

# Register card
layer.register(card)

# Verify action
authority = layer.verify("component", "read:data")
print(f"Allowed: {authority.allowed}")
print(f"Reason: {authority.reason}")
print(f"Evidence: {authority.evidence_level}")

# Quick check
can_execute = layer.can_execute("component", "write:data")
print(f"Can execute: {can_execute}")
```

### Pattern Matching Rules
| Pattern | Matches |
|---------|---------|
| `*` | Anything |
| `read:*` | All read actions |
| `read:specific` | Exact action only |
| `write:data*` | Actions starting with "data" |
| `execute:approved` | Exact match |

### Load Cards from Directory
```python
from mastermind.runtime.identity import IdentityLayer

layer = IdentityLayer(strict=True)

# Load all YAML cards from directory
count = layer.load_from_directory("/root/mastermind/identity")
print(f"Loaded {count} agent cards")

# List all capabilities
caps = layer.get_capabilities()
print(f"Capabilities: {caps}")

# Find components with capability
components = layer.get_components_with_capability("read")
print(f"Components with 'read': {components}")
```

## Lanes

### Lane Management
```python
# List lanes
lanes = runtime.lanes.list_names()
print(f"Lanes: {lanes}")

# Execute in specific lane
receipt = await runtime.execute(mission)
```

## Python Usage

### Direct Runtime Access
```python
import sys
sys.path.insert(0, '/root')
from mastermind.runtime.spine import MastermindRuntime
from mastermind.runtime.config import MastermindConfig
from mastermind.runtime.receipt import MissionRecord

config = MastermindConfig.from_env()
runtime = MastermindRuntime(config)

# Check health
health = runtime.health()
print(health)

# Execute mission
mission = MissionRecord(
    intent="process data",
    requested_by="agent",
    action_class="plan",
    target_component="data-processor",
    required_capability="transform"
)
receipt = await runtime.execute(mission)
print(receipt.to_dict())

# Verify chain
valid = runtime.verify_chain()
print(f"Chain valid: {valid}")

# Export receipts
runtime.export_receipts("/path/to/receipts.ndjson")
```

### MissionRecord Fields
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `intent` | str | required | What to accomplish |
| `requested_by` | str | required | Who requested |
| `action_class` | str | "plan" | read, plan, write_internal |
| `mission_id` | UUID | auto | Unique identifier |
| `target_component` | str | None | Target component |
| `required_capability` | str | None | Required capability |
| `metadata` | dict | {} | Additional data |

### ActionRecord Fields
| Field | Type | Description |
|-------|------|-------------|
| `status` | str | succeeded, failed, blocked |
| `output` | Any | Result data |
| `error` | str | Error message |
| `evidence_refs` | tuple | Evidence references |
| `metadata` | dict | Additional data |

## Configuration

### MastermindConfig
```python
from mastermind.runtime.config import MastermindConfig

config = MastermindConfig.from_env()
```

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `MASTERMIND_STRICT_IDENTITY` | `true` | Enable strict identity |
| `MASTERMIND_LANE_DEFAULT` | `default` | Default lane name |
| `MASTERMIND_RECEIPT_EXPORT_PATH` | `/tmp/receipts` | Export path |

## Testing

### Run Tests
```bash
cd /root/mastermind && python -m pytest tests/ -v
```

### Test Coverage
- `test_runtime.py` — Runtime execution tests
- Config, receipts, identity, lanes coverage

## Integration Points

### With Quantum Nexus
- Receipt-backed memory operations
- Identity verification for vault access
- Lane-based execution for parallel tasks

### With Tower of Babel
- Tower floors in AgentCard
- Evidence levels aligned with Tower registry
- Technology selection integration

### With Aspen Grove
- Receipt-backed connector operations
- Identity for connector authorization
- Lane-based parallel sync

### With Brain
- Decision engine receipt tracking
- Threat intel audit trails
- Timeline event receipts
