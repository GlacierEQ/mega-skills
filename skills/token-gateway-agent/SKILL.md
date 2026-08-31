---
name: token-gateway-agent
description: "Autonomous skill for token gateway agent within the APEX Estate."
---

# Token Gateway Agent v2.0

## Purpose
Manages the Universal Token Gateway service with full Supabase JWT signature verification and production-grade security.

## Capabilities
### Core Functions
1. **JWT Signature Verification**
   - Fetches JWKS (JSON Web Key Set) from Supabase
   - Validates RS256 signatures automatically
   - Handles token expiration (exp, nbf)
   - Enforces issuer (aud) validation
   - Token caching (5min TTL) for performance

2. **Rate Limiting & Throttling**
   - Per-subject rate limiter with sliding window
   - Configurable limits (default: 30 req/min)
   - Exponential backoff on abuse detection
   - Rate limit headers in responses

3. **Secure Vault Access**
   - Proxy to Supabase vault (operator_key_vault table)
   - Key name sanitization (prevent injection)
   - Audited access logging (immutable)
   - Fallback to environment variables on failure

4. **Health Monitoring**
   - Continuous health checks
   - JWKS freshness monitoring (alert if >10min stale)
   - Vault connectivity status
   - Metrics export (Prometheus format)

5. **Agent Onboarding**
   - Automated agent registration
   - Scope-based access control
   - Temporary token generation
   - Session management

## Runtime Requirements
- SUPABASE_URL (e.g., https://kjebemdgvjvuutzvhbtp.supabase.co)
- SERVICE_ROLE_KEY (for vault queries)
- Optional: JWKS_CACHE_TTL_SECONDS (default: 300)
- Optional: RATE_LIMIT_PER_MIN (default: 30)

## Workflow
```
┌─────────────────┐      ┌─────────────────────┐
│   Agent JWT     │──►──► │  Gateway /health   │
│ (Supabase)      │      │  Gateway /api/vault│
└─────────────────┘      └─────┬─────┬─────────┘
                              │     │
                              │     │ validate signature
                              ▼     ▼
                        ┌─────────────┐
                        │  Vault DB   │
                        │  (operator_key_vault) │
                        └─────────────┘
                              │
                              ▼
                        ┌─────────────┐
                        │ Audit Log   │
                        │ (immutable) │
                        └─────────────┘
```

## Version History
- v1.0: Minimal JWT verification (basic decode only)
- v2.0: Full JWKS signature verification + production hardening

## Integration Points
- Supabase: JWKS endpoint at .well-known/jwks.json
- Vault: operator_key_vault table queries
- Audit: Supabase immutable storage
- Monitoring: OpenTelemetry metrics
