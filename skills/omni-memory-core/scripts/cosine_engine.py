#!/usr/bin/env python3
"""
TF-IDF weighted cosine similarity against queries
Part of omni-memory-core skill.
"""

import argparse
import json
import math
import sys
from pathlib import Path


def cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """Compute cosine similarity between two sparse feature vectors."""
    if not vec_a or not vec_b:
        return 0.0
    # Intersection of keys
    common_keys = set(vec_a.keys()) & set(vec_b.keys())
    if not common_keys:
        return 0.0
    dot_product = sum(vec_a[k] * vec_b[k] for k in common_keys)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return max(0.0, min(1.0, dot_product / (norm_a * norm_b)))


def rank_documents(query_vec: dict[str, float], documents: dict[str, dict[str, float]], top_k: int = 5) -> list[dict]:
    """Rank documents by cosine similarity against a query vector."""
    scores = []
    for doc_id, doc_vec in documents.items():
        sim = cosine_similarity(query_vec, doc_vec)
        scores.append({"doc_id": doc_id, "score": round(sim, 6)})
    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores[:top_k]


def main():
    parser = argparse.ArgumentParser(description="TF-IDF weighted cosine similarity engine")
    parser.add_argument("--json", help="Optional JSON input with query and doc vectors")
    args = parser.parse_args()

    v1 = {"qua": 0.5, "ant": 0.5, "mem": 0.707}
    v2 = {"qua": 0.5, "ant": 0.5, "rec": 0.707}
    sim = cosine_similarity(v1, v2)

    result = {
        "sample_similarity": round(sim, 4),
        "status": "ready",
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

