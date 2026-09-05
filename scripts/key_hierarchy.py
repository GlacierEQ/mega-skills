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
            "GITHUB_TOKEN_SECONDARY",
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
        "aliases": ["NETLIFY_TOKEN", "NETLIFY_API_KEY"],
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
