# Key hierarchy

One wrap. One named vault. One winner per service. Values never live in git
or in chat.

## Layers

| Layer | What | Who holds it | Method |
|---|---|---|---|
| L0 wrap | `GLACIEREQ_SEAL_WRAP` / `.seal-wrap` | operator disk only | 32-byte wrap, PBKDF2-SHA256 |
| L1 system vault | Supabase `vault.secrets` + `operator_key_vault` | `supabase-glaciereq` service role | `supabase_vault` / pgcrypto at rest |
| L2 family winner | `operator_key_canonical_v1` | service role | first populated alias in precedence order |
| L3 runtime | process env / gitignored `.env.runtime` | local runner | name only in logs |

## Precedence (strongest usable connector key)

Exact canonical name first. Then the least-weird alias that actually has a value.

- GitHub: `GITHUB_TOKEN` → primary → master → classic PAT
- Vercel: `VERCEL_TOKEN` → `VERCEL_API_KEY`
- Buildkite: `BUILDKITE_API_TOKEN`
- xAI / OpenAI / Anthropic: `*_API_KEY` before admin/management tokens
- AWS: access key + secret as a pair
- Supabase: management PAT for the API; service role only inside that project
- Notion / Stripe / Netlify: secret/integration token, never the publishable key

Resolve in the database with `operator_resolve_key(family)`.
Do not `select key_value` into a chat transcript.

## Rules

- Never force-push.
- Never commit plaintext or wrap keys.
- Anon and authenticated cannot read the catalog view or the resolver.
- Missing names are reported as missing. That is the whole message.
