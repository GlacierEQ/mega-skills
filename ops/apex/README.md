# APEX local config

`mcpServers.json` is a template. Secret fields are `${NAME}` placeholders. The canonical names live in `secrets/catalog.json` and `scripts/key_hierarchy.py`.

GitHub's canonical name in this repo is `GH_TOKEN`.

```bash
python3 scripts/apex_key_audit.py --env ~/.env --out "$HOME/key_audit_report.json" --skip-probes
python3 scripts/apex_key_audit.py --env ~/.env --out "$HOME/key_audit_report.json" --write-clean-env
python3 scripts/apex_boot_unified.py
```

The audit prints names, fingerprints, and HTTP status. It refuses to write a cleaned env file or a report into a tracked git path, and it checks the report for secret values before writing it. Do not commit `~/.env`.

`n8n-mcp` runs `ops/apex/n8n_stdio_bridge.py` from the repo root. The bearer token stays in `N8N_API_KEY` and is sent as an HTTP header. It is not a process argument.
