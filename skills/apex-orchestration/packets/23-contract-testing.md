# Packet 23 — CONTRACT-TESTING

**Owner:** apex-orchestration v1.3.0
**Maturity:** 9 / "Producer/consumer signature locks; breaks the build on breaking changes"
**Layer:** Skill
**Scope:** When a code subtask produces a public API, the VERIFY lane extracts the contract (function signatures, type signatures, return types, exceptions) and writes it to a contract registry. Future dispatches that would consume this API check the contract first; mismatches BLOCK the dispatch.

---

## Invariant (L5)

A contract test is valid iff:
1. Every public function in the test_subject has a contract entry: `{name, params: [{name, type}], returns: type, raises: [str], side_effects: []}`.
2. A consumer task that targets a producer's API gets a BLOCK with F-VER-04 if the consumer's expected signature is not in the producer's contract.
3. A producer change to a public signature is a **breaking change** if any consumer exists; the change is BLOCKED unless explicitly approved.
4. The contract registry is append-only; supersedes is set when a contract evolves.

## The Contract Schema

```json
{
  "contract_id": "contract_<ulid>",
  "module": "src/lib/auth.ts",
  "version": "1.2.0",
  "ts": "2026-09-04T...",
  "supersedes": "contract_<prev_ulid>",
  "functions": [
    {
      "name": "authenticate",
      "params": [{"name": "user", "type": "User"}, {"name": "token", "type": "str"}],
      "returns": "Result<Session, AuthError>",
      "raises": ["AuthError", "NetworkError"],
      "side_effects": ["writes:db:sessions"]
    }
  ]
}
```

## The Consumer Check

Before dispatching a consumer task, the orchestrator extracts the consumer's expected signature from its prompt (e.g. `await authenticate(user, token)`) and looks it up in the producer's contract. If not found, BLOCK with F-VER-04.

## Gates

- **G1 — Coverage gate.** Every public function in a test_subject MUST have a contract entry. Uncovered → F-VER-04.
- **G2 — Breaking-change gate.** Removing or renaming a public function is a breaking change. If consumers exist (from receipt history), BLOCK.
- **G3 — Schema-version gate.** Contracts are versioned. A consumer specifying `version: ^1.0.0` rejects `2.0.0`.
- **G4 — Append-only gate.** Contract entries are append-only; corrections create new versions with `supersedes`.
- **G5 — Audit gate.** Every contract check is logged. F-VER-04 events trigger a notification (if `notifications: true`).

## Anti-Patterns

- Generating contracts from function bodies (fragile; type erasure risk).
- Locking contracts to absolute versions (no evolution possible).
- Skipping the consumer check for trusted producers.
- Treating undocumented functions as "internal" without explicit opt-in.

## L2 Evidence

- Coverage test: every public function in `test_subject` has a contract entry.
- Consumer check test: consumer expects `authenticate(user, token)` → producer contract has it → pass. Rename in producer → fail.
- Breaking-change test: producer removes a public function with consumers → BLOCK.
- Schema-version test: consumer with `^1.0.0` accepts `1.9.0` but rejects `2.0.0`.
- Append-only test: attempt to modify a contract → fails; new version required.

## Versioning

- **Major bump:** contract schema change.
- **Minor bump:** new field added.
- **Patch:** bug fix in check logic.

Current version: **1.0.0** (paired with apex-orchestration v1.3.0).
