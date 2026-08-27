---
name: aerospace-trajectory-core
description: SpaceX orbital dynamics, Keplerian propagation, Lambert transfer boundary value solvers, and thermodynamic cryogenic boil-off equations.
---

# Aerospace Trajectory Core

## Purpose

Execute mathematical orbital propagation, delta-v transfer budget calculations, Lambert targeting, and cryogenic boil-off simulations across aerospace flight software and satellite constellations.

## Procedure

1. Ingest initial Keplerian orbital elements $(a, e, i, \Omega, \omega, \nu)$ or Cartesian state vectors $(\mathbf{r}, \mathbf{v})$.
2. Solve Lambert's boundary-value problem for targeted orbital transfers between state vectors.
3. Propagate orbital state vectors using high-order numerical integration (`orbital_integrator.jl`).
4. Calculate cryogenic LOX/CH4 boil-off rates and pressure curves based on tank thermal models (`boiloff.py`).
5. Evaluate orbital conjunction probabilities with Starlink constellation nodes.

## Output contract

Produce `aerospace-trajectory-telemetry.json` with computed delta-v budgets, transfer trajectories, boil-off estimates, and collision avoidance vectors.

## Local validation

The procedure passes only when orbital state vectors conserve mechanical energy and angular momentum within numerical tolerance thresholds, and unit tests pass 100% green.

## Non-goals

Do not issue live physical flight commands without mission authority approval. Do not bypass aerodynamic thermal constraints.
