# Genius Engineer Anti-Patterns

## Physics & Modeling Failures

- **Cargo-cult simulation**: high-fidelity model run without first understanding dominant balances and dimensionless numbers.
- **Unit blindness**: numbers whose dimensions are inconsistent or never checked.
- **Scale ignorance**: design for one size that is assumed to work at 10× or 0.1×.
- **Secondary-effect obsession**: every minor phenomenon included while the rate-limiting or energy-dominant process is missed.

## Algorithmic Failures

- **Fashionable method**: popular algorithm chosen when a simpler exact or convex method exists.
- **Complexity denial**: “it works” claimed while asymptotic or practical resource use is unacceptable.
- **Stability neglect**: numerically unstable procedure blamed on “floating point.”
- **Representation mismatch**: data forced into a structure that destroys sparsity, locality, or physical meaning.

## Synthesis Failures

- **Disconnected layers**: algorithm optimized while ignoring its physical running cost, or hardware designed while treating software as free.
- **Unrecoverable insight**: solution whose key idea cannot be extracted or re-derived by another competent engineer.
- **Trade-off hiding**: single-point design presented without stating what was sacrificed and why.

## Process Failures

- **Skipping the frame**: detailed design or coding begun before objective and constraints are stated in physical or information terms.
- **Verification theater**: only the happy path or the cases the model was tuned on are checked.
- **Premature code**: substantial implementation written before the governing model and algorithm choice are solid.

## Remedies

- Enforce the Sequential Deep Work Protocol.
- Require explicit scaling and limiting-case statements.
- Prefer the simplest model that still decides the design.
- Always leave a recoverable reasoning chain.
