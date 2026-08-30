---
name: cross-cloud-memory-synthesis
description: 'Combo Skill: Cross Cloud Memory Synthesis. Reusable capability chain.'
---

# Cross Cloud Memory Synthesis

## Purpose and selection

Use this Combo Skill when knowledge across 291k+ multi-cloud documents (Dropbox, ShadowDrive, local estate) must be indexed into subword n-gram vector spaces and reinforced through Hebbian synaptic learning. Do **not** use it for trivial single-file text searches.

## Incremental value

This Combo Skill converts unstructured distributed cloud storage into a deterministic, self-learning vector memory matrix. It adds subword 3-gram term frequency modeling, TF-IDF cosine ranking, and dynamic Hebbian synaptic weight updates.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `mission-contract` | Skill | Yes | Set cloud storage scope and indexing boundaries | Memory mandate | `MISSION.md` | Target paths and decay rates are explicit |
| 2 | `omni-memory-core` | Skill | Yes | Vectorize files, calculate cosine metrics, update synapses | `MISSION.md` and file trees | `omni-memory-index-report.json` | Vector shingles and synaptic updates verified |
| 3 | `quality-gate` | Skill | Yes | Verify embedding integrity and retrieval recall | Index report and queries | Gate record | Zero NaN corruption; retrieval recall verified |

## Ordered execution

1. **Storage boundary — `mission-contract`** consumes search mandates and cloud storage paths, produces `MISSION.md`, and passes when cloud Horizons and learning rate constants are defined.
2. **Vector matrix synthesis — `omni-memory-core`** consumes `MISSION.md`, produces `omni-memory-index-report.json`, and passes when term frequency vectors and associative synapses update cleanly.
3. **Recall verification — `quality-gate`** consumes index reports and benchmark queries, produces a gate record, and passes when retrieval accuracy passes acceptance thresholds.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `mission-contract` | `omni-memory-core` | Cloud Horizon paths, learning rate, decay factor | Vector embeddings and synaptic weight graph | memory owner | Paths and vector hyperparameters are explicit |
| `omni-memory-core` | `quality-gate` | Index report, similarity matrices, recall tests | Verified gate record | quality owner | Zero NaN values and retrieval recall passes threshold |

## Evidence, risks, and state

The Combo must record all document counts, shingle vocabulary sizes, cosine similarity scores, and synaptic update deltas in its evidence register. It must not alter raw cloud files or expose private credentials. Update active state after each index partition.

## Quality gates

The Combo is complete only when all candidate files are vectorized, synaptic weights are monotonically updated, and `cross-cloud-memory-record.md` is emitted.

## Compound output

**Artifact:** `cross-cloud-memory-record.md`

**Ready for Mega Skill integration when:**

1. Subword 3-gram vocabulary and TF-IDF matrices are calculated.
2. Hebbian associative synapses are reinforced.
3. Semantic retrieval queries return accurate document references.
