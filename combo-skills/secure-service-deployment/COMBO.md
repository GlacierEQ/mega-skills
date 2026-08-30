---
id: secure-service-deployment
display_name: Secure Service Deployment
schema: ../../schemas/combo-skill.schema.json
version: 1.0.0
status: active
---

# Secure Service Deployment

## Purpose and selection

Containerizing and deploying microservices, MCP servers, or background APIs.
Do **not** use when local interactive script execution without containerization or networking.

## Incremental value

Unified secure deployment pipeline: integrates API typing, multi-stage containerization, OWASP security scanning, and MCP registration into a single certified release manifest.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `api-integration` | Skill | Yes | Specify typed API interfaces, retry backoff, and webhook listeners. | Service functional spec, Protocol schemas | API_INTERFACE_SPEC.json, Client SDK stubs | OpenAPI / MCP protocol schemas are fully typed and validated. |
| 2 | `docker-devops` | Skill | Yes | Author multi-stage Dockerfiles, compose environments, and registry pipelines. | API_INTERFACE_SPEC.json, Service source code | Dockerfile, docker-compose.yml, Container image digest | Container builds successfully with multi-stage layer caching. |
| 3 | `security-review` | Skill | Yes | Execute OWASP security review, credential sanitization, and vulnerability scanning. | Dockerfile, docker-compose.yml, Environment secrets | SECURITY_AUDIT_REPORT.md, Air-gap credential manifest | Zero baked-in secrets, zero high/critical CVEs in base images. |
| 4 | `mcp-master-server` | Skill | Yes | Register and coordinate MCP tool endpoints with health watchdogs. | API_INTERFACE_SPEC.json, Container runtime configuration | MCP_REGISTRATION_MANIFEST.json, Healthcheck watchdog | MCP endpoints discoverable and responsive to protocol pings. |
| 5 | `quality-gate` | Skill | Yes | Validate container health, runtime latency, and cryptographic provenance. | SECURITY_AUDIT_REPORT.md, MCP_REGISTRATION_MANIFEST.json | SERVICE_DEPLOYMENT_MANIFEST.md, Production signoff | End-to-end container healthcheck passes with bounded latency. |

## Ordered execution

1. **Step 1 — `api-integration`**: Consumes Service functional spec, Protocol schemas, produces API_INTERFACE_SPEC.json, Client SDK stubs, and satisfies: OpenAPI / MCP protocol schemas are fully typed and validated.
2. **Step 2 — `docker-devops`**: Consumes API_INTERFACE_SPEC.json, Service source code, produces Dockerfile, docker-compose.yml, Container image digest, and satisfies: Container builds successfully with multi-stage layer caching.
3. **Step 3 — `security-review`**: Consumes Dockerfile, docker-compose.yml, Environment secrets, produces SECURITY_AUDIT_REPORT.md, Air-gap credential manifest, and satisfies: Zero baked-in secrets, zero high/critical CVEs in base images.
4. **Step 4 — `mcp-master-server`**: Consumes API_INTERFACE_SPEC.json, Container runtime configuration, produces MCP_REGISTRATION_MANIFEST.json, Healthcheck watchdog, and satisfies: MCP endpoints discoverable and responsive to protocol pings.
5. **Step 5 — `quality-gate`**: Consumes SECURITY_AUDIT_REPORT.md, MCP_REGISTRATION_MANIFEST.json, produces SERVICE_DEPLOYMENT_MANIFEST.md, Production signoff, and satisfies: End-to-end container healthcheck passes with bounded latency.

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner |
|---|---|---|---|---|
| `api-integration` | `docker-devops` | API_INTERFACE_SPEC.json | Dockerfile, docker-compose.yml | api-engineer |
| `docker-devops` | `security-review` | Dockerfile, docker-compose.yml | SECURITY_AUDIT_REPORT.md | devops-engineer |
| `security-review` | `mcp-master-server` | SECURITY_AUDIT_REPORT.md | MCP_REGISTRATION_MANIFEST.json | secops-auditor |
| `mcp-master-server` | `quality-gate` | MCP_REGISTRATION_MANIFEST.json | SERVICE_DEPLOYMENT_MANIFEST.md | mcp-architect |

## Evidence, risks, and state

The Combo records evidence in its evidence register:
- Cryptographic SHA-256 container image digest.
- Automated vulnerability scan results with zero high/critical issues.
- Live healthcheck ping verification receipt.

Risk boundaries:
- Zero secrets or sensitive API keys committed or baked into images.
- Strict container isolation with non-root runtime users.

## Quality gates

- Container boots within 5 seconds and passes healthcheck.
- Security review confirms 100% credential air-gapping.

## Compound output

**Artifact:** `SERVICE_DEPLOYMENT_MANIFEST.md`

**Ready for Mega Skill integration when:**

1. Container healthcheck passes with HTTP 200 / MCP ready status.
2. Security review certifies zero credential leaks.
