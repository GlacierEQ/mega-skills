#!/usr/bin/env python3
"""Pick the strongest usable key name per service family. Names only."""

from __future__ import annotations

import json
from typing import Any


FAMILIES: dict[str, dict[str, Any]] = {
    "github": {
        "env": "GH_TOKEN",
        "use": "github",
        "method": "pat-or-app-token",
        "aliases": [
            "GITHUB_TOKEN",
            "GITHUB_TOKEN_PRIMARY",
            "GITHUB_PRIMARY_TOKEN",
            "GITHUB_MASTER_TOKEN",
            "GITHUB_MASTER_PAT",
            "GITHUB_PAT",
            "GITHUB_CLASSIC_PAT",
            "GITHUB_PAT_ALT",
            "GITHUB_TOKEN_ALT",
            "GITHUB_TOKEN_ALT1",
            "GITHUB_TOKEN_ALT2",
            "GITHUB_TOKEN_SECONDARY",
            "GITHUB_PAT_CLASSIC",
            "GITHUB_PAT_MASTER_ALT",
        ],
    },
    "vercel": {
        "env": "VERCEL_TOKEN",
        "use": "vercel",
        "method": "account-token",
        "aliases": ["VERCEL_TOKEN", "VERCEL_API_KEY"],
    },
    "buildkite": {
        "env": "BUILDKITE_API_TOKEN",
        "use": "buildkite",
        "method": "api-token",
        "aliases": ["BUILDKITE_API_TOKEN", "BUILDKITE_TOKEN"],
    },
    "xai": {
        "env": "XAI_API_KEY",
        "use": "runtime",
        "method": "api-key",
        "aliases": ["XAI_API_KEY", "XAI_TOKEN", "XAI_MANAGEMENT_KEY"],
    },
    "openai": {
        "env": "OPENAI_API_KEY",
        "use": "runtime",
        "method": "api-key",
        "aliases": ["OPENAI_API_KEY", "OPENAI_ADMIN_KEY", "OPENAI_WINDSURF_KEY"],
    },
    "anthropic": {
        "env": "ANTHROPIC_API_KEY",
        "use": "runtime",
        "method": "api-key",
        "aliases": ["ANTHROPIC_API_KEY", "ANTHROPIC_CLAUDE_CODE_KEY", "CLAUDE_CODE_TOKEN"],
    },
    "aws_access": {
        "env": "AWS_ACCESS_KEY_ID",
        "use": "runtime",
        "method": "iam-access-key",
        "aliases": ["AWS_ACCESS_KEY_ID"],
    },
    "aws_secret": {
        "env": "AWS_SECRET_ACCESS_KEY",
        "use": "runtime",
        "method": "iam-secret",
        "aliases": ["AWS_SECRET_ACCESS_KEY"],
    },
    "supabase_mgmt": {
        "env": "SUPABASE_ACCESS_TOKEN",
        "use": "supabase",
        "method": "mgmt-pat",
        "aliases": ["SUPABASE_ACCESS_TOKEN", "SUPABASE_PAT"],
    },
    "supabase_service": {
        "env": "SUPABASE_SERVICE_ROLE_KEY",
        "use": "supabase",
        "method": "service-role",
        "aliases": ["SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SERVICE_KEY", "SUPABASE_SECRET"],
    },
    "notion": {
        "env": "NOTION_TOKEN",
        "use": "notion",
        "method": "integration-token",
        "aliases": ["NOTION_TOKEN", "NOTION_API_KEY", "NOTION_API_TOKEN"],
    },
    "stripe": {
        "env": "STRIPE_SECRET_KEY",
        "use": "stripe",
        "method": "secret-key",
        "aliases": ["STRIPE_SECRET_KEY", "STRIPE_SEC"],
    },
    "netlify": {
        "env": "NETLIFY_TOKEN",
        "use": "netlify",
        "method": "personal-token",
        "aliases": ["NETLIFY_TOKEN", "NETLIFY_API_KEY", "NETLIFY_TOKEN_ALT"],
    },
    "groq": {
        "env": "GROQ_API_KEY",
        "use": "runtime",
        "method": "api-key",
        "aliases": ["GROQ_API_KEY", "GROQ_SECONDARY_KEY", "GROQ_TERTIARY_KEY", "GROQ_TABLET_KEY"],
    },
    "deepseek": {
        "env": "DEEPSEEK_API_KEY",
        "use": "runtime",
        "method": "api-key",
        "aliases": ["DEEPSEEK_API_KEY", "DEEPSEEK_PRIMARY_KEY", "DEEPSEEK_SECONDARY_KEY", "DEEPSEEK_TERTIARY_KEY"],
    },
    "perplexity": {
        "env": "PERPLEXITY_API_KEY",
        "use": "runtime",
        "method": "api-key",
        "aliases": ["PERPLEXITY_API_KEY", "PERPLEXITY_PRIMARY_KEY", "PERPLEXITY_SECONDARY_KEY"],
    },
    "gemini": {
        "env": "GEMINI_API_KEY",
        "use": "runtime",
        "method": "api-key",
        "aliases": ["GEMINI_API_KEY", "GEMINI_API_KEY_ALT", "GOOGLE_API_KEY"],
    },
    "cloudflare": {
        "env": "CLOUDFLARE_API_TOKEN",
        "use": "cloudflare",
        "method": "api-token",
        "aliases": ["CLOUDFLARE_API_TOKEN", "CLOUDFLARE_TOKEN", "CLOUDFLARE_TOKEN_ALT"],
    },
    "mem0": {
        "env": "MEM0_API_KEY",
        "use": "memory",
        "method": "api-key",
        "aliases": ["MEM0_API_KEY", "MEM0_KEY", "MEM0_PRO_API_KEY", "MEM0_REG_API_KEY"],
    },
    "pinecone": {
        "env": "PINECONE_API_KEY",
        "use": "memory",
        "method": "api-key",
        "aliases": ["PINECONE_API_KEY", "PINECONE_PRIMARY_KEY"],
    },
    "supermemory": {
        "env": "SUPERMEMORY_API_KEY",
        "use": "memory",
        "method": "api-key",
        "aliases": ["SUPERMEMORY_API_KEY", "SUPERMEMORY_API_KEY_ALT"],
    },
    "memoryplugin": {
        "env": "MEMORY_PLUGIN_TOKEN",
        "use": "memory",
        "method": "token",
        "aliases": ["MEMORY_PLUGIN_TOKEN", "MEMORY_PLUGIN_DIRECT_KEY"],
    },
    "taskade": {
        "env": "TASKADE_API_KEY",
        "use": "taskade",
        "method": "api-key",
        "aliases": ["TASKADE_API_KEY", "TASKADE_API_KEY_ALT"],
    },
    "n8n": {
        "env": "N8N_API_KEY",
        "use": "n8n",
        "method": "api-key",
        "aliases": ["N8N_API_KEY", "N8N_MCP_BEARER"],
    },
}


def pick_winner(family: str, present: set[str]) -> str | None:
    spec = FAMILIES[family]
    for name in spec["aliases"]:
        if name in present:
            return name
    return None


def catalog_bindings() -> dict[str, dict[str, str]]:
    out = {}
    for spec in FAMILIES.values():
        out[spec["env"]] = {"use": spec["use"], "env": spec["env"], "method": spec["method"]}
    return out
