---
name: omni-memory-core
description: "291k-File cross-cloud vector indexing, subword n-gram TF-IDF cosine metrics, and dynamic Hebbian synaptic weight reinforcement."
---


# Omni Memory Core

## Purpose

Index, vectorize, and semantically retrieve knowledge across 291k+ multi-cloud files (Dropbox, ShadowDrive, local storage), dynamically reinforcing associative synapses across operational sprints.

## Procedure

1. Traverse designated file trees and parse multi-modal document contents.
2. Construct subword 3-gram term frequency vectors ($\mathbf{v}_d$) across the global vocabulary.
3. Compute TF-IDF weighted cosine similarity metrics against search queries.
4. Reinforce associative synaptic weights ($w_{ij}^{(t+1)} = \gamma w_{ij}^{(t)} + \eta$) for co-retrieved entities.
5. Export updated vector embeddings and graph associations to local SQLite/Qdrant memory storage.

## Output contract

Produce `omni-memory-index-report.json` with vector shingle counts, cosine similarity scores, updated synaptic weights, and retrieval paths.

## Local validation

The procedure passes only when cosine similarity calculations match deterministic mathematical vectors and synaptic weights update monotonically without NaN corruption.

## Non-goals

Do not store unencrypted sensitive credentials in index vectors. Do not overwrite immutable source document bytes.
