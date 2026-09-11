#!/usr/bin/env python3
"""
Subword 3-gram TF-IDF vectors across global vocabulary
Part of omni-memory-core skill.
"""

import argparse
import collections
import json
import math
import re
import sys
from pathlib import Path


def extract_3grams(text: str) -> list[str]:
    """Extract character 3-grams from normalized text."""
    normalized = re.sub(r'\s+', ' ', text.lower().strip())
    if len(normalized) < 3:
        return [normalized] if normalized else []
    return [normalized[i:i+3] for i in range(len(normalized) - 2)]


def compute_tf(tokens: list[str]) -> dict[str, float]:
    """Compute normalized term frequencies."""
    if not tokens:
        return {}
    counts = collections.Counter(tokens)
    total = len(tokens)
    return {k: v / total for k, v in counts.items()}


def vectorize_text(text: str, idf_weights: dict[str, float] = None) -> dict:
    """Generate subword 3-gram TF-IDF vector for input text."""
    ngrams = extract_3grams(text)
    tf = compute_tf(ngrams)
    vector = {}
    for gram, freq in tf.items():
        idf = idf_weights.get(gram, 1.0) if idf_weights else 1.0
        vector[gram] = freq * idf

    # L2 normalize
    norm = math.sqrt(sum(v * v for v in vector.values()))
    normalized_vector = {k: v / norm for k, v in vector.items()} if norm > 0 else vector

    return {
        "text_length": len(text),
        "total_3grams": len(ngrams),
        "unique_features": len(normalized_vector),
        "vector": normalized_vector,
    }


def main():
    parser = argparse.ArgumentParser(description="Subword 3-gram TF-IDF vectorizer")
    parser.add_argument("--text", default="Quantum memory indexing and associative recall", help="Input text")
    args = parser.parse_args()

    result = vectorize_text(args.text)
    # Output summary
    summary = {
        "total_3grams": result["total_3grams"],
        "unique_features": result["unique_features"],
        "top_features": sorted(result["vector"].items(), key=lambda x: x[1], reverse=True)[:5],
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

