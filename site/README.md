# Mega-Skills Site

This directory contains the self-contained public-facing architecture site for GlacierEQ Mega-Skills.

## Purpose

Explain the Mega-Skills capability hierarchy and operating model without exposing private repository implementation details.

The site presents:

- Skills → Combo Skills → Mega Skills
- the Snowball Rule
- long-horizon mission execution and handoff
- inspectability and evidence registers
- capability readiness / claim discipline
- representative Mega mission-system patterns
- source-preservation and provenance invariants
- the contrast between ad-hoc prompt piles and a durable capability control plane

## Source basis

The copy and architecture are derived from the current repository contracts and documentation, especially:

- `README.md`
- `HIERARCHY.md`
- `docs/END_TO_END_MEGA_SKILLS.md`
- `docs/CAPABILITY_READINESS.md`

The site intentionally avoids unsupported counts, performance metrics, customer claims, and private repository URLs.

## Build

No build toolchain is required. `index.html` is self-contained HTML/CSS and can be served by any static host.

Example local preview:

```bash
python -m http.server 8080 --directory site
```

## Current status

- Source page: `site/index.html`
- Responsive layout: included
- Reduced-motion handling: included
- Sticky anchor navigation: included
- SEO title and description: included
- External images/fonts/scripts: none required
- Publication: not automatically enabled by this directory
