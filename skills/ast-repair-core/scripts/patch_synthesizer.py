#!/usr/bin/env python3
"""
Patch Synthesizer
Generates surgical code replacements via model dispatch based on defect context.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PatchContext:
    """Complete context for patch synthesis."""
    error_type: str
    error_message: str
    failing_code: str
    surrounding_context: str
    ast_chunk: Dict
    test_output: str
    imports: List[str]
    docstring: Optional[str]


@dataclass
class SynthesizedPatch:
    """A synthesized code patch."""
    original_code: str
    replacement_code: str
    explanation: str
    confidence: float
    changes_summary: List[str]


# Model prompt template for surgical patch synthesis
PATCH_SYNTHESIS_PROMPT = """You are an expert code repair engineer. Generate a SURGICAL, MINIMAL patch to fix the defect.

## Defect Context
**Error Type:** {error_type}
**Error Message:** {error_message}

**Failing Code (exact lines):**
```python
{failing_code}
```

**Surrounding Context (±15 lines):**
```python
{surrounding_context}
```

**AST Chunk Info:**
- Node Type: {node_type}
- Name: {name}
- Parent Context: {parent_context}
- Decorators: {decorators}
- Docstring: {docstring}
- Imports Available: {imports}

**Full Test Output:**
```
{test_output}
```

## Requirements
1. Produce a MINIMAL replacement - only change what's necessary to fix the error
2. Preserve all existing functionality, imports, decorators, docstrings
3. Do NOT add stubs, pass statements, or NotImplemented
4. Do NOT modify test files
5. The fix must be syntactically correct and pass the failing test

## Output Format (JSON only)
```json
{{
  "replacement_code": "complete replacement code for the failing chunk",
  "explanation": "1-2 sentences explaining the fix",
  "confidence": 0.0-1.0,
  "changes_summary": ["change 1", "change 2"]
}}
```"""


def build_prompt(context: PatchContext) -> str:
    """Build the model prompt for patch synthesis."""
    return PATCH_SYNTHESIS_PROMPT.format(
        error_type=context.error_type,
        error_message=context.error_message,
        failing_code=context.failing_code,
        surrounding_context=context.surrounding_context,
        node_type=context.ast_chunk.get("node_type", "unknown"),
        name=context.ast_chunk.get("name", "unknown"),
        parent_context=context.ast_chunk.get("parent_context", "module"),
        decorators=context.ast_chunk.get("decorators", []),
        docstring=context.ast_chunk.get("docstring", "none"),
        imports=context.imports,
        test_output=context.test_output[-2000:] if len(context.test_output) > 2000 else context.test_output
    )


def call_synthesis_model(prompt: str) -> Optional[SynthesizedPatch]:
    """Call the synthesis model (OpenRouter, local, etc.) to generate patch."""
    # This is a stub - in production, this would call the actual model
    # For now, return a template patch structure
    return None


def synthesize_patch_locally(context: PatchContext) -> Optional[SynthesizedPatch]:
    """Attempt local synthesis for common patterns (no model call)."""
    error_msg = context.error_message.lower()
    failing = context.failing_code
    
    # Common pattern: IndexError -> bounds check
    if "indexerror" in error_msg or "index out of range" in error_msg:
        if "[" in failing and "]" in failing:
            # Simple heuristic: add bounds check before list access
            return SynthesizedPatch(
                original_code=failing,
                replacement_code=failing + "\n# TODO: Add bounds check",
                explanation="Local synthesis: IndexError detected - add bounds validation",
                confidence=0.3,
                changes_summary=["Add bounds check before list access"]
            )
    
    # Common pattern: AttributeError -> hasattr check
    if "attributeerror" in error_msg:
        return SynthesizedPatch(
            original_code=failing,
            replacement_code=failing + "\n# TODO: Add hasattr check",
            explanation="Local synthesis: AttributeError detected - add attribute existence check",
            confidence=0.3,
            changes_summary=["Add hasattr/try-except for attribute access"]
        )
    
    # Common pattern: KeyError -> dict.get or in check
    if "keyerror" in error_msg:
        return SynthesizedPatch(
            original_code=failing,
            replacement_code=failing + "\n# TODO: Use dict.get() or 'in' check",
            explanation="Local synthesis: KeyError detected - use safe dict access",
            confidence=0.3,
            changes_summary=["Use dict.get() or 'key in dict' check"]
        )
    
    # Common pattern: TypeError -> type check
    if "typeerror" in error_msg:
        return SynthesizedPatch(
            original_code=failing,
            replacement_code=failing + "\n# TODO: Add type validation",
            explanation="Local synthesis: TypeError detected - add type checking",
            confidence=0.3,
            changes_summary=["Add isinstance() or type annotation validation"]
        )
    
    # Common pattern: ZeroDivisionError
    if "zerodivisionerror" in error_msg or "division by zero" in error_msg:
        return SynthesizedPatch(
            original_code=failing,
            replacement_code=failing + "\n# TODO: Add zero check before division",
            explanation="Local synthesis: Division by zero - add denominator validation",
            confidence=0.3,
            changes_summary=["Add zero-check before division"]
        )
    
    return None


def synthesize_patch(context: PatchContext) -> SynthesizedPatch:
    """Main synthesis entry point - tries local first, then model."""
    # Try local synthesis first
    local_patch = synthesize_patch_locally(context)
    if local_patch and local_patch.confidence > 0.5:
        return local_patch
    
    # Try model synthesis
    model_patch = call_synthesis_model(build_prompt(context))
    if model_patch:
        return model_patch
    
    # Fallback: return original with marker
    return SynthesizedPatch(
        original_code=context.failing_code,
        replacement_code=context.failing_code + "\n# REPAIR NEEDED: " + context.error_message,
        explanation=f"Could not synthesize patch for {context.error_type}: {context.error_message}",
        confidence=0.0,
        changes_summary=["Manual repair required"]
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: patch_synthesizer.py <context_json_file> [--model]")
        print("  context_json_file: Output from ast_chunker + traceback_parser")
        sys.exit(1)
    
    context_file = Path(sys.argv[1])
    if not context_file.exists():
        print(f"Context file not found: {context_file}")
        sys.exit(1)
    
    data = json.loads(context_file.read_text())
    
    # Build PatchContext from combined data
    context = PatchContext(
        error_type=data.get("error_type", "UnknownError"),
        error_message=data.get("error_message", ""),
        failing_code=data.get("root_cause", {}).get("code_context", ""),
        surrounding_context=data.get("surrounding_context", ""),
        ast_chunk=data.get("root_cause", {}),
        test_output=data.get("test_output", ""),
        imports=data.get("imports", []),
        docstring=data.get("docstring")
    )
    
    patch = synthesize_patch(context)
    
    print(json.dumps({
        "original_code": patch.original_code,
        "replacement_code": patch.replacement_code,
        "explanation": patch.explanation,
        "confidence": patch.confidence,
        "changes_summary": patch.changes_summary
    }, indent=2))


if __name__ == "__main__":
    main()
