# Synthesis Patterns — Fusing Physics, Chemistry & Algorithms

## Pattern 1 — Physics-to-Optimization

1. Write the governing equations or conservation statements.
2. Identify design variables and the true objective (energy, time, cost, risk, information).
3. Convert constraints into feasible sets an optimizer or search can respect.
4. Choose an algorithm whose assumptions match the structure (convex, combinatorial, black-box, …).

## Pattern 2 — Scaling-First Design Space Pruning

- Use dimensional analysis and asymptotic regimes to eliminate large regions of the design space before numerical search or detailed simulation.
- Explore only the remaining low-dimensional manifold of promising candidates.

## Pattern 3 — Minimal Viable Physical Model

- Build the simplest model that still predicts dominant behavior and key trade-offs.
- Calibrate its few parameters from limited data or known limits.
- Use the model to guide both the algorithm and any experimental or simulation campaign.

## Pattern 4 — Resource Profile as Design Variable

- Treat time, energy, memory, bandwidth, or material usage of the algorithm/process as quantities that obey physical constraints.
- Optimize the joint system (algorithm + physical embodiment) rather than the algorithm in isolation.

## Pattern 5 — Feasibility Regions from Chemistry/Materials

- Translate thermodynamic, kinetic, or materials limits into hard or soft constraints on the search.
- Examples: temperature window, concentration bounds, stress limits, cycle-life requirements become bounds or penalties.

## Pattern 6 — Insight Extraction Loop

After any computational result:
- Identify the dominant balance or mechanism.
- Re-derive a simple scaling or closed-form approximation that captures the same behavior.
- Prefer the insight + simple model over an opaque high-fidelity number when deciding or communicating.
