# Mega-Skills Site — Canonical Release Status

**Phase:** RECONCILE_BUILD  
**Canonical repository:** `GlacierEQ/mega-skills`  
**Canonical site:** `site/index.html`  
**Canonical branch:** `main`

## Reconciled state

- One canonical site tree exists: `site/`.
- The prior visual-builder project `05cd1942-ed7c-4d04-9c38-7dd325b0282b` is **non-canonical** and partial.
- Its continuation is blocked because the Lovable connector authorization lacks the `projects:write` scope.
- The committed static page is self-contained and does not require the Lovable project to render or deploy.
- No second repository or parallel knowledge base is created for this site.

## Verified source receipt

- Git blob SHA: `8055675e83cde574e86558ec65aecda14e516dd5`
- SHA-256: `182cb2ad1bc64009cfc19ff26a335f4b138b3a03708c091cda390cfb0f02bf65`
- Size: `27,380 bytes`

Runtime validation confirmed:
- every internal anchor resolves;
- title and description metadata exist;
- all required architecture sections exist;
- reduced-motion handling is present;
- the page is self-contained;
- the private repository URL is not embedded in the public page.

## Repository-native validation

Run:

```bash
python scripts/validate_site.py
```

The validator fails closed when required sections, anchor targets, claim-discipline content, reduced-motion support, or self-contained asset rules regress.

## Deployment path

`.github/workflows/mega-skills-site.yml` is the canonical publication path.

It performs:

1. repository checkout;
2. deterministic static-site validation;
3. GitHub Pages configuration;
4. upload of `site/` as the Pages artifact;
5. GitHub Pages deployment.

### Completion test

Publication is complete only when the workflow's **Validate static site** job passes and the **Deploy GitHub Pages** job returns a provider-side Pages URL.

## Current external blocker

The currently exposed Code Mode tool surface does not provide callable Netlify or Vercel deployment operations. That prevents an independent provider deployment from this turn. This does **not** block repository-native Pages deployment, which is now encoded in GitHub Actions and will produce its own provider-side receipt or exact failure reason.
