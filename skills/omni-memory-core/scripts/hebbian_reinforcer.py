#!/usr/bin/env python3
"""
Associative synaptic weight updates (w_ij = gamma*w + eta)
Part of omni-memory-core skill.
"""

import argparse
import json
import sys
from pathlib import Path


def update_hebbian_weights(
    weights: dict[str, float],
    active_nodes: list[str],
    gamma_decay: float = 0.98,
    eta_learning_rate: float = 0.1,
    max_weight: float = 1.0,
) -> dict:
    """Update associative synaptic weights using Hebbian learning rule w_ij = gamma*w + eta*a_i*a_j."""
    updated = {}

    # Apply decay to all existing weights
    for pair, w in weights.items():
        updated[pair] = round(w * gamma_decay, 6)

    # Reinforce co-active node pairs
    for i in range(len(active_nodes)):
        for j in range(i + 1, len(active_nodes)):
            n1, n2 = sorted([active_nodes[i], active_nodes[j]])
            pair_key = f"{n1}--{n2}"
            current = updated.get(pair_key, 0.0)
            new_w = min(max_weight, current + eta_learning_rate)
            updated[pair_key] = round(new_w, 6)

    return {
        "total_synapses": len(updated),
        "coactive_nodes": active_nodes,
        "gamma_decay": gamma_decay,
        "eta_learning_rate": eta_learning_rate,
        "weights": updated,
    }


def main():
    parser = argparse.ArgumentParser(description="Hebbian associative synaptic weight reinforcer")
    parser.add_argument("--nodes", nargs="+", default=["memory_a", "memory_b"], help="Active node IDs")
    parser.add_argument("--gamma", type=float, default=0.98, help="Decay factor gamma")
    parser.add_argument("--eta", type=float, default=0.1, help="Learning rate eta")
    args = parser.parse_args()

    initial_weights = {"memory_a--memory_b": 0.5, "memory_a--memory_c": 0.4}
    result = update_hebbian_weights(initial_weights, args.nodes, gamma_decay=args.gamma, eta_learning_rate=args.eta)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

