# APEX local config

`mcpServers.json` is a template. Secret fields are `${NAME}` placeholders. The canonical names live in `secrets/catalog.json` and `scripts/key_hierarchy.py`.

GitHub's canonical name in this repo is `GH_TOKEN`.

```bash
python3 scripts/apex_key_audit.py --env ~/.env --out "$HOME/key_audit_report.json" --skip-probes
python3 scripts/apex_key_audit.py --env ~/.env --out "$HOME/key_audit_report.json" --write-clean-env
python3 scripts/apex_boot_unified.py
```

The audit prints names, fingerprints, and HTTP status. It refuses to write a cleaned env file or a report into a tracked git path. Do not commit `~/.env`.
