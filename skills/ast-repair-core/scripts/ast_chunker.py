#!/usr/bin/env python3
"""
AST Chunker - ApexEpistemicChunker
Extracts the exact AST node enclosing a defect line with full context.
"""

import ast
import sys
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
from dataclasses import dataclass


@dataclass
class CodeChunk:
    """Represents an extracted AST chunk with full context."""
    node_type: str          # FunctionDef, ClassDef, AsyncFunctionDef, etc.
    name: str               # Function/class name
    file_path: str
    start_line: int
    end_line: int
    source: str             # Full source code of the chunk
    parent_context: str     # Surrounding context (class, module)
    imports: List[str]      # Relevant imports for this chunk
    decorators: List[str]   # Decorators on the node
    docstring: Optional[str]


def get_node_source(source_lines: List[str], node: ast.AST) -> str:
    """Extract source code for an AST node."""
    start = node.lineno - 1
    end = getattr(node, 'end_lineno', node.lineno)
    return "\n".join(source_lines[start:end])


def get_imports_for_node(tree: ast.AST, target_node: ast.AST) -> List[str]:
    """Get imports relevant to a specific node."""
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            # Check if this import is used in or before target_node
            for alias in node.names:
                imports.append(f"{node.__class__.__name__}: {alias.name}")
    return imports


def find_enclosing_node(tree: ast.AST, target_line: int) -> Optional[ast.AST]:
    """Find the smallest AST node that encloses the target line."""
    candidates = []
    
    for node in ast.walk(tree):
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            if node.lineno <= target_line <= node.end_lineno:
                # Only consider substantive nodes
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, 
                                     ast.ClassDef, ast.Try, ast.With,
                                     ast.For, ast.While, ast.If,
                                     ast.Expr, ast.Assign)):
                    candidates.append(node)
    
    if not candidates:
        return None
    
    # Return the smallest (most specific) enclosing node
    return min(candidates, key=lambda n: (n.end_lineno - n.lineno))


def extract_chunk(file_path: Path, target_line: int, context_lines: int = 10) -> Optional[CodeChunk]:
    """Extract the AST chunk enclosing the target line."""
    try:
        source = file_path.read_text(encoding="utf-8")
        source_lines = source.splitlines()
        tree = ast.parse(source)
    except SyntaxError as e:
        return None
    except Exception:
        return None
    
    # Find enclosing node
    node = find_enclosing_node(tree, target_line)
    if not node:
        # Fallback: return context around the line
        start = max(0, target_line - context_lines - 1)
        end = min(len(source_lines), target_line + context_lines)
        return CodeChunk(
            node_type="fallback_context",
            name=f"lines_{start+1}-{end}",
            file_path=str(file_path),
            start_line=start + 1,
            end_line=end,
            source="\n".join(source_lines[start:end]),
            parent_context="module",
            imports=[],
            decorators=[],
            docstring=None
        )
    
    # Extract chunk details
    chunk_source = get_node_source(source_lines, node)
    
    # Get parent context
    parent_context = "module"
    for parent in ast.iter_child_nodes(tree):
        for child in ast.walk(parent):
            if child is node:
                if isinstance(parent, ast.ClassDef):
                    parent_context = f"class {parent.name}"
                elif isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    parent_context = f"function {parent.name}"
                break
    
    # Get decorators
    decorators = []
    if hasattr(node, 'decorator_list'):
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(f"{ast.unparse(dec)}")
    
    # Get docstring
    docstring = ast.get_docstring(node)
    
    # Get relevant imports
    imports = get_imports_for_node(tree, node)
    
    return CodeChunk(
        node_type=node.__class__.__name__,
        name=getattr(node, 'name', 'anonymous'),
        file_path=str(file_path),
        start_line=node.lineno,
        end_line=getattr(node, 'end_lineno', node.lineno),
        source=chunk_source,
        parent_context=parent_context,
        imports=imports,
        decorators=decorators,
        docstring=docstring
    )


def extract_surrounding_context(file_path: Path, target_line: int, radius: int = 15) -> str:
    """Extract surrounding context for the target line."""
    try:
        source = file_path.read_text(encoding="utf-8")
        lines = source.splitlines()
        start = max(0, target_line - radius - 1)
        end = min(len(lines), target_line + radius)
        
        context_lines = []
        for i in range(start, end):
            marker = ">>> " if i == target_line - 1 else "    "
            context_lines.append(f"{marker}{i+1:4d}: {lines[i]}")
        return "\n".join(context_lines)
    except Exception:
        return ""


def main():
    if len(sys.argv) < 3:
        print("Usage: ast_chunker.py <file_path> <line_number> [--context N]")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    target_line = int(sys.argv[2])
    context = 15
    
    if "--context" in sys.argv:
        idx = sys.argv.index("--context")
        if idx + 1 < len(sys.argv):
            context = int(sys.argv[idx + 1])
    
    chunk = extract_chunk(file_path, target_line)
    
    if chunk:
        result = {
            "node_type": chunk.node_type,
            "name": chunk.name,
            "file_path": chunk.file_path,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "parent_context": chunk.parent_context,
            "decorators": chunk.decorators,
            "docstring": chunk.docstring,
            "imports": chunk.imports,
            "source": chunk.source,
            "surrounding_context": extract_surrounding_context(file_path, target_line, context)
        }
        print(json.dumps(result, indent=2))
    else:
        print("Failed to extract chunk")
        sys.exit(1)


if __name__ == "__main__":
    import json
    main()
