#!/usr/bin/env python3
"""skill-ops — find the power skill a job needs, then merge skills together."""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path

ROOT = Path("/root/workspace/projects")
DOTFILES = Path("/root/dotfiles")
REPO = Path("/root/workspace/NEXCOM-CVB-APEX-FORTRESS")
ENV_BIN = Path("/root/.env/bin")
CATALOG = ROOT / "mega-skills/power-skills/CATALOG.json"

def load_catalog():
    return json.load(open(CATALOG))

def _by_id(skill):
    for e in load_catalog()["entries"]:
        if e.get("id") == skill:
            return e
    return None

def find(purpose):
    return [e for e in load_catalog()["entries"]
            if purpose.lower() in (e.get("power") or "").lower()
            or purpose.lower() in (e.get("purpose") or "").lower()]

def _resolve(p):
    if not p or str(p).startswith("/"):
        return Path(p)
    if p.startswith("projects/"):
        return ROOT / p[len("projects/"):]
    if p.startswith("dotfiles-"):
        return DOTFILES / p[len("dotfiles-"):]
    if p.startswith("env-bin:"):
        return ENV_BIN / p[len("env-bin:"):]
    if p.startswith("environment:"):
        return ENV_BIN / p[len("environment:"):]
    if p.startswith("NEXCOM-CVB-APEX-FORTRESS/"):
        return REPO / p[len("NEXCOM-CVB-APEX-FORTRESS/"):]
    return ROOT / p

def read_skill(path):
    p = _resolve(path)
    if not p.exists():
        raise SystemExit(f"skill not found: {path} (resolved {p})")
    text = p.read_text(encoding="utf-8")
    meta = {}
    if text.startswith("---\n"):
        parts = text.split("\n---\n", 1)
        head = parts[0]
        body = parts[1] if len(parts) > 1 else ""
        for line in head.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
    else:
        # non-frontmatter file (e.g. a script): use filename stem as name
        body = text
        meta["name"] = p.stem
        meta["version"] = "unknown"
        meta["purpose"] = ""
    return meta, body

def merge(a, b, out):
    aa = _as_path(a)
    bb = _as_path(b)
    ma, ba = read_skill(aa)
    mb, bb2 = read_skill(bb)
    out_name = f"{ma.get('name','skill')} + {mb.get('name','skill')}"
    lines = [
        "---",
        f"name: {out_name}",
        f"version: 0.2.0 (merged from {ma.get('version','0.1') + ' + ' + str(mb.get('version','0.1'))})",
        f"merge_of: [{ma.get('name','skill')} + {mb.get('name','skill')}]",
        f"purpose: {ma.get('purpose','') or mb.get('purpose','')} integration",
        f"metadata: combined from {ma.get('name','') if ma.get('name') else 'skillA'} + {mb.get('name','') if mb.get('name') else 'skillB'}",
        "origin: glaciereq (merged)",
        "related_skills: []",
        "---",
    ]
    combined = []
    seen = set()
    for block in (ba, bb2):
        for raw in block.split("\n\n"):
            m = re.match(r"^(#{1,3})\s+(.*)", raw.lstrip())
            title = m.group(2).strip().lower() if m else ""
            if title and title in seen and len(seen) > 4:
                combined.append(f"_merged from {ma.get('name','A')} (duplicate section)")
                continue
            if title:
                seen.add(title)
            combined.append(raw.strip())
    out_md = "\n\n".join(lines) + "\n"
    out_p = Path(out)
    out_p.mkdir(parents=True, exist_ok=True)
    (out_p / "SKILL.md").write_text(out_md, encoding="utf-8")
    (out_p / "receipt.json").write_text(json.dumps({
        "schema": "glaciereq.skill-merge.receipt.v1", "inputs": [a, b],
        "merged": out_name, "bytes": len(out_md),
        "sha256": hashlib.sha256(out_md.encode()).hexdigest(),
    }, indent=2), encoding="utf-8")
    print(f"MERGED {a} + {b} -> {out}/SKILL.md  ({len(out_md)} B)")

def _as_path(skill):
    for entry in load_catalog()["entries"]:
        if entry.get("id") == skill:
            p = Path(entry.get("path") or skill)
            cand = p / "SKILL.md" if p.is_dir() and (p / "SKILL.md").exists() else p
            return str(cand) if cand.exists() else str(p)
    return skill

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "find"
    if cmd == "find" and len(sys.argv) > 2:
        for e in find(sys.argv[2]):
            print(f"{e['id']:32s} purpose={e.get('purpose','')!r:34s} -> {e.get('path','')}")
    elif cmd == "merge":
        if len(sys.argv) != 5:
            raise SystemExit("usage: skill-ops.py merge A B OUT")
        merge(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        raise SystemExit("usage: skill-ops.py find <purpose> | merge A B OUT")
