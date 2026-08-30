#!/usr/bin/env python3
"""
Fallback Identifier
Identifies safe fallbacks for every non-verified required prerequisite.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class FallbackType(Enum):
    ALTERNATIVE_TOOL = "alternative_tool"
    ALTERNATIVE_VERSION = "alternative_version"
    MOCK_SERVICE = "mock_service"
    CACHED_DATA = "cached_data"
    DEGRADED_MODE = "degraded_mode"
    MANUAL_WORKAROUND = "manual_workaround"
    SKIP_OPTIONAL = "skip_optional"


@dataclass
class Fallback:
    prerequisite_id: str
    fallback_type: FallbackType
    description: str
    implementation: str
    cost: str  # "low", "medium", "high"
    risk: str  # "low", "medium", "high"
    owner: str
    test_command: Optional[str] = None


# Fallback strategies by prerequisite type
FALLBACK_STRATEGIES = {
    "pytest": [
        Fallback("pytest", FallbackType.ALTERNATIVE_TOOL, "Use python -m unittest instead",
                "python -m unittest discover", "low", "low", "dev"),
        Fallback("pytest", FallbackType.ALTERNATIVE_TOOL, "Use nox for test orchestration",
                "nox -s tests", "medium", "low", "dev"),
    ],
    "python": [
        Fallback("python", FallbackType.ALTERNATIVE_VERSION, "Use pyenv to install required version",
                "pyenv install 3.11 && pyenv local 3.11", "medium", "low", "dev"),
        Fallback("python", FallbackType.ALTERNATIVE_TOOL, "Use docker with python image",
                "docker run --rm -v $(pwd):/work python:3.11-slim python -m pytest", "high", "medium", "dev"),
    ],
    "git": [
        Fallback("git", FallbackType.ALTERNATIVE_TOOL, "Use GitHub CLI for basic operations",
                "gh repo view, gh pr list", "low", "medium", "dev"),
    ],
    "openrouter": [
        Fallback("openrouter", FallbackType.ALTERNATIVE_TOOL, "Use local Ollama models",
                "ollama run llama3", "medium", "high", "ops"),
        Fallback("openrouter", FallbackType.MOCK_SERVICE, "Use recorded responses for testing",
                "Load from test fixtures", "low", "low", "dev"),
    ],
    "anthropic": [
        Fallback("anthropic", FallbackType.ALTERNATIVE_TOOL, "Use OpenRouter as proxy",
                "Route via OPENROUTER_API_KEY", "low", "medium", "ops"),
    ],
    "openai": [
        Fallback("openai", FallbackType.ALTERNATIVE_TOOL, "Use OpenRouter as proxy",
                "Route via OPENROUTER_API_KEY", "low", "medium", "ops"),
    ],
    "groq": [
        Fallback("groq", FallbackType.ALTERNATIVE_TOOL, "Use Together AI as alternative",
                "TOGETHER_AI_KEY for fast inference", "low", "medium", "ops"),
    ],
    "supabase": [
        Fallback("supabase", FallbackType.MOCK_SERVICE, "Use SQLite for local development",
                "sqlite3 local.db", "low", "high", "dev"),
    ],
    "oscript": [
        Fallback("osascript", FallbackType.DEGRADED_MODE, "Run in headless mode without GUI",
                "Set HEADLESS=1 env var", "low", "low", "dev"),
    ],
    "screencapture": [
        Fallback("screencapture", FallbackType.DEGRADED_MODE, "Use mock screenshots for testing",
                "Generate placeholder images", "low", "low", "dev"),
    ],
}


DEFAULT_FALLBACKS = [
    Fallback("unknown", FallbackType.MANUAL_WORKAROUND, "Document manual workaround",
             "Document steps in RUNBOOK.md", "high", "high", "dev"),
    Fallback("unknown", FallbackType.SKIP_OPTIONAL, "Skip optional capability",
             "Mark capability as blocked in mission", "low", "low", "pm"),
]


def identify_fallbacks(classifications_file: Path) -> List[Dict]:
    """Identify fallbacks for non-verified prerequisites."""
    data = json.loads(classifications_file.read_text())
    classifications = data.get("classifications", [])
    
    fallbacks = []
    
    for c in classifications:
        prereq_id = c["prerequisite_id"]
        classification = c["classification"]
        
        # Only provide fallbacks for non-verified required items
        if classification in ["missing", "incompatible", "restricted", "expired"]:
            # Try to find specific fallback
            fallback_key = None
            for key in FALLBACK_STRATEGIES:
                if key.lower() in prereq_id.lower():
                    fallback_key = key
                    break
            
            if fallback_key:
                for fb in FALLBACK_STRATEGIES[fallback_key]:
                    fallbacks.append(asdict(fb))
            else:
                # Use default fallbacks
                for fb in DEFAULT_FALLBACKS:
                    fb_copy = Fallback(
                        prerequisite_id=prereq_id,
                        fallback_type=fb.fallback_type,
                        description=fb.description,
                        implementation=fb.implementation,
                        cost=fb.cost,
                        risk=fb.risk,
                        owner=fb.owner,
                        test_command=fb.test_command
                    )
                    fallbacks.append(asdict(fb_copy))
    
    return fallbacks


def main():
    if len(sys.argv) < 2:
        print("Usage: fallback_identifier.py <classifications.json> [--output fallbacks.json]")
        sys.exit(1)
    
    classifications_file = Path(sys.argv[1])
    output_path = Path("fallbacks.json")
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_path = Path(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    
    fallbacks = identify_fallbacks(classifications_file)
    
    # Convert enums
    for fb in fallbacks:
        if hasattr(fb["fallback_type"], "value"):
            fb["fallback_type"] = fb["fallback_type"].value
    
    output_path.write_text(json.dumps({
        "fallbacks": fallbacks,
        "summary": {
            "total": len(fallbacks),
            "by_type": {t.value: len([f for f in fallbacks if f.get("fallback_type") == t.value]) 
                       for t in FallbackType}
        }
    }, indent=2))
    
    print(f"Fallbacks written to {output_path}")


if __name__ == "__main__":
    main()
