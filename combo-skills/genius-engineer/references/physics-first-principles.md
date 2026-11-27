# Physics First Principles for Engineers

## Core Conservation Laws

Check which of these dominate:

- Mass / particle number
- Energy (internal, kinetic, potential, chemical)
- Momentum / angular momentum
- Charge
- Information / entropy (information-processing systems)

If a design appears to violate or ignore one, stop and re-examine.

## Dimensional Analysis & Scaling

1. List relevant quantities and their dimensions.
2. Form dimensionless groups (Buckingham Pi).
3. Express the quantity of interest as a function of those groups.
4. Examine limiting behavior as each group → 0 or → ∞.
5. Estimate magnitudes from scaling before detailed calculation.

High-leverage questions:
- How do power, force, time, or cost scale with size L?
- Which dimensionless number sets the regime (Re, Pe, Fo, Kn, Mach, …)?

## Limiting Cases Checklist

- Quasi-static vs inertial
- Continuum vs discrete / molecular
- Equilibrium vs far-from-equilibrium
- Diffusive vs advective transport
- Linear response vs strongly nonlinear
- Deterministic vs fluctuation-dominated

## Energy & Power Thinking

- Every real process has an energy cost and a power limit.
- Trace where energy comes from and where it goes (heat, work, radiation, storage).
- Minimize irreversible entropy generation when efficiency matters.
- For computational systems, treat energy per operation and power density as first-class variables.

## Common Traps

- Ignoring surface-to-volume scaling (cooling/heating rates, diffusion times ~ L²).
- Treating material properties as constant across temperature, rate, or size changes.
- Citing “efficiency” without a stated reference process.
- Designing for the average while the physics is dominated by extremes or tails.
