#!/usr/bin/env python3
"""
Export embeddings + graph to SQLite/Qdrant
Part of omni-memory-core skill.
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path


def export_to_sqlite(db_path: Path, nodes: list[dict], edges: list[dict] = None) -> dict:
    """Export memory nodes and graph edges into SQLite tables."""
    db_file = db_path.resolve()
    db_file.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS memory_nodes (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            vector_json TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS memory_edges (
            source_id TEXT,
            target_id TEXT,
            weight REAL DEFAULT 1.0,
            PRIMARY KEY (source_id, target_id)
        )
    """)

    for node in nodes:
        cur.execute(
            "INSERT OR REPLACE INTO memory_nodes (id, text, vector_json) VALUES (?, ?, ?)",
            (node.get("id"), node.get("text", ""), json.dumps(node.get("vector", {}))),
        )

    for edge in (edges or []):
        cur.execute(
            "INSERT OR REPLACE INTO memory_edges (source_id, target_id, weight) VALUES (?, ?, ?)",
            (edge.get("source"), edge.get("target"), edge.get("weight", 1.0)),
        )

    conn.commit()
    conn.close()

    return {
        "db_path": str(db_file),
        "nodes_exported": len(nodes),
        "edges_exported": len(edges or []),
        "status": "success",
    }


def main():
    parser = argparse.ArgumentParser(description="Export memory graph to SQLite")
    parser.add_argument("--db", type=Path, default=Path("/tmp/omni_memory.db"), help="Output SQLite database path")
    args = parser.parse_args()

    sample_nodes = [
        {"id": "node-1", "text": "Quantum memory architecture", "vector": {"qua": 0.7, "mem": 0.7}},
        {"id": "node-2", "text": "Associative retrieval matrix", "vector": {"ass": 0.7, "rec": 0.7}},
    ]
    sample_edges = [{"source": "node-1", "target": "node-2", "weight": 0.85}]

    result = export_to_sqlite(args.db, sample_nodes, sample_edges)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

