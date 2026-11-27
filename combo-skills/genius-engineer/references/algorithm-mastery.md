# Algorithmic Mastery for Genius Engineering

## Matching Structure to Method

| Problem Structure           | Preferred Approaches                                      |
|-----------------------------|-----------------------------------------------------------|
| Graphs / networks           | BFS/DFS, Dijkstra, A*, flow, matching, spectral           |
| Geometry / continuous space | Computational geometry, gradient methods, sampling        |
| Combinatorial search        | Branch-and-bound, dynamic programming, ILP, local search  |
| Simulation / dynamics       | Explicit/implicit integrators, Monte Carlo, event-driven  |
| Approximation / learning    | Regularized optimization, sparse methods, careful ML      |
| Streaming / online          | Reservoir sampling, sketches, competitive analysis        |

## Complexity Discipline

- Express complexity in terms of true parameters (n, m, d, κ, ε, physical size L, …).
- Distinguish worst-case, average-case, and smoothed complexity when relevant.
- Communication and data movement often dominate arithmetic cost on real hardware.
- For numerical algorithms, report stability properties and condition-number effects.

## Numerical & Approximate Methods

- Prefer methods whose error can be bounded relative to required physical tolerance.
- Guard against cancellation, overflow/underflow, and round-off accumulation.
- Use adaptive methods (step size, mesh, precision) when multiple scales are present.
- When full simulation is too expensive, apply model reduction or surrogates and quantify the error.

## Hardware-Aware Design

- Cache locality and blocking.
- Vectorization and parallelism (data-parallel vs task-parallel).
- Memory bandwidth vs compute intensity (roofline).
- Energy and power as first-class costs for large or embedded systems.

## Invention Heuristics

- Reduce to a known problem that already has a strong algorithm.
- Exploit sparsity, low rank, monotonicity, convexity, or matroid structure.
- Choose a representation that makes the expensive operation cheap.
- Treat the algorithm’s own resource consumption as a controllable physical variable.
