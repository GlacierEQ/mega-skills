---
id: vercel-fullstack-deployment
display_name: Vercel Fullstack Deployment
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: active
---

# Vercel Fullstack Deployment

## Purpose and selection

Next.js applications, Turbopack bundling, and edge function deployments to Vercel are needed.

## Incremental value

This Combo Skill composes nextjs-ecosystem, turbopack, vercel-platform-ops into a unified, verified `VERCEL_DEPLOYMENT_MANIFEST.md`.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `nextjs-ecosystem` | skill | Yes | Compile Next.js server components and layout routing. | Workspace source, Route layout | nextjs-build-manifest.json | App router tree validates without cyclic links. |
| 2 | `turbopack` | skill | Yes | Execute high-speed incremental bundler compilation. | nextjs-build-manifest.json | turbopack-bundle-receipt.json | Incremental bundle produces zero compilation warnings. |
| 3 | `vercel-platform-ops` | skill | Yes | Orchestrate zero-downtime edge deployment and preview verification. | turbopack-bundle-receipt.json | VERCEL_DEPLOYMENT_MANIFEST.md | Deployment manifest verifies edge functions and routes. |

## Ordered execution

1. **nextjs-ecosystem** consumes Workspace source, Route layout, produces nextjs-build-manifest.json, and verifies App router tree validates without cyclic links..
2. **turbopack** consumes nextjs-build-manifest.json, produces turbopack-bundle-receipt.json, and verifies Incremental bundle produces zero compilation warnings..
3. **vercel-platform-ops** consumes turbopack-bundle-receipt.json, produces VERCEL_DEPLOYMENT_MANIFEST.md, and verifies Deployment manifest verifies edge functions and routes..

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `nextjs-ecosystem` | `turbopack` | nextjs-build-manifest.json | turbopack-bundle-receipt.json | `nextjs-ecosystem` | Verified handoff |
| `turbopack` | `vercel-platform-ops` | turbopack-bundle-receipt.json | VERCEL_DEPLOYMENT_MANIFEST.md | `turbopack` | Verified handoff |

## Compound output

Produce `VERCEL_DEPLOYMENT_MANIFEST.md` upon completion.
