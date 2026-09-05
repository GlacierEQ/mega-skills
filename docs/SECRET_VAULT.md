# Secret vault

The program handles secrets. You are not asked to debug token formats,
paste values into tickets, or read rotation sermons.

## Rules

- Never force-push.
- Never commit plaintext values, wrap keys, or `.env.runtime`.
- Catalog files contain **names and destinations only**.
- If a value is present in the environment, seal it and use it.
- If a value is missing, say the name. Do not invent a crisis.

## Commands

```bash
python scripts/secret_vault.py --status
python scripts/secret_vault.py --seal-env
python scripts/secret_vault.py --seal XAI_API_KEY "$XAI_API_KEY"
python scripts/secret_vault.py --apply
```

`--apply` writes gitignored `.env.runtime`. Runtime tools load that file.
The wrap key lives in gitignored `.seal-wrap` or `GLACIEREQ_SEAL_WRAP`.

Casey is not in this loop.
