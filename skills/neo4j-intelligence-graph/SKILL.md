---
name: neo4j-intelligence-graph
description: "Build and query 5-layer case intelligence graphs in Neo4j. Models actors, evidence, legal strategies, and constitutional violations as interconnected knowledge graphs with RICO predicate mapping."
---

# Neo4j Intelligence Graph Skill

## Overview
Constructs forensic-grade case intelligence as a knowledge graph. Maps actors, evidence chains, legal theories, and constitutional violations as nodes + relationships, enabling cross-case analysis and pattern detection at scale.

## 5-Layer Architecture

```
LAYER 1: ACTORS
├─ Teresa (Actor A) — TRO weaponization
├─ Brower (GAL) — Misconduct/bias
├─ Family Court Judge — Judicial corruption
└─ [Other parties]

LAYER 2: EVIDENCE
├─ Deposition transcripts (FRE 901 authenticated)
├─ Audio files (SHA-256 CoC hashed)
├─ Email records (Gmail forensics)
├─ Document discovery (PDF metadata)
└─ Internet archives (timestamp verified)

LAYER 3: LEGAL THEORIES
├─ 42 USC §1983 — Civil rights violations
├─ 18 USC §241 — Conspiracy against rights
├─ 18 USC §1512 — Evidence tampering
├─ 18 USC §1951 — RICO predicate acts
└─ Constitutional (1st, 4th, 5th, 14th)

LAYER 4: CONSTITUTIONAL VIOLATIONS
├─ Due Process violations (37 identified)
├─ Equal Protection violations (12 identified)
├─ Right to Petition violations (6 identified)
├─ Judicial impartiality violations (8 identified)
└─ Access to courts violations (4 identified)

LAYER 5: RICO STRUCTURE
├─ Enterprise (family court system)
├─ Pattern (2+ predicates)
├─ Predicates (47 identified)
└─ Damages (§1962(c) violations)
```

## Node Types

### Actor
```
(:Actor {
  name: "Teresa",
  role: "Parent",
  designation: "Actor_A",
  violations: ["42-USC-1983", "18-USC-241"],
  predicates: ["Extortion", "Fraud", "Abuse of Process"]
})
```

### Evidence
```
(:Evidence {
  id: "audio_001",
  type: "Audio",
  source: "Deposition",
  date: "2024-07-15",
  coc_hash: "SHA-256:...",
  authenticated: true,
  admissible: true
})
```

### LegalTheory
```
(:LegalTheory {
  code: "42-USC-1983",
  statute: "Civil Rights Act",
  violation_count: 37,
  damages_eligible: true,
  strength: "high"
})
```

### ConstitutionalRight
```
(:ConstitutionalRight {
  amendment: "14th",
  clause: "Due Process",
  violation_count: 37,
  precedent: ["Mathews v. Eldridge", "Greenholtz v. Inmates"]
})
```

### RICOPredicate
```
(:RICOPredicate {
  act: "Wire Fraud (18-USC-1343)",
  pattern: "TRO_Weaponization",
  instances: 12,
  dates: ["2023-04-01", "2023-06-15"],
  evidence_links: [audio_001, email_047, depo_003]
})
```

## Relationship Types

```
(Actor)-[:COMMITS]->(RICOPredicate)
(Evidence)-[:PROVES]->(LegalTheory)
(LegalTheory)-[:VIOLATES]->(ConstitutionalRight)
(Actor)-[:VIOLATES]->(ConstitutionalRight)
(RICOPredicate)-[:SUPPORTS]->(LegalTheory)
(Evidence)-[:AUTHORED_BY]->(Actor)
(Evidence)-[:TIMELINE]->(Evidence)
(ConstitutionalRight)-[:PRECEDENT]->(Case)
```

## Query Patterns

### 1. Actor Timeline
```cypher
MATCH (actor:Actor {name: "Teresa"})-[:VIOLATES]->(right)
MATCH (actor)-[:COMMITS]->(predicate)-[:EVIDENCE]->(evidence)
RETURN evidence.date, evidence.type, predicate.act
ORDER BY evidence.date
```

### 2. Evidence Chain
```cypher
MATCH (e1:Evidence)-[:TIMELINE]->(e2)-[:TIMELINE]->(e3)
WHERE e1.coc_hash IS NOT NULL
RETURN e1, e2, e3
```

### 3. RICO Pattern
```cypher
MATCH (actor:Actor)-[:COMMITS]->(p1:RICOPredicate),
      (actor)-[:COMMITS]->(p2:RICOPredicate)
WHERE p1 <> p2
RETURN actor.name, count(DISTINCT p1, p2) as predicate_count
```

### 4. Constitutional Violation Network
```cypher
MATCH (actor:Actor)-[:VIOLATES]->(right:ConstitutionalRight)
MATCH (right)-[:PRECEDENT]->(case:Case)
MATCH (actor)-[:COMMITS]->(predicate)-[:SUPPORTS]->(theory)
MATCH (theory)-[:VIOLATES]->(right)
RETURN actor, right, case, predicate, theory
```

### 5. Damages Calculation
```cypher
MATCH (actor:Actor)-[:VIOLATES {instances: count}]->(right:ConstitutionalRight)
MATCH (right)-[:DAMAGES_ELIGIBLE {amount: dollars}]->()
RETURN actor.name, sum(count * dollars) as total_damages
```

## Connection Configuration

### Neo4j Aura
```
Connection: <see connections.py> (AuraDB)
Endpoint: https://[aura-instance].neo4j.io/graphql
Method: Cypher queries via HTTP
Auth: Bearer token in env
```

### Local Neo4j (Development)
```
Connection: <see connections.py> (Direct HTTP)
Endpoint: http://localhost:7474 (dev) or Aura (prod)
Method: Transactional HTTP
```

## Schema Export

```json
{
  "nodes": [
    "Actor", "Evidence", "LegalTheory",
    "ConstitutionalRight", "RICOPredicate",
    "Case", "Timeline"
  ],
  "relationships": [
    "COMMITS", "PROVES", "VIOLATES",
    "SUPPORTS", "AUTHORED_BY", "TIMELINE",
    "PRECEDENT", "EVIDENCE", "DAMAGES_ELIGIBLE"
  ],
  "indexes": [
    "Actor(name)", "Evidence(coc_hash)",
    "LegalTheory(code)", "RICOPredicate(act)"
  ]
}
```

## Data Import

### CSV Format
```csv
actor,violation,law,evidence_id,date
Teresa,§1983,42-USC-1983,audio_001,2024-07-15
Brower,Misconduct,Hawaii-RPC,depo_003,2024-08-22
```

### JSON Format
```json
{
  "actors": [...],
  "evidence": [...],
  "relationships": [...],
  "statistics": {
    "total_violations": 67,
    "actors_implicated": 3,
    "evidence_items": 47
  }
}
```

## Analysis Tools

### Centrality Analysis
```cypher
CALL algo.betweenness.stream('Actor', 'VIOLATES')
YIELD nodeId, score
RETURN algo.getNodeById(nodeId).name, score
ORDER BY score DESC
```

### Pattern Detection
```cypher
CALL algo.triangle.stream('Actor', 'COMMITS', 'SUPPORTS')
YIELD nodeA, nodeB, nodeC
RETURN nodeA, nodeB, nodeC
```

## Outputs

- **intelligence_graph.json** — Full schema + data export
- **actor_analysis.md** — Centrality + network position per actor
- **evidence_chain.md** — Chronological evidence linkage
- **legal_strength_report.md** — Violation count + precedent matching
- **rico_analysis.md** — Predicate inventory + damages estimation
- **notion_sync.json** — SUPERLUMINAL_CASE_MATRIX sync format

## Use When
- Building comprehensive case intelligence
- Detecting RICO patterns across actors
- Tracing evidence chains forensically
- Analyzing constitutional violation networks
- Estimating damages for settlement/trial
- Cross-referencing legal theories to evidence
- Supporting expert witness analysis
