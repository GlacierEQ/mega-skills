---
name: primordial-mesh
description: Operating inside the Primordial Mesh Titan at /root/projects/PRIMORDIAL-MESH-TITAN.
  Distributed context, polymorphic mesh architecture, zenith capsule. Use when working
  on the mesh layer that sits beneath all other Mermicorn/GlacierEQ projects.
version: 0.1.0
---

# Primordial Mesh Titan

The mesh layer beneath Mermicorn/GlacierEQ. Distributed context, polymorphic
mesh architecture, and the zenith capsule. This is the substrate — other
projects consume the mesh but the mesh doesn't consume them.

**See:**
- `@/root/.agents/skills/apex-sovereign-runtime/SKILL.md` — runtime doctrine
- `@/root/.agents/skills/mermicorn-grove/SKILL.md` — what sits above the mesh
- `@/root/.agents/skills/clean-code/SKILL.md` — code style
- `@/root/.agents/skills/codemaster/SKILL.md` — coding workflow

## Quick rules

- **Test command:** `cd /root/projects/PRIMORDIAL-MESH-TITAN && python -m pytest tests/ -v` (verify per repo)
- **The mesh is a substrate.** Don't import downstream projects; downstream imports the mesh.
- **Zenith capsule is the highest-resolution context store.** Other projects
  read from it; this project doesn't push to it on their behalf.

## Sharp edges

- The mesh is the lowest layer. Anything that imports the mesh is fine;
  anything the mesh imports is suspect.
- Schema changes are migrations, not edits. Use the mesh's migration tool.
- Distributed context is a contract, not a cache. Treat it as a system of
  record for shared state.
