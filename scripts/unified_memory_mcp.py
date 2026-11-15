#!/usr/bin/env python3
"""Three-layer memory MCP. Credentials come from the environment, never from this file."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import aiohttp
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(Path.home() / ".env", override=False)

mcp = FastMCP("UnifiedMemory")
CACHE_DIR = Path.home() / ".apex_cache"
CACHE_FILE = CACHE_DIR / "memory_hits.json"
MAX_FACT_LENGTH = 1000
SIMILARITY_THRESHOLD = 0.75


def _ensure_cache() -> None:
    CACHE_DIR.mkdir(exist_ok=True)


def _cache_get(key: str) -> str | None:
    if not CACHE_FILE.exists():
        return None
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8")).get(key)
    except (OSError, json.JSONDecodeError):
        return None


def _cache_set(key: str, value: str) -> None:
    _ensure_cache()
    data: dict[str, str] = {}
    if CACHE_FILE.exists():
        try:
            loaded = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data = {str(item_key): str(item_value) for item_key, item_value in loaded.items()}
        except (OSError, json.JSONDecodeError):
            data = {}
    data[key] = value
    CACHE_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    CACHE_FILE.chmod(0o600)


def _qhash(query: str) -> str:
    return hashlib.sha256(query.strip().lower().encode()).hexdigest()


def _dedup(items: list) -> list:
    seen: set[str] = set()
    unique = []
    for item in items:
        if not isinstance(item, dict):
            continue
        text = (item.get("text") or item.get("memory") or "").strip().lower()
        if text and text not in seen:
            seen.add(text)
            unique.append(item)
    return unique


def _mem0_key(account: str) -> str:
    preferred = "MEM0_PRO_API_KEY" if account == "pro" else "MEM0_REG_API_KEY"
    return os.getenv(preferred) or os.getenv("MEM0_API_KEY", "")


@mcp.tool()
async def add_mem0_fact(fact: str, account: str = "pro", user_id: str = "operator") -> str:
    if len(fact) > MAX_FACT_LENGTH:
        fact = fact[:MAX_FACT_LENGTH] + "... (truncated)"
    key = _mem0_key(account)
    if not key:
        return f"Error: Mem0 key missing for account={account}"
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.mem0.ai/v1/memories/",
            json={"messages": [{"role": "user", "content": fact}], "user_id": user_id, "version": "v2"},
            headers={"Authorization": f"Token {key}", "Content-Type": "application/json"},
        ) as response:
            if response.status != 200:
                return f"Error {response.status}: {await response.text()}"
            return json.dumps(await response.json())


@mcp.tool()
async def search_mem0_facts(query: str, account: str = "pro", user_id: str = "operator") -> str:
    cache_key = f"mem0:{account}:{user_id}:{_qhash(query)}"
    cached = _cache_get(cache_key)
    if cached:
        return f"[CACHE HIT] {cached}"
    key = _mem0_key(account)
    if not key:
        return f"Error: Mem0 key missing for account={account}"
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.mem0.ai/v1/memories/search/",
            json={"query": query, "filters": {"user_id": user_id}},
            headers={"Authorization": f"Token {key}", "Content-Type": "application/json"},
        ) as response:
            if response.status != 200:
                return f"Error {response.status}: {await response.text()}"
            data = await response.json()
            if isinstance(data, list):
                data = _dedup(data)
            elif isinstance(data, dict) and "results" in data:
                data["results"] = _dedup(data["results"])
            result = json.dumps(data)
            _cache_set(cache_key, result)
            return result


@mcp.tool()
async def search_supermemory(query: str, container_tag: str = "default") -> str:
    cache_key = f"sm:{container_tag}:{_qhash(query)}"
    cached = _cache_get(cache_key)
    if cached:
        return f"[CACHE HIT] {cached}"
    key = os.getenv("SUPERMEMORY_API_KEY", "")
    if not key:
        return "Error: SUPERMEMORY_API_KEY missing"
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.supermemory.ai/v4/memories/search",
            json={"q": query, "containerTag": container_tag, "limit": 10},
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        ) as response:
            if response.status != 200:
                return f"Error {response.status}: {await response.text()}"
            result = json.dumps(await response.json())
            _cache_set(cache_key, result)
            return result


@mcp.tool()
async def query_pinecone_vector(query: str) -> str:
    cache_key = f"pc:{_qhash(query)}"
    cached = _cache_get(cache_key)
    if cached:
        return f"[CACHE HIT] {cached}"
    pinecone_key = os.getenv("PINECONE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    host = os.getenv("PINECONE_HOST")
    if not (pinecone_key and openai_key and host):
        return "Error: Missing PINECONE_API_KEY, PINECONE_HOST, or OPENAI_API_KEY"
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/embeddings",
            json={"input": [query], "model": "text-embedding-3-small"},
            headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
        ) as response:
            if response.status != 200:
                return f"Embedding error: {await response.text()}"
            vector = (await response.json())["data"][0]["embedding"]
        async with session.post(
            f"https://{host}/query",
            json={"vector": vector, "topK": 4, "includeMetadata": True},
            headers={"Api-Key": pinecone_key, "Content-Type": "application/json"},
        ) as response:
            if response.status != 200:
                return f"Pinecone error: {await response.text()}"
            data = await response.json()
            data["matches"] = [item for item in data.get("matches", []) if item.get("score", 0.0) >= SIMILARITY_THRESHOLD]
            result = json.dumps(data)
            _cache_set(cache_key, result)
            return result


@mcp.tool()
async def semantic_memory_router(query: str, user_id: str = "operator") -> str:
    folded = query.lower()
    if any(token in folded for token in ["evidence", "legal", "precedent", "pdf", "exhibit", "brief", "court"]):
        return await query_pinecone_vector(query)
    if any(token in folded for token in ["repo", "github", "url", "architecture", "project", "doc"]):
        return await search_supermemory(query)
    return await search_mem0_facts(query, account="pro", user_id=user_id)


if __name__ == "__main__":
    transport = "sse" if len(sys.argv) > 1 and sys.argv[1] == "sse" else "stdio"
    mcp.run(transport)
