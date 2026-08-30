#!/usr/bin/env python3
"""
Credential Resolver
Resolves credentials from environment variables or encrypted keystores with hygiene checks.
"""

import os
import json
import base64
import sys
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass
from cryptography.fernet import Fernet


@dataclass
class Credential:
    name: str
    value: str
    source: str  # "env", "keystore", "default"
    masked: bool = True


SERVICE_CREDENTIAL_MAP = {
    "supabase": ["SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "SUPABASE_URL"],
    "github": ["GITHUB_TOKEN", "GITHUB_PAT", "GITHUB_CLIENT_SECRET"],
    "openrouter": ["OPENROUTER_API_KEY", "OPENROUTER_PRIMARY", "OPENROUTER_SECONDARY"],
    "deepseek": ["DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL"],
    "groq": ["GROQ_API_KEY", "GROQ_SECONDARY"],
    "anthropic": ["ANTHROPIC_API_KEY", "ANTHROPIC_CODE_ASSISTANT"],
    "openai": ["OPENAI_API_KEY", "OPENAI_WINDSURF", "OPENAI_ADMIN"],
    "gemini": ["GEMINI_API_KEY", "GEMINI_GOOGLE_API", "GEMINI_CLIENT_SECRET"],
    "perplexity": ["PERPLEXITY_API_KEY", "PERPLEXITY_SECONDARY"],
    "cohere": ["COHERE_API_KEY"],
    "together_ai": ["TOGETHER_AI_KEY"],
    "supabase_glaciereq": ["SUPABASE_GLACIEREQ_KEY"],
    "firebase": ["FIREBASE_API_KEY"],
    "pinecone": ["PINECONE_API_KEY", "PINECONE_HIGUY_KEY"],
    "neo4j": ["NEO4J_API_KEY"],
    "linear": ["LINEAR_API_KEY"],
    "jira": ["JIRA_API_TOKEN", "JIRA_SITE"],
    "todoist": ["TODOIST_API_TOKEN"],
    "gitlab": ["GITLAB_PAT"],
    "cursor": ["CURSOR_API_KEY"],
    "cody": ["CODY_API_KEY"],
    "warp": ["WARP_PRIMARY", "WARP_SECONDARY"],
    "vercel": ["VERCEL_TOKEN"],
    "render": ["RENDER_PRIMARY", "RENDER_SECONDARY"],
    "railway": ["RAILWAY_API_KEY"],
    "prisma": ["PRISMA_POSTGRES_URL"],
    "slack": ["SLACK_APP_ID", "SLACK_CLIENT_ID", "SLACK_CLIENT_SECRET", "SLACK_SIGNING_SECRET"],
}


def resolve_from_env(var_names: List[str]) -> List[Credential]:
    """Resolve credentials from environment variables."""
    creds = []
    for var in var_names:
        value = os.environ.get(var)
        if value:
            creds.append(Credential(
                name=var,
                value=value,
                source="env",
                masked=True
            ))
    return creds


def resolve_from_keystore(keystore_path: Path, service: str, master_key: str) -> List[Credential]:
    """Resolve credentials from encrypted keystore."""
    creds = []
    if not keystore_path.exists():
        return creds
    
    try:
        cipher = Fernet(base64.urlsafe_b64encode(master_key[:32].encode().ljust(32, b'0')))
        encrypted_data = keystore_path.read_bytes()
        decrypted = cipher.decrypt(encrypted_data).decode()
        data = json.loads(decrypted)
        
        if service in data:
            for key, value in data[service].items():
                creds.append(Credential(
                    name=f"{service}.{key}",
                    value=value,
                    source="keystore",
                    masked=True
                ))
    except Exception:
        pass
    return creds


def validate_credential_hygiene(creds: List[Credential]) -> List[str]:
    """Check for credential hygiene issues."""
    issues = []
    for cred in creds:
        if len(cred.value) < 10:
            issues.append(f"{cred.name}: value too short (<10 chars)")
        if cred.value.startswith(("sk-", "ghp_", "sk_", "pplx-", "gsk_")) and not cred.masked:
            issues.append(f"{cred.name}: exposed secret pattern")
        if "test" in cred.value.lower() and "prod" in cred.name.lower():
            issues.append(f"{cred.name}: test credential in production context")
    return issues


def mask_value(value: str, visible: int = 4) -> str:
    """Mask credential value for display."""
    if len(value) <= visible * 2:
        return "*" * len(value)
    return value[:visible] + "*" * (len(value) - visible * 2) + value[-visible:]


def main():
    if len(sys.argv) < 2:
        print("Usage: credential_resolver.py <service> [--keystore PATH] [--master-key KEY] [--list]")
        print("Services:", ", ".join(sorted(SERVICE_CREDENTIAL_MAP.keys())))
        sys.exit(1)
    
    service = sys.argv[1]
    keystore_path = None
    master_key = None
    list_all = False
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--keystore" and i + 1 < len(sys.argv):
            keystore_path = Path(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--master-key" and i + 1 < len(sys.argv):
            master_key = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--list":
            list_all = True
            i += 1
        else:
            i += 1
    
    if list_all:
        for svc, vars_list in SERVICE_CREDENTIAL_MAP.items():
            print(f"\n{svc}:")
            for v in vars_list:
                val = os.environ.get(v)
                if val:
                    print(f"  {v}: {mask_value(val)} (env)")
        return
    
    if service not in SERVICE_CREDENTIAL_MAP:
        print(f"Unknown service: {service}")
        print("Available:", ", ".join(sorted(SERVICE_CREDENTIAL_MAP.keys())))
        sys.exit(1)
    
    all_creds = []
    
    # Resolve from env
    all_creds.extend(resolve_from_env(SERVICE_CREDENTIAL_MAP[service]))
    
    # Resolve from keystore if provided
    if keystore_path and master_key:
        all_creds.extend(resolve_from_keystore(keystore_path, service, master_key))
    
    # Validate hygiene
    issues = validate_credential_hygiene(all_creds)
    
    # Output
    result = {
        "service": service,
        "credentials_found": len(all_creds),
        "credentials": [
            {
                "name": c.name,
                "source": c.source,
                "masked_value": mask_value(c.value) if c.masked else c.value,
                "length": len(c.value)
            }
            for c in all_creds
        ],
        "hygiene_issues": issues
    }
    
    print(json.dumps(result, indent=2))
    
    if issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
