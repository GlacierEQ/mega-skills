---
name: mermicorn-mega-boot
description: "Operating inside Mermicorn Mega Boot at /root/mermicorn-mega-boot. Use to scaffold a new Mermicorn-compliant project (the boot pattern that produces a leaf for the Mermicorn Grove)."
---



# Mermicorn Mega Boot

The scaffold that produces a new Mermicorn-compliant project. Running
Mega Boot on a new directory produces a leaf ready to be registered in
the Mermicorn Grove.

**See:**
- `@/root/.agents/skills/mermicorn-grove/SKILL.md` — where the leaf lands
- `@/root/.agents/skills/clean-code/SKILL.md` — code style the scaffold follows
- `@/root/.agents/skills/codemaster/SKILL.md` — coding workflow

## Quick rules

- **Test command:** `cd /root/mermicorn-mega-boot && python -m pytest tests/ -v`
- **Entry point:** the boot CLI; check its README.
- **Scaffolded projects must register in the Grove** after creation, or
  they're orphans.
- **The scaffold enforces APEX doctrine** — receipt chains, identity
  gating, lane routing. Don't strip them.

## Sharp edges

- Don't run Mega Boot on an existing project; it overwrites structure.
  Use a fresh directory.
- The scaffold is opinionated. Customizing it is fine; gutting the
  receipt chain or identity gate is not.
- If the scaffold produces an error, the receipt is the first place
  to look. The boot has its own audit log.
